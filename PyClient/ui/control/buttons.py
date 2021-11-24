from typing import NoReturn

import keys
import utils
from ui.ctrl import *
from ui.outputs import buffer, CmdBkColor, CmdFgColor
from ui.shared import Is_Consumed, Consumed, Not_Consumed


class button(control):

    def reload(self):
        self._layout_changed = True
        self.cache_layout()

    def cache_layout(self):
        if not self._layout_changed:
            return
        self._layout_changed = False
        content = self.content()
        if self.width != auto:
            self._r_width = self.width
            rest = self.width + 2 - len(content)
            if rest <= 0:
                self.margin = 0
            else:
                self.margin = rest // 2
        else:
            self._r_width = len(content) + 2 * self.margin

    def paint_on(self, buf: buffer):
        if self._layout_changed:
            self.cache_layout()
        if self.left_margin > 0:
            buf.addtext(utils.repeat(' ', self.left_margin), end='')
        bk = CmdBkColor.White if self.is_focused else None
        fg = CmdFgColor.Black if self.is_focused else None
        distext = self.distext
        distext = utils.fillto(distext, " ", self.render_width)
        buf.addtext(distext, end='', fgcolor=fg, bkcolor=bk)

    @property
    def distext(self) -> str:
        if self.margin > 0:
            if self.is_focused:
                margin = utils.repeat(" ", self.margin)
                if self.margin * 2 + 2 < self.render_width:
                    head = " "
                else:
                    head = ""
                res = f"{head}{margin}{self.content()}{margin}"
                return utils.fillto(res, " ", self.render_width)
            else:
                margin = utils.repeat(" ", self.margin - 1)
                if self.margin * 2 + 2 < self.render_width:
                    head = "[ "
                else:
                    head = "["
                return f"{head}{margin}{self.content()}{margin}]"

        else:
            return self.content()

    def __init__(self, content: ContentGetter, on_press: Callable[[], NoReturn]):
        super().__init__()
        if isinstance(content, str):
            self.content = lambda: content
        else:
            self.content = content
        self._margin = 1
        self.on_press_func = on_press
        self._width: PROP = auto
        self._r_width = 0

    def press(self):
        self.on_press_func()

    def on_input(self, char: chars.char) -> Is_Consumed:
        if keys.k_enter == char:
            self.press()
            return Consumed
        elif chars.c_esc == char:
            self.on_exit_focus(self)
            return Consumed
        return Not_Consumed

    @property
    def margin(self) -> int:
        return self._margin

    @margin.setter
    def margin(self, value: int):
        value = max(0, value)
        self._margin = value

    @property
    def width(self) -> PROP:
        return self._width

    @width.setter
    def width(self, value: PROP):
        if self.width != value:
            if value == auto:
                self._width = auto
            else:
                self._width = max(0, value)
                self.on_prop_changed(self, "width")

    @property
    def height(self) -> int:
        return 1

    @height.setter
    def height(self, value: int):
        pass

    @property
    def focusable(self) -> bool:
        return True

    def __repr__(self) -> str:
        return f"<button {self.content()}>"

    @property
    def render_width(self) -> int:
        return self._r_width

    def notify_content_changed(self):
        self.on_content_changed(self)
        self._layout_changed = True
