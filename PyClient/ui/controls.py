from dataclasses import dataclass
from io import StringIO
from typing import Union, List, Optional, Callable

import chars
import keys
import utils
from core.chats import roomid
from core.events import event
from net.networks import server_token
from ui import outputs as output
from utils import clear_screen, get
from io import StringIO


class textbox:
    def __init__(self, cursor_icon: str = "^"):
        self._input_list = []
        self.cursor_icon = cursor_icon
        self._cursor: int = 0
        self._cursor: int = 0
        self._on_cursor_move = event()
        self._on_append = event()
        self._on_delete = event()
        self._on_gen_distext = event()
        self._on_list_replace = event()

    @property
    def on_gen_distext(self) -> event:
        """
        Para 1:textbox object


        Para 2:the final string which will be displayed soon(render_content.string)

        :return: event(textbox,render_content)
        """
        return self._on_gen_distext

    @property
    def on_cursor_move(self) -> event:
        """
        Para 1:textbox object


        Para 2:former cursor position


        Para 3:current cursor position

        :return: event(textbox,int,int)
        """
        return self._on_cursor_move

    @property
    def on_append(self) -> event:
        """
        Para 1:textbox object


        Para 2:cursor position


        Para 3:char appended

        :return: event(textbox,int,str)
        """
        return self._on_append

    @property
    def on_delete(self) -> event:
        """
        Para 1:textbox object


        Para 2:cursor position


        Para 3:char deleted

        :return: event(textbox,int,str)
        """
        return self._on_delete

    @property
    def on_list_replace(self) -> event:
        """
        Para 1:textbox object


        Para 2:former list


        Para 3:current list

        :return: event(textbox,list,list)
        """
        return self._on_list_replace

    @property
    def input_list(self):
        return self._input_list[:]

    @property
    def input_count(self):
        return len(self._input_list)

    @input_list.setter
    def input_list(self, value):
        former = self._input_list
        if isinstance(value, list):
            self._input_list = value[:]
        else:
            self._input_list = list(value)
        self.cursor = 0
        self.on_list_replace(self, former, self._input_list)

    @property
    def inputs(self) -> str:
        return utils.compose(self.input_list, connector='')

    def clear(self):
        self.input_list = []

    @property
    def cursor(self):
        return self._cursor

    @cursor.setter
    def cursor(self, value):
        list_len = len(self._input_list)
        former = self._cursor
        current = min(max(0, value), list_len)
        if former != current:
            self._cursor = current
            self.on_cursor_move(self, former, current)

    def home(self):
        self.cursor = 0

    def left(self):
        self.cursor -= 1

    def right(self):
        self.cursor += 1

    def end(self):
        self.cursor = self.input_count

    @property
    def distext(self) -> str:
        cursor_pos = self._cursor
        with StringIO() as s:
            cur = 0
            for char in self._input_list:
                if cur == cursor_pos:
                    s.write(self.cursor_icon)
                s.write(char)
                cur += 1
            if cur == cursor_pos:
                s.write(self.cursor_icon)

            res = s.getvalue()
            dis = render_content(res)
            self.on_gen_distext(self, dis)
            return dis.string

    def append(self, char):
        self._input_list.insert(self._cursor, char)
        self.on_append(self, self.cursor, char)
        self.cursor += 1

    def delete(self, left=True):
        if self._cursor > 0:
            n = self._cursor - 1 if left else self._cursor
            if n < len(self._input_list):
                ch = self._input_list.pop(n)
                self.on_delete(self, self.cursor, ch)
                self.cursor -= 1


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
        kbs.on_any = lambda c: spapp(chars.to_str(c))

    def append(self, ch: Union[str, chars.char]):
        if isinstance(ch, str):
            super().append(ch)
        elif isinstance(ch, chars.char):
            consumed = self.kbs.trigger(ch)
            if not consumed:
                super().append(to_str(ch))


class tab:
    def __init__(self):
        pass

    @property
    def distext(self) -> str:
        return ""


class chat_tab(tab):

    def __init__(self, max_lines: int = 10):
        super().__init__()
        self.history: List[str] = []
        self.max_display_line = max_lines

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

    def add(self, tab: tab):
        self.tabs.append(tab)

    def remove(self, item: Union[int, tab]):
        if isinstance(item, int):
            del self.tabs[item]
        elif isinstance(item, tab):
            self.tabs.remove(item)

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


