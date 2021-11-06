from abc import ABC, abstractmethod
from io import StringIO
from typing import Union, List, Optional

import chars
import keys
from cmd import cmdmanager
from core import utils
from core.chats import roomid, i_msgmager
from core.events import event
from net.networks import server_token
from ui import outputs as output
from ui.k import kbinding
from ui.outputs import CmdBkColor, CmdFgColor
from ui.outputs import buffer
from ui.states import state, smachine
from ui.tbox import textbox


class xtextbox(textbox):
    def __init__(self, cursor_icon: str = '^'):
        super().__init__(cursor_icon)
        kbs = kbinding()
        self.kbs = kbs
        kbs.bind(keys.k_backspace, lambda c: self.delete())
        kbs.bind(keys.k_delete, lambda c: self.delete(left=False))
        kbs.bind(keys.k_left, lambda c: self.left())
        kbs.bind(keys.k_right, lambda c: self.right())
        kbs.bind(keys.k_home, lambda c: self.home())
        kbs.bind(keys.k_end, lambda c: self.end())
        spapp = super().append
        kbs.on_any = lambda c: spapp(chars.to_str(c)) if c.is_printable() else None

    def append(self, ch: Union[str, chars.char]):
        if isinstance(ch, str):
            super().append(ch)
        elif isinstance(ch, chars.char):
            consumed = self.kbs.trigger(ch)
            if not consumed:
                super().append(to_str(ch))


class tab(ABC):

    def __init__(self, client: "client", tablist: "tablist"):
        self.tablist = tablist
        self.client = client

    def on_input(self, char):
        pass

    def draw_on(self, buf: buffer):
        pass

    def deserialize_config(self, config):
        pass

    def serialize_config(self, config):
        pass

    @property
    @abstractmethod
    def title(self) -> str:
        pass


class chat_tab(tab):

    def __init__(self, client: "client", tablist: "tablist"):
        super().__init__(client, tablist)
        self.textbox = xtextbox()
        self.history: List[str] = []
        self.max_display_line = 10
        self.fill_until_max = True
        self.msg_manager: i_msgmager = self.client.msg_manager

        def set_client(state: state) -> None:
            state.client = self.client
            state.textbox = self.textbox
            state.tablist = self.tablist

        def gen_state(statetype: type) -> state:
            if issubclass(statetype, inputable_state):
                s = statetype()
                set_client(s)
                return s
            else:
                return statetype()

        self.sm = smachine(state_pre=set_client, stype_pre=gen_state)
        self.sm.enter(cmd_mode)
        self.textbox.on_append.add(lambda b, p, c: client.mark_dirty())
        self.textbox.on_delete.add(lambda b, p, c: client.mark_dirty())
        self.textbox.on_cursor_move.add(lambda b, f, c: client.mark_dirty())
        self.textbox.on_list_replace.add(lambda b, f, c: client.mark_dirty())

    def draw_on(self, buf: buffer):
        # TODO:Change the room id
        li = self.msg_manager.load_until_today(roomid(12345), self.max_display_line)
        self.history = []
        for time, uid, text in li:
            self.history.append(f"{time.strftime('%Y%m%d-%H:%M:%S')}\n\t{uid}:{text}")

        buf.addtext(self.distext)
        self.sm.draw_on(buf)
        buf.addtext(self.textbox.distext)

    @property
    def distext(self) -> str:
        if len(self.history) < self.max_display_line:
            displayed = self.history
            have_rest = True
        else:
            displayed = self.history[-self.max_display_line:]
            have_rest = False

        if have_rest and self.fill_until_max:
            with StringIO() as s:
                s.write(utils.compose(displayed, connector="\n"))
                displayed_len = len(displayed)
                s.write(utils.fill("", "\n", self.max_display_line - displayed_len))
                return s.getvalue()
        else:
            return utils.compose(displayed, connector="\n")

    def on_input(self, char):
        self.sm.on_input(char)

    @property
    def title(self) -> str:
        return "chat tab"


class setting_tab(tab):
    pass


class main_menu_tab(tab):
    pass


