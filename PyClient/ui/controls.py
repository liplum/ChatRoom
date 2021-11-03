from abc import ABC, abstractmethod
from datetime import datetime
from io import StringIO
from typing import Union, List, Optional

import chars
import keys
import utils
from core.chats import roomid, userid
from net.networks import server_token
from ui import outputs as output
from ui.k import kbinding
from ui.outputs import CmdBkColor, CmdFgColor
from ui.outputs import buffer
from ui.states import state, smachine
from ui.tbox import textbox
from utils import clear_screen


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

        def set_client(state: state) -> None:
            state.client = self.client
            state.textbox = self.textbox

        def gen_state(statetype: type) -> state:
            if issubclass(statetype, inputable_state):
                s = statetype()
                set_client(s)
                return s
            else:
                return statetype()

        self.sm = smachine(state_pre=set_client, stype_pre=gen_state)
        self.sm.enter(cmd_mode)
        self.textbox.on_append.add(lambda b, p, c: client.make_dirty())
        self.textbox.on_delete.add(lambda b, p, c: client.make_dirty())
        self.textbox.on_cursor_move.add(lambda b, f, c: client.make_dirty())
        self.textbox.on_list_replace.add(lambda b, f, c: client.make_dirty())

    def draw_on(self, buf: buffer):
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
        self.win = win
        self.view_history = []
        self.max_view_history = 5
        self.chat_tabs: List[tab] = []

    def add(self, tab: "tab"):
        self.tabs.append(tab)
        if isinstance(tab, chat_tab):
            self.chat_tabs.append(tab)
        if self.cur is None:
            self.cur = tab

    def remove(self, item: Union[int, "tab"]):
        if isinstance(item, int):
            need_removed = self.tabs[item]
            del self.tabs[item]
            if isinstance(tab, chat_tab):
                self.chat_tabs.remove(need_removed)
        elif isinstance(item, tab):
            self.tabs.remove(item)
            if isinstance(tab, chat_tab):
                self.chat_tabs.remove(tab)

    def switch(self):
        if len(self.view_history) >= 2:
            self.goto(self.view_history[-1])

    def goto(self, number: int):
        if 0 <= number < len(self.tabs):
            self.cur = self.tabs[number]
            self.add_view_history(number)

    def add_view_history(self, number: int):
        self.view_history.append(number)
        if len(self.view_history) > self.max_view_history:
            self.view_history = self.view_history[-self.max_view_history:]

    def draw_on(self, buf: buffer):
        c = 0
        tab_count = len(self.tabs)
        for t in self.tabs:
            c += 1
            if t is self.cur:
                buf.addtext(f" {t.title} ", bkcolor=CmdBkColor.Yellow, end='')
            else:
                buf.addtext(f" {t.title} ", bkcolor=CmdBkColor.Green, end='')
            if c < tab_count:
                buf.addtext("|", bkcolor=CmdBkColor.White)
        buf.addtext("")


class window:
    def __init__(self, client: "client", displayer: output.i_display):
        self.client = client
        self.max_display_line = 10
        self.displayer: output.i_display = displayer
        self.tablist = tablist(self)
        self.screen_buffer: Optional[buffer] = None
        self.newtab(chat_tab)

    def newtab(self, tabtype: type):
        self.tablist.add(tabtype(self.client, self.tablist))

    def prepare(self):
        self.screen_buffer = self.displayer.gen_buffer()

    def update_screen(self):
        clear_screen()
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

    def receive_room_text(self, user_id: userid, room_id: roomid, text: str, time: datetime):
        add_text(f"{time.strftime('%Y%m%d-%H:%M:%S')}\n\t{user_id}:{text}")
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


class inputable_state(state):
    textbox: textbox
    client: "client"

    def __init__(self):
        super().__init__()


class cmd_mode(inputable_state):
    def __init__(self):
        super().__init__()
        self.islongcmd = False
        self.longcmd = ""

    def on_en(self):
        self.client.make_dirty()
        self.textbox.clear()

    tip: str = utils.fillto("Command mode:", " ", 40)

    def draw_on(self, buf: buffer):
        buf.addtext(text=cmd_mode.tip, fgcolor=CmdFgColor.Black,
                    bkcolor=CmdBkColor.Blue,
                    end='\n')

    def enter_long_cmd_mode(self):
        self.islongcmd = True

    def quit_long_cmd_mode(self):
        self.islongcmd = False

    def on_input(self, char: chars.char):
        c = self.client
        tb = self.textbox
        if c.key_quit_text_mode == char:
            self.quit_long_cmd_mode()
            tb.clear()

        if tb.input_count <= 0:
            self.quit_long_cmd_mode()
        if self.islongcmd:
            if keys.k_enter == char:
                input_list = tb.input_list
                args = utils.compose(input_list, connector='')
                tb.clear()
                # TODO:Complete This
                self.quit_long_cmd_mode()
            else:
                tb.append(char)
        else:
            if c.key_enter_text == char:
                self.sm.enter(text_mode)
                return True
            elif chars.c_colon == char:
                self.enter_long_cmd_mode()
                tb.append(chars.c_colon)
            elif chars.c_q == char:
                c.running = False


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
        self.client.make_dirty()
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
