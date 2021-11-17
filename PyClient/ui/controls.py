from abc import ABC, abstractmethod
from io import StringIO
from typing import Union, List, Optional

import GLOBAL
import chars
import i18n
import keys
import ui.states
import utils
from cmd import WrongUsageError, CmdError, CmdNotFound, analyze_cmd_args, compose_full_cmd, is_quoted
from cmd import cmdmanager
from core.chats import i_msgmager
from core.shared import server_token, roomid
from events import event
from ui import outputs as output
from ui.k import kbinding
from ui.outputs import CmdBkColor, CmdFgColor
from ui.outputs import buffer
from ui.states import ui_state, ui_smachine
from ui.tbox import textbox
import sys

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

    def add_string(self, string: str):
        pass

    def on_added(self):
        pass

    def on_removed(self):
        pass


class chat_tab(tab):

    def __init__(self, client: "client", tablist: "tablist"):
        super().__init__(client, tablist)
        self.textbox = xtextbox()
        self.history: List[str] = []
        self.max_display_line = 10
        self.fill_until_max = True
        self.msg_manager: i_msgmager = self.client.msg_manager
        self.network: "i_network" = self.client.network
        self.logger: "i_logger" = self.client.logger
        self.first_loaded = False

        self._connected: Optional[server_token] = None
        self._joined: Optional[roomid] = None

        def set_client(state: ui_state) -> None:
            state.client = self.client
            state.textbox = self.textbox
            state.tablist = self.tablist
            state.tab = self

        def gen_state(statetype: type) -> ui_state:
            if issubclass(statetype, ui_state):
                s = statetype()
                set_client(s)
                return s
            else:
                return statetype()

        self.sm = ui_smachine(state_pre=set_client, stype_pre=gen_state, allow_repeated_entry=False)
        self.sm.enter(cmd_mode)
        self.textbox.on_append.add(lambda b, p, c: client.mark_dirty())
        self.textbox.on_delete.add(lambda b, p, c: client.mark_dirty())
        self.textbox.on_cursor_move.add(lambda b, f, c: client.mark_dirty())
        self.textbox.on_list_replace.add(lambda b, f, c: client.mark_dirty())

    def send_text(self):
        if self.connected:
            inputs = self.textbox.inputs
            self.client.send_text(roomid(12345), inputs, self.connected)
        else:
            self.logger.error(f"[Tab][{self}]Haven't connected a server yet.")
        self.textbox.clear()

    @property
    def joined(self) -> Optional[roomid]:
        return self._joined

    @joined.setter
    def joined(self, value):
        self._joined = value

    @property
    def connected(self) -> Optional[server_token]:
        return self._connected

    def connect(self, server_token):
        if self.network.is_connected(server_token):
            self._connected = server_token
        else:
            self.logger.error(f"[Tab][{self}]Cannot access a unconnected/disconnected server.")

    def _add_msg(self, time, uid, text):
        self.history.append(f"{time.strftime('%Y%m%d-%H:%M:%S')}\n  {uid}:  {text}")

    def first_load(self):
        self.history = []
        if self.connected and self.joined:
            li = self.msg_manager.load_until_today(self.connected, self.joined, self.max_display_line)
            for time, uid, text in li:
                self._add_msg(time, uid, text)
        self.first_loaded = True

    def draw_on(self, buf: buffer):
        if not self.first_loaded:
            self.first_load()

        self.render_connection_info(buf)
        buf.addtext(self.distext)
        self.sm.draw_on(buf)
        buf.addtext(self.textbox.distext)

    def render_connection_info(self, buf: buffer):
        if self.connected:
            if self.joined:
                tip = i18n.trans('tabs.chat_tab.joined',
                                 ip=self.connected.ip, port=self.connected.port, room_id=self.joined.id)
            else:
                tip = i18n.trans('tabs.chat_tab.connected',
                                 ip=self.connected.ip, port=self.connected.port)
        else:
            tip = i18n.trans('tabs.chat_tab.no_connection')
        buf.addtext(text=tip, bkcolor=CmdBkColor.White, fgcolor=CmdFgColor.Black, end='\n')

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
        if self.connected and self.joined:
            return str(self.joined.id)
        return i18n.trans("tabs.chat_tab.name")

    def add_string(self, string: str):
        self.history.append(string)

    def on_added(self):
        self.msg_manager.on_received.add(self._on_received_msg)

    def _on_received_msg(self, manager, server, room_id, msg_unit):
        if server == self.connected and room_id == self.joined:
            time, uid, text = msg_unit
            self._add_msg(time, uid, text)

    def on_removed(self):
        self.msg_manager.on_received.remove(self._on_received_msg)


