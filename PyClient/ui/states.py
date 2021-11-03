from typing import Callable, Optional, Union

import chars
from ui.outputs import buffer


class state:
    sm: "smachine"

    def on_en(self):
        pass

    def on_ex(self):
        pass

    def draw_on(self, buf: buffer):
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
        s.sm = self
        if self.pre is not None:
            self.pre.on_ex()
        self.pre = self.cur
        self.cur = s
        if self.cur is not None:
            self.cur.on_en()

    def back(self):
        self.enter(self.pre)

    def draw_on(self, buf: buffer):
        if self.cur is not None:
            self.cur.draw_on(buf)

    def on_input(self, char: chars.char):
        if self.cur is not None:
            return self.cur.on_input(char)