class window:
    def __init__(self, displayer: output.i_display):
        self.history: List[str] = []
        self.max_display_line = 10
        self.displayer: output.i_display = displayer
        self.fill_until_max: bool = False
        self.tabli = tablist(self)

    def newtab(self):
        pass

    def display(self):
        clear_screen()
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

    def add_text(self, text: str):
        self.history.append(text)

    def clear_all(self):
        self.history = []


@dataclass
class render_content:
    string: str


class kbinding:
    def __init__(self):
        self.bindings = {}
        self._on_any = None

    def bind(self, ch: chars.char, func):
        self.bindings[ch] = func

    @property
    def on_any(self):
        return self._on_any

    @on_any.setter
    def on_any(self, func):
        self._on_any = func

    def trigger(self, ch: chars.char, *args, **kwargs) -> bool:
        func = get(self.bindings, ch)
        if func is not None:
            func(ch, *args, **kwargs)
            return True
        if self.on_any is not None:
            self.on_any(ch, *args, **kwargs)
            return True
        return False


class state:
    def on_en(self):
        pass

    def on_ex(self):
        pass

    def update(self):
        pass

    def on_input(self, char: chars.char):
        pass


class smachine:
    def __init__(self, state_pre: Callable[[state], None] = None, stype_pre: Callable[[type], state] = None):
        self.cur: Optional[state] = None
        self.pre: Optional[state] = None
        self.state_pre = state_pre
        self.stype_pre = stype_pre

    def enter(self, s: Union[state, type]):
        if isinstance(s, state):
            if self.state_pre is not None:
                self.state_pre(s)
        elif isinstance(s, type):
            if self.stype_pre is not None:
                s = self.stype_pre(s)
            else:
                s = s()
        if self.pre is not None:
            self.pre.on_ex()
        self.pre = self.cur
        self.cur = s
        if self.cur is not None:
            self.cur.on_en()

    def back(self):
        self.enter(self.pre)

    def update(self):
        if self.cur is not None:
            self.cur.update()

    def on_input(self, char: chars.char):
        if self.cur is not None:
            return self.cur.on_input(char)


class client_state(state):
    def __init__(self, client: "client"):
        super().__init__()
        self.client: "client" = client


class cmd_mode(client_state):
    def __init__(self, client: "client"):
        super().__init__(client)
        self.islongcmd = False
        self.longcmd = ""

    def on_en(self):
        self.client.make_dirty()
        self.client.textbox.clear()

    tip: str = utils.fillby("Command mode:", " ", 40)

    def update(self):
        c = self.client
        dlock = c.display_lock
        dlock(c.win.display)
        dlock(c.display.display_text, text=cmd_mode.tip, fgcolor=output.CmdBkColor.Black,
              bkcolor=output.CmdBkColor.Blue,
              end='\n')

    def enter_long_cmd_mode(self):
        self.islongcmd = True

    def quit_long_cmd_mode(self):
        self.islongcmd = False

    def on_input(self, char: chars.char):
        c = self.client
        tb = c.textbox
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
                c.sm.enter(text_mode)
                return True
            elif chars.c_colon == char:
                self.enter_long_cmd_mode()
                tb.append(chars.c_colon)
            elif chars.c_q == char:
                c.running = False


class text_mode(client_state):

    def __init__(self, client: "client"):
        super().__init__(client)
        kbs = kbinding()
        self.kbs = kbs

        def send_text():
            inputs = self.client.textbox.inputs
            self.client.send_text(roomid(12345), inputs, server_token("127.0.0.1", 5000))
            self.client.textbox.clear()

        kbs.bind(keys.k_enter, lambda c: send_text())
        kbs.on_any = lambda c: self.client.textbox.append(c)

    def on_en(self):
        self.client.make_dirty()
        self.client.textbox.clear()

    tip: str = utils.fillby("Text mode:", " ", 40)

    def update(self):
        c = self.client
        dlock = c.display_lock
        dlock(c.win.display)
        dlock(c.display.display_text, text=text_mode.tip, fgcolor=output.CmdBkColor.Black,
              bkcolor=output.CmdBkColor.Blue,
              end='\n')

    def on_input(self, char: chars.char):
        c = self.client
        if c.key_quit_text_mode == char:
            c.sm.enter(cmd_mode)
        elif True:
            self.kbs.trigger(char)
