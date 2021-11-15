from typing import Callable, Optional, Union, TypeVar

import chars
from ui.outputs import buffer

STATE = TypeVar('STATE')


class state:
    sm: "smachine"

    def on_en(self):
        pass

    def on_ex(self):
        pass


class smachine:
    def __init__(self, state_pre: Callable[[STATE], None] = None, stype_pre: Callable[[type], STATE] = None,
                 allow_repeated_entry: bool = True):
        self.cur: Optional[STATE] = None
        self.pre: Optional[STATE] = None
        self.state_pre = state_pre
        self.stype_pre = stype_pre
        self.allow_repeated_entry = allow_repeated_entry

    def enter(self, s: Union[STATE, type]):
        if not self.allow_repeated_entry:
            if isinstance(s, type) and type(self.cur) == s:
                return

        if isinstance(s, type):
            if self.stype_pre is not None:
                s = self.stype_pre(s)
            else:
                s = s()
        else:
            if self.state_pre is not None:
                self.state_pre(s)

        s.sm = self
        if self.pre is not None:
            self.pre.on_ex()
        self.pre = self.cur
        self.cur = s
        if self.cur is not None:
            self.cur.on_en()

    def back(self):
        self.enter(self.pre)


class ui_state(state):
    textbox: "textbox"
    client: "client"
    tablist: "tablist"
    sm: "ui_smachine"

    def __init__(self):
        super().__init__()

    def draw_on(self, buf: buffer):
        pass

    def on_input(self, char: chars.char):
        pass


class ui_smachine(smachine):

    def draw_on(self, buf: buffer):
        if self.cur is not None:
            self.cur.draw_on(buf)

    def on_input(self, char: chars.char):
        if self.cur is not None:
            return self.cur.on_input(char)
