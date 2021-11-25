import traceback
from collections import namedtuple

import GLOBAL
import i18n
import keys
import states
import utils
from cmd import *
from ui import outputs as output
from ui.outputs import CmdStyle
from ui.tabs import *
from ui.uistates import ui_state


def common_hotkey(char: chars.char, tab: tab, client: iclient, tablist: tablist, win: iwindow):
    """

    :param win:
    :param tab:
    :param char:
    :param client:
    :param tablist:
    :return: (True | None) Whether the char wasn't consumed
    """
    if chars.c_q == char:
        client.stop()
    elif chars.c_a == char:
        tablist.back()
    elif chars.c_s == char:
        tablist.switch()
    elif chars.c_d == char:
        tablist.next()
    elif chars.c_x == char:
        tablist.remove(tab)
    elif chars.c_n == char:
        chat = win.new_chat_tab()
        tablist.add(chat)
    elif chars.c_m == char:
        main_menu = win.newtab('main_menu_tab')
        tablist.add(main_menu)
    else:
        return True


Cmd_Context = namedtuple("Cmd_Context", ["client", "win", "tablist", "network", "tab", "cmd_manager"])


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


class cmd_state(states.state):
    mode: "cmd_mode"
    sm: "cmd_smachine"

    def __init__(self, mode: "cmd_mode"):
        self.mode = mode

    def on_input(self, char: chars.char) -> Is_Consumed:
        pass


class cmd_smachine(states.smachine):
    def on_input(self, char: chars.char):
        if self.cur is not None:
            return self.cur.on_input(char)


class cmd_mode(ui_state):
    def __init__(self):
        super().__init__()
        self.cmd_history: List[str] = []
        self.cmd_history_index = 0
        self.last_cmd_history: Optional[str] = None
        self.long_cmd_mode_type: Type[cmd_long_mode] = cmd_long_mode
        self.hotkey_cmd_mode_type: Type[cmd_hotkey_mode] = cmd_hotkey_mode

        def gen_state(statetype: type) -> cmd_state:
            if issubclass(statetype, cmd_state):
                s = statetype(self)
                return s
            else:
                return statetype()

        self.cmd_sm = cmd_smachine(stype_pre=gen_state, allow_repeated_entry=False)

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
        self.cmd_sm.enter(self.hotkey_cmd_mode_type)
        self.client.mark_dirty()
        self.textbox.clear()
        self.cmd_manager: cmdmanager = self.client.cmd_manger

    def paint_on(self, buf: buffer):
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

    def gen_context(self) -> Cmd_Context:
        contxt = Cmd_Context(self.client, self.client.win, self.tablist, self.client.network, self.tab,
                             self.cmd_manager)
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
        # switch mode and input
        self.switch_mode()
        self.cmd_sm.on_input(char)
        self.switch_mode()

    def switch_mode(self):
        if self.long_cmd_mode_type and self.is_long_cmd_mode:
            self.cmd_sm.enter(self.long_cmd_mode_type)
        elif self.hotkey_cmd_mode_type:
            self.cmd_sm.enter(self.hotkey_cmd_mode_type)


def _error_style_text(text: str) -> str:
    return output.tintedtxt(text, style=CmdStyle.Bold,
                            fgcolor=CmdFgColor.Red, end="")


def _tip_style_text(text: str) -> str:
    return output.tintedtxt(text, fgcolor=CmdFgColor.Green, end="")


def _error_style_i18n_text(key: str, *args, **kwargs) -> str:
    return output.tintedtxt(i18n.trans(key, *args, **kwargs), style=CmdStyle.Bold,
                            fgcolor=CmdFgColor.Red, end="")


def _error_style_textX(IO, text: str):
    output.tintedtxtIO(IO, text, style=CmdStyle.Bold,
                       fgcolor=CmdFgColor.Red, end="")


def _tip_style_textX(IO, text: str):
    output.tintedtxtIO(IO, text, fgcolor=CmdFgColor.Green, end="")


def _error_style_i18n_textX(IO, key: str, *args, **kwargs):
    output.tintedtxtIO(IO, i18n.trans(key, *args, **kwargs), style=CmdStyle.Bold,
                       fgcolor=CmdFgColor.Red, end="")


_EST = _error_style_text
_TST = _tip_style_text
_EST18 = _error_style_i18n_text

_ESTX = _error_style_textX
_TSTX = _tip_style_textX
_EST18X = _error_style_i18n_textX


class cmd_long_mode(cmd_state):
    def __init__(self, mode: cmd_mode):
        super().__init__(mode)
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
        contxt: Cmd_Context = mode.gen_context()
        try:
            mode.cmd_manager.execute(contxt, cmd_name, args)
        except WrongUsageError as wu:
            with StringIO() as s:
                _EST18X(s, "modes.command_mode.cmd.wrong_usage")
                s.write(':\n')
                pos = wu.position
                is_pos_quoted = is_quoted(pos + 1, quoted_indexes)
                s.write(gen_cmd_error_text(cmd_name, args, full_cmd, pos, _TST(wu.msg), is_pos_quoted))
                mode.tab.add_string(s.getvalue())
        except CmdNotFound as cnt:
            error_output = gen_cmd_error_text(
                cmd_name, args, full_cmd, -1,
                _EST18("modes.command_mode.cmd.cannot_find", name=cmd_name))
            mode.tab.add_string(error_output)
        except CmdError as ce:
            with StringIO() as s:
                _EST18X(s, "modes.command_mode.cmd.cmd_error")
                s.write(':\n')
                s.write(gen_cmd_error_text(cmd_name, args, full_cmd, -2, _TST(ce.msg)))
                mode.tab.add_string(s.getvalue())
        except Exception as any_e:
            with StringIO() as s:
                _EST18X(s, "modes.command_mode.cmd.unknown_error")
                s.write(':\n')
                s.write(gen_cmd_error_text(
                    cmd_name, args, full_cmd, -2,
                    i18n.trans("modes.command_mode.cmd.not_support", name=cmd_name)))
                mode.tab.add_string(s.getvalue())
                mode.tab.logger.error(f"{any_e}\n{traceback.format_exc()}")

        mode.cmd_history.append(full_cmd)
        mode.cmd_history_index = 0
        tb.clear()

    def on_input(self, char: chars.char) -> Is_Consumed:
        mode = self.mode
        tb = mode.textbox

        # execute command
        if keys.k_enter == char:
            self.cmd_long_mode_execute_cmd()
        # auto filling
        elif chars.c_tab_key == char:
            return Not_Consumed
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
            consumed = tb.on_input(char)  # normally,add this char into textbox
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
        return Consumed


class cmd_hotkey_mode(cmd_state):
    def __init__(self, mode: cmd_mode):
        super().__init__(mode)

    def on_input(self, char: chars.char) -> Is_Consumed:
        mode = self.mode
        tb = mode.textbox

        if chars.c_colon == char:
            tb.append(chars.c_colon)
        else:
            not_consumed = common_hotkey(char, mode.tab, mode.client, mode.tablist, mode.client.win)
            if not_consumed:
                return False
        return True