class setting_tab(tab):
    pass


class main_menu_tab(tab):
    pass


class tablist:
    def __init__(self, win: "window"):
        self.tabs: List[tab] = []
        self._cur: Optional[tab] = None
        self.cur_index = 0
        self.win = win
        self.view_history = []
        self.max_view_history = 5
        self.chat_tabs: List[tab] = []
        self._on_curtab_changed = event()
        self._on_tablist_changed = event()

    @property
    def on_curtab_changed(self) -> event:
        """
        Para 1:tablist object

        Para 2:index of current tab

        Para 3:current tab

        :return: event(tablist,int,tab)
        """
        return self._on_curtab_changed

    @property
    def on_tablist_changed(self) -> event:
        """
        Para 1:textbox object

        Para 2:change type: True->add ; False->remove

        Para 3:operated tab

        :return: event(textbox,bool,tab)
        """
        return self._on_tablist_changed

    def __len__(self) -> int:
        return len(self.tabs)

    @property
    def cur(self) -> Optional[tab]:
        return self._cur

    @cur.setter
    def cur(self, value: Optional[tab]):
        changed = self._cur is not value
        if changed:
            self._cur = value
            self.cur_index = self.tabs.index(self.cur)
            self.on_curtab_changed(self, self.cur_index, tab)

    def add(self, tab: "tab"):
        self.tabs.append(tab)
        if isinstance(tab, chat_tab):
            self.chat_tabs.append(tab)
            self.on_tablist_changed(self, True, tab)
        if self.cur is None:
            self.cur = tab
        tab.on_added()

    def remove(self, item: Union[int, "tab"]):
        if isinstance(item, int):
            if 0 <= item < len(self.tabs):
                removed = self.tabs[item]
                del self.tabs[item]
                self.on_tablist_changed(self, False, removed)
                removed.on_removed()
            if isinstance(removed, chat_tab):
                self.chat_tabs.remove(removed)

        elif isinstance(item, tab):
            self.tabs.remove(item)
            self.on_tablist_changed(self, False, item)
            item.on_removed()
            if isinstance(item, chat_tab):
                self.chat_tabs.remove(item)
        self.goto(self.cur_index - 1)

    def switch(self):
        if len(self.view_history) >= 2:
            self.goto(self.view_history[-1])

    def goto(self, number: int):
        if self.cur_index == number:
            return
        if 0 <= number < len(self.tabs):
            self.cur = self.tabs[number]
            self.add_view_history(number)

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
        self.displayer: output.i_display = displayer
        # self.max_display_line = 10
        self.tablist = tablist(self)
        self.screen_buffer: Optional[buffer] = None
        self.tablist.on_curtab_changed.add(lambda li, n, t: self.client.mark_dirty())
        self.tablist.on_tablist_changed.add(lambda li, mode, t: self.client.mark_dirty())

    def start(self):
        self.network: "i_network" = self.client.network
        self.gen_default_tab()

    def gen_default_tab(self):
        chat = chat_tab(self.client, self.tablist)
        self.tablist.add(chat)
        first_or_default = utils.get_at(self.network.connected_servers, 0)
        if first_or_default:
            chat.connect(first_or_default)
            chat.joined = roomid(12345)

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


class context:
    pass


def gen_cmd_error_text(cmd_name: str, args: List[str], full_cmd: str, pos: int, msg: str,
                       is_quoted: bool = False) -> str:
    argslen = len(args) + 1
    with StringIO() as s:
        s.write(full_cmd)
        s.write('\n')
        if pos == -1:
            s.write(' ')
            for _ in range(len(cmd_name)):
                s.write('^')
            for arg in args:
                for _ in range(len(arg) + 1):
                    s.write(' ')
            s.write('\n')
        elif pos >= 0:
            for _ in range(len(cmd_name) + 2):
                s.write(' ')
            for i, arg in enumerate(args):
                if i == pos:
                    if is_quoted:
                        s.write(' ')
                    for _ in range(len(arg)):
                        s.write('^')
                else:
                    for _ in range(len(arg)):
                        s.write(' ')
                if i < argslen:
                    s.write(' ')
            s.write('\n')
        s.write(msg)
        return s.getvalue()