class tablist:
    def __init__(self, win: "window"):
        self.tabs: List[tab] = []
        self.cur: Optional[tab] = None
        self.cur_index = 0
        self.win = win
        self.view_history = []
        self.max_view_history = 5
        self.chat_tabs: List[tab] = []
        self._on_curtab_changed = event()
        self._on_tablist_changed = event()

    @property
    def on_curtab_changed(self) -> event:
        return self._on_curtab_changed

    @property
    def on_tablist_changed(self) -> event:
        return self._on_tablist_changed

    def __len__(self) -> int:
        return len(self.tabs)

    def add(self, tab: "tab"):
        self.tabs.append(tab)
        if isinstance(tab, chat_tab):
            self.chat_tabs.append(tab)
            self.on_tablist_changed(self, True, tab)
        if self.cur is None:
            self.cur = tab
            self.cur_index = self.tabs.index(self.cur)
            self.on_curtab_changed(self, tab)

    def remove(self, item: Union[int, "tab"]):
        if isinstance(item, int):
            if 0 <= item < len(self.tabs):
                removed = self.tabs[item]
                del self.tabs[item]
                self.on_tablist_changed(self, False, removed)
            if isinstance(removed, chat_tab):
                self.chat_tabs.remove(need_removed)
        elif isinstance(item, tab):
            self.tabs.remove(item)
            self.on_tablist_changed(self, False, item)
            if isinstance(tab, chat_tab):
                self.chat_tabs.remove(tab)

    def switch(self):
        if len(self.view_history) >= 2:
            self.goto(self.view_history[-1])

    def goto(self, number: int):
        if self.cur_index == number:
            return
        if 0 <= number < len(self.tabs):
            self.cur = self.tabs[number]
            self.add_view_history(number)
            self.cur_index = self.tabs.index(self.cur)
            self.on_curtab_changed(self, number, self.cur)

    def next(self):
        self.goto(self.cur_index + 1)

    def back(self):
        self.goto(self.cur_index - 1)

    def add_view_history(self, number: int):
        self.view_history.append(number)
        if len(self.view_history) > self.max_view_history:
            self.view_history = self.view_history[-self.max_view_history:]

    def draw_on(self, buf: buffer):
        c = 0
        tab_count = len(self.tabs)
        cur = self.cur
        with StringIO() as separator:
            for i, t in enumerate(self.tabs):
                c += 1
                bk = CmdBkColor.Yellow if t is cur else CmdBkColor.Green
                fg = CmdFgColor.Black if t is cur else CmdFgColor.Violet
                title = t.title
                displayed_title = f" {title} "
                buf.addtext(displayed_title, fgcolor=fg, bkcolor=bk, end='')
                repeated = " " if t is cur else "─"
                second_line = repeated * len(displayed_title)
                separator.write(second_line)
                if c < tab_count:
                    buf.addtext("│", end='')
                    if t is cur:
                        separator.write("└")
                    elif i + 1 < tab_count and self.tabs[i + 1] is cur:
                        separator.write("┘")
                    else:
                        separator.write("┴")
            buf.addtext()
            buf.addtext(separator.getvalue())


class window:
    def __init__(self, client: "client", displayer: output.i_display):
        self.client = client
        self.max_display_line = 10
        self.displayer: output.i_display = displayer
        self.tablist = tablist(self)
        self.screen_buffer: Optional[buffer] = None
        self.newtab(chat_tab)
        self.tablist.on_curtab_changed.add(lambda li, n, t: self.client.mark_dirty())
        self.tablist.on_tablist_changed.add(lambda li, mode, t: self.client.mark_dirty())

    def newtab(self, tabtype: type):
        self.tablist.add(tabtype(self.client, self.tablist))

    def prepare(self):
        self.screen_buffer = self.displayer.gen_buffer()

    def update_screen(self):
        utils.clear_screen()
        self.prepare()
        self.tablist.draw_on(self.screen_buffer)
        curtab = self.tablist.cur
        if curtab:
            curtab.draw_on(self.screen_buffer)

        self.displayer.render(self.screen_buffer)

    def on_input(self, char):
        curtab = self.tablist.cur
        if curtab:
            curtab.on_input(char)
        """
        if len(self.history) < self.max_display_line:
            displayed = self.history
            have_rest = True
        else:
            displayed = self.history[-self.max_display_line:]
            have_rest = False
        for d in displayed:
            self.displayer.display_text(d, end="\n")
        if have_rest and self.fill_until_max:
            displayed_len = len(displayed)
            for i in range(self.max_display_line - displayed_len):
                self.displayer.display_text(end="\n")
        """

    """ 
    def add_text(self, text: str):
        self.history.append(text)

    def clear_all(self):
        self.history = []
    """


