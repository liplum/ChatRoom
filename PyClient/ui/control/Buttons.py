import keys
from ui.Controls import *
from ui.outputs import buffer, CmdBkColor, CmdFgColor, tintedtxtIO
from ui.shared import IsConsumed, Consumed, NotConsumed


class Button(text_control):

    def __init__(self, content: ContentGetter, on_press: Callable[[], NoReturn]):
        super().__init__()
        if isinstance(content, str):
            self.content = lambda: content
        else:
            self.content = content
        self._margin = 1
        self.on_press_func = on_press
        self._width: PROP = Auto

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
        if width != Auto:
            self.RenderWidth = width
            rest = width - content_len
            if rest <= 1:
                self.margin = 0
            else:
                self.margin = (rest + 1) // 2
        else:
            self.RenderWidth = content_len + 2 * self.margin

    def paint_on(self, buf: buffer):
        if self.IsLayoutChanged:
            self.cache_layout()
        with StringIO() as s:
            utils.repeatIO(s, ' ', self.left_margin)
            bk = CmdBkColor.White if self.is_focused else None
            fg = CmdFgColor.Black if self.is_focused else None
            tintedtxtIO(s, self.distext, fgcolor=fg, bkcolor=bk)
            buf.addtext(s.getvalue(), end='')

    def Arrange(self, width: int, height: int) -> Tuple[int, int]:
        if not self.IsVisible:
            self.RenderWidth = 0
            self.RenderHeight = 0
            return 0, 0
        content = self.content()
        self.RenderWidth = min(len(content) + 2, width)
        self.RenderHeight = min(1, height)
        return self.RenderWidth, self.RenderHeight

    def Measure(self):
        if not self.IsVisible:
            self.DWidth = 0
            self.DHeight = 0
            return
        content = self.content()
        self.DWidth = len(content) + 2
        self.DHeight = 1

    def PaintOn(self, canvas: Canvas):
        g = StrWriter(canvas, 0, 0, self.RenderWidth, self.RenderHeight)
        bk = BK.White if self.IsFocused else None
        fg = FG.Black if self.IsFocused else None
        g.Write(self.distext, bk, fg)

    @property
    def distext(self) -> str:
        with StringIO() as s:
            content = self.content()
            content_len = len(content)
            render_width = self.RenderWidth
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
            if value == Auto:
                self._width = Auto
            else:
                self._width = max(0, value)
                self.on_prop_changed(self, "tw")

    @property
    def height(self) -> int:
        return 1

    @height.setter
    def height(self, value: int):
        if value != Auto:
            value = 1
        self._height = value

    @property
    def focusable(self) -> bool:
        return True

    def __repr__(self) -> str:
        return f"<Button {self.content()}>"
