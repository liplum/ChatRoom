from typing import NoReturn

import keys
from ui.controls import *
from ui.outputs import buffer, CmdBkColor, CmdFgColor, tintedtxtIO
from ui.shared import IsConsumed, Consumed, NotConsumed


class button(text_control):

    def reload(self):
        self.IsLayoutChanged = True
        self.cache_layout()

    def cache_layout(self):
        if not self.IsLayoutChanged:
            return
        self.IsLayoutChanged = False
        content = self.content()
        content_len = len(content)
        width = self.width
        if width != auto:
            self._r_width = width
            rest = width - content_len
            if rest <= 1:
                self.margin = 0
            else:
                self.margin = (rest + 1) // 2
        else:
            self._r_width = content_len + 2 * self.margin

    def paint_on(self, buf: buffer):
        if self.IsLayoutChanged:
            self.cache_layout()
        with StringIO() as s:
            utils.repeatIO(s, ' ', self.left_margin)
            bk = CmdBkColor.White if self.is_focused else None
            fg = CmdFgColor.Black if self.is_focused else None
            tintedtxtIO(s, self.distext, fgcolor=fg, bkcolor=bk)
            buf.addtext(s.getvalue(), end='')

    def Arrange(self, canvas: Optional[Canvas]):
        if not self.IsLayoutChanged:
            return
        self.IsLayoutChanged = False
        content = self.content()
        content_len = len(content)
        width = self.width
        if width != auto:
            if canvas:
                width = min(width, canvas.Width)
            self._r_width = width
            rest = width - content_len
            if rest <= 1:
                self.margin = 0
            else:
                self.margin = (rest + 1) // 2
        else:
            if canvas:
                width = canvas.Width
            self._r_width = width
            rest = width - content_len
            if rest <= 1:
                self.margin = 0
            else:
                self.margin = (rest + 1) // 2

    def PreArrange(self):
        content = self.content()
        content_len = len(content)
        width = self.width
        if width != auto:
            self._r_width = width
            rest = width - content_len
            if rest <= 1:
                self.margin = 0
            else:
                self.margin = (rest + 1) // 2
        else:
            self._r_width = content_len + 2 * self.margin

    def PaintOn(self, canvas: Canvas):
        if self.IsLayoutChanged:
            self.Arrange(canvas)
        g = StrWriter(canvas, 0, 0, self.render_width, self.render_height)
        bk = BK.White if self.is_focused else None
        fg = FG.Black if self.is_focused else None
        g.Write(self.distext, bk, fg)

    @property
    def distext(self) -> str:
        with StringIO() as s:
            content = self.content()
            content_len = len(content)
            render_width = self.render_width
            is_odd = content_len % 2 == 1
            margin = self.margin
            if margin > 0:
                if self.is_focused:
                    utils.repeatIO(s, " ", margin)
                    self._render_charsIO(s, content)
                    if is_odd:
                        utils.repeatIO(s, " ", margin - 1)
                    else:
                        utils.repeatIO(s, " ", margin)
                else:
                    self._render_charsIO(s, '[')
                    utils.repeatIO(s, " ", margin - 1)
                    self._render_charsIO(s, content)
                    if is_odd:
                        utils.repeatIO(s, " ", margin - 2)
                    else:
                        utils.repeatIO(s, " ", margin - 1)
                    self._render_charsIO(s, ']')
            else:
                s.write(content[0:render_width])
            return s.getvalue()

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

    def on_input(self, char: chars.char) -> IsConsumed:
        if keys.k_enter == char:
            self.press()
            return Consumed
        elif chars.c_esc == char:
            self.on_exit_focus(self)
            return Consumed
        return NotConsumed

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
        if value != auto:
            value = 1
        self._height = value

    @property
    def focusable(self) -> bool:
        return True

    def __repr__(self) -> str:
        return f"<button {self.content()}>"

    @property
    def render_width(self) -> int:
        return self._r_width