class context:
    pass


class inputable_state(state):
    textbox: textbox
    client: "client"
    tablist: tablist

    def __init__(self):
        super().__init__()


class cmd_mode(inputable_state):
    def __init__(self):
        super().__init__()
        self.long_mode = False
        self.longcmd = ""
        self.autofilling = False
        self.autofilling_it = None
        self.autofilling_cur = None
        self.autofilling_all = None

    def on_en(self):
        self.client.mark_dirty()
        self.textbox.clear()
        self.cmd_manager: cmdmanager = self.client.cmd_manger

    tip: str = utils.fillto("Command mode:", " ", 40)

    def draw_on(self, buf: buffer):
        buf.addtext(text=cmd_mode.tip, fgcolor=CmdFgColor.Black,
                    bkcolor=CmdBkColor.Blue,
                    end='\n')

    def enter_long_mode(self):
        self.long_mode = True

    def quit_long_mode(self):
        self.long_mode = False
        self.textbox.clear()

    def on_input(self, char: chars.char):
        c = self.client
        tb = self.textbox
        if c.key_quit_text_mode == char:
            self.quit_long_mode()

        if tb.input_count <= 0:
            self.quit_long_mode()
        if self.long_mode:
            if keys.k_enter == char:
                input_list = tb.input_list
                full_args = utils.compose(input_list, connector='')
                args = utils.split_strip(full_args, by=' ')
                cmd_name = args[0][1:]
                contxt = context()
                contxt.client = self.client
                contxt.tablist = self.tablist
                self.cmd_manager.execute(contxt, cmd_name, args[1:])
                tb.clear()
                # TODO:Complete This
                self.quit_long_mode()
            elif chars.c_table == char:
                if self.autofilling:
                    try:
                        cur_len = len(self.autofilling_cur)
                        tb.rmtext(cur_len)

                    except StopIteration:
                        self.autofilling_it = iter(self.autofilling_all)
                else:
                    self.autofilling = True
                    cmd_manager: cmdmanager = c.cmd_manager
                    inputs = tb.inputs[1:]
                    self.autofilling_all = cmd_manager.prompts(inputs)
                    if len(all_prompts) == 0:
                        self.autofilling = False
                    else:
                        self.autofilling_it = iter(autofilling_all)
                        self.autofilling_cur = next(self.autofilling_it)
                        tb.addtext(self.autofilling_cur)
            else:
                tb.append(char)
                if self.autofilling:
                    self.autofilling_all = cmd_manager.prompts(inputs)
                    if len(all_prompts) == 0:
                        self.autofilling = False
                    else:
                        self.autofilling_it = iter(autofilling_all)
                        self.autofilling_cur = next(self.autofilling_it)
                        tb.addtext(self.autofilling_cur)
                else:
                    pass
        else:  # single mode
            if c.key_enter_text == char:
                self.sm.enter(text_mode)
                return True
            elif chars.c_colon == char:
                self.enter_long_mode()
                tb.append(chars.c_colon)
            elif chars.c_q == char:
                c.running = False
            elif chars.c_a == char:
                self.tablist.back()
            elif chars.c_d == char:
                self.tablist.next()
            elif chars.c_n == char:
                self.tablist.add(chat_tab(self.client, self.tablist))


class text_mode(inputable_state):

    def __init__(self):
        super().__init__()
        kbs = kbinding()
        self.kbs = kbs

        def send_text():
            inputs = self.textbox.inputs
            self.client.send_text(roomid(12345), inputs, server_token("127.0.0.1", 5000))
            self.textbox.clear()

        kbs.bind(keys.k_enter, lambda c: send_text())
        kbs.on_any = lambda c: self.textbox.append(c)

    def on_en(self):
        self.client.mark_dirty()
        self.textbox.clear()

    tip: str = utils.fillto("Text mode:", " ", 40)

    def draw_on(self, buf: buffer):
        buf.addtext(text=text_mode.tip, fgcolor=CmdFgColor.Black,
                    bkcolor=CmdBkColor.Blue,
                    end='\n')

    def on_input(self, char: chars.char):
        c = self.client
        if c.key_quit_text_mode == char:
            self.sm.enter(cmd_mode)
        elif True:
            self.kbs.trigger(char)