class _cmd_state(ui.states.state):
    mode: "cmd_mode"
    sm: "_cmd_smachine"

    def on_input(self, char: chars.char):
        pass


class _cmd_smachine(ui.states.smachine):
    def on_input(self, char: chars.char):
        if self.cur is not None:
            return self.cur.on_input(char)


class cmd_mode(ui_state):
    def __init__(self):
        super().__init__()
        self.cmd_history: List[str] = []
        self.cmd_history_index = 0
        self.last_cmd_history: Optional[str] = None

        def set_cmd_mode(state: _cmd_state) -> None:
            state.mode = self

        def gen_state(statetype: type) -> _cmd_state:
            if issubclass(statetype, _cmd_state):
                s = statetype()
                set_cmd_mode(s)
                return s
            else:
                return statetype()

        self.cmd_sm = _cmd_smachine(state_pre=set_cmd_mode, stype_pre=gen_state, allow_repeated_entry=False)
        self.cmd_sm.enter(_cmd_single_mode)

    @property
    def cmd_history_index(self) -> int:
        return self._cmd_history_index

    @cmd_history_index.setter
    def cmd_history_index(self, value: int):
        if value >= 0:
            self._cmd_history_index = 0
        else:
            value = max(value, -len(self.cmd_history))
            value = min(value, -1)
            self._cmd_history_index = value

    @property
    def cur_cmd_history(self) -> Optional[str]:
        if len(self.cmd_history) == 0 or self.cmd_history_index == 0:
            return None
        else:
            return self.cmd_history[self.cmd_history_index]

    def on_en(self):
        self.client.mark_dirty()
        self.textbox.clear()
        self.cmd_manager: cmdmanager = self.client.cmd_manger

    def draw_on(self, buf: buffer):
        head_text = f"{i18n.trans('modes.command_mode.name')}:"
        if GLOBAL.DEBUG:
            head_text = f"{i18n.trans('modes.command_mode.name')}:{self.cmd_history_index} {self.cmd_sm.cur}"

        tip = utils.fillto(head_text, " ", 40)
        buf.addtext(text=tip, fgcolor=CmdFgColor.White,
                    bkcolor=CmdBkColor.Blue,
                    end='\n')

        if GLOBAL.DEBUG:
            buf.addtext(repr(self.cmd_history))

    @property
    def is_long_cmd_mode(self) -> bool:
        inputs = self.textbox.input_list
        return len(inputs) > 0 and inputs[0] == ':'

    def gen_context(self):
        contxt = context()
        contxt.client = self.client
        contxt.tablist = self.tablist
        contxt.network = self.client.network
        contxt.tab = self.tab
        contxt.cmd_manager = self.cmd_manager
        return contxt

    def _show_cmd_history(self):
        cur_his = self.cur_cmd_history
        if cur_his:
            if cur_his != self.last_cmd_history:
                # display history
                self.textbox.input_list = cur_his
                self.last_cmd_history = cur_his
                self.textbox.end()
        else:
            self.textbox.clear()

    def on_input(self, char: chars.char):
        c = self.client
        tb = self.textbox
        # press quit to clear textbox
        if c.key_quit_text_mode == char:
            self.textbox.clear()
            return

        # browser command using history
        if keys.k_up == char:
            up_or_down = -1
        elif keys.k_down == char:
            up_or_down = -1
        else:
            up_or_down = 0
            self.cmd_history_index = 0
        if up_or_down:
            saved = False
            if self.cmd_history_index == 0 and self.textbox.input_count > 0:
                # save current text
                input_list = self.textbox.input_list
                cur_content = utils.compose(input_list, connector='')
                saved = True
            self.cmd_history_index += up_or_down
            self._show_cmd_history()
            if saved:
                self.cmd_history.append(cur_content)
                self.cmd_history_index -= 1
            return
        # switch mode
        if self.is_long_cmd_mode:
            self.cmd_sm.enter(_cmd_long_mode)
        else:
            self.cmd_sm.enter(_cmd_single_mode)

        self.cmd_sm.on_input(char)


class _cmd_long_mode(_cmd_state):
    def __init__(self):
        self.autofilling = False
        self.autofilling_it = None
        self.autofilling_cur = None
        self.autofilling_all = None

    def cmd_long_mode_execute_cmd(self):
        mode = self.mode
        tb = self.mode.textbox
        input_list = tb.input_list
        full_cmd = utils.compose(input_list, connector='')
        cmd_args, quoted_indexes = analyze_cmd_args(full_cmd)
        full_cmd = compose_full_cmd(cmd_args, quoted_indexes)
        args = cmd_args[1:]
        cmd_name = cmd_args[0][1:]
        contxt = mode.gen_context()
        try:
            mode.cmd_manager.execute(contxt, cmd_name, args)
        except WrongUsageError as wu:
            with StringIO() as s:
                s.write(i18n.trans("modes.command_mode.cmd.wrong_usage"))
                s.write(':\n')
                pos = wu.position
                is_pos_quoted = is_quoted(pos + 1, quoted_indexes)
                s.write(gen_cmd_error_text(cmd_name, args, full_cmd, pos, wu.msg, is_pos_quoted))
                mode.tab.add_string(s.getvalue())
        except CmdNotFound as cnt:
            error_output = gen_cmd_error_text(
                cmd_name, args, full_cmd, -1,
                i18n.trans("modes.command_mode.cmd.cannot_find", name=cmd_name))
            mode.tab.add_string(error_output)
        except CmdError as ce:
            with StringIO() as s:
                s.write(i18n.trans("modes.command_mode.cmd.cmd_error"))
                s.write(':\n')
                s.write(gen_cmd_error_text(cmd_name, args, full_cmd, -2, ce.msg))
                mode.tab.add_string(s.getvalue())
        except Exception as any_e:
            with StringIO() as s:
                if GLOBAL.DEBUG:
                    mode.tab.add_string(f"{any_e}\n{sys.exc_info()}")
                else:
                    s.write(i18n.trans("modes.command_mode.cmd.unknown_error"))
                    s.write(':\n')
                    s.write(gen_cmd_error_text(
                        cmd_name, args, full_cmd, -2,
                        i18n.trans("modes.command_mode.cmd.not_support", name=cmd_name)))
                    mode.tab.add_string(s.getvalue())

        mode.cmd_history.append(full_cmd)
        mode.cmd_history_index = 0
        tb.clear()

    def on_input(self, char: chars.char):
        mode = self.mode
        tb = mode.textbox

        # execute command
        if keys.k_enter == char:
            self.cmd_long_mode_execute_cmd()
        # auto filling
        elif chars.c_table == char:
            # TODO:Complete Autofilling
            if mode.autofilling:  # press tab and already entered auto-filling mode
                # to next candidate
                # cur_len = len(self.autofilling_cur)
                # tb.rmtext(cur_len)
                # self.autofilling_it = iter(self.autofilling_all)
                pass
            else:  # press tab but haven't enter auto-filling mode yet
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
        else:  # not enter and not tab
            tb.append(char)  # normally,add this char into textbox
            if self.autofilling:  # if already entered auto-filling
                # update candidate list
                self.autofilling_all = cmd_manager.prompts(inputs)
                if len(all_prompts) == 0:
                    self.autofilling = False
                else:
                    self.autofilling_it = iter(autofilling_all)
                    self.autofilling_cur = next(self.autofilling_it)
                    tb.addtext(self.autofilling_cur)
            else:
                pass


class _cmd_single_mode(_cmd_state):

    def on_input(self, char: chars.char):
        mode = self.mode
        tb = mode.textbox

        if mode.client.key_enter_text == char:
            mode.sm.enter(text_mode)
            return
        elif chars.c_colon == char:
            tb.append(chars.c_colon)
        elif chars.c_q == char:
            mode.client.stop()
        elif chars.c_a == char:
            mode.tablist.back()
        elif chars.c_d == char:
            mode.tablist.next()
        elif chars.c_n == char:
            mode.tablist.add(chat_tab(mode.client, mode.tablist))


class text_mode(ui_state):

    def __init__(self):
        super().__init__()
        kbs = kbinding()
        self.kbs = kbs

        kbs.on_any = lambda c: self.textbox.append(c)
        kbs.bind(keys.k_enter, lambda c: self.tab.send_text())

    def on_en(self):
        self.client.mark_dirty()
        self.textbox.clear()

    def draw_on(self, buf: buffer):
        tip = utils.fillto(f"{i18n.trans('modes.text_mode.name')}:", " ", 40)
        buf.addtext(text=tip, fgcolor=CmdFgColor.White,
                    bkcolor=CmdBkColor.Blue,
                    end='\n')

    def on_input(self, char: chars.char):
        c = self.client
        if c.key_quit_text_mode == char:
            self.sm.enter(cmd_mode)
        elif True:
            self.kbs.trigger(char)
