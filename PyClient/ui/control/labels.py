from ui.controls import *
from ui.outputs import buffer


class label(control):
    def __init__(self, content: ContentGetter):
        super().__init__()
        if isinstance(content, str):
            self.content = lambda: content
        else:
            self.content = content
        self._width: PROP = auto
        self._r_width = 0

    @property
    def width(self) -> PROP:
        return self._width

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
        return False

    def paint_on(self, buf: buffer):
        if self.IsLayoutChanged:
            self.cache_layout()
        if self.left_margin > 0:
            buf.addtext(utils.repeat(' ', self.left_margin), end='')
        content = self.content()
        if self.width != auto:
            if self.width < len(content):
                content = content[0:self.width]
            elif self.width > len(content):
                content = utils.fillto(content, " ", self.width)
        buf.addtext(content, end="")

    def PaintOn(self, canvas: Canvas):
        content = self.content()
        rw = self.render_width
        if rw < len(content):
            content = content[0:self.width]
        elif rw > len(content):
            content = utils.fillto(content, " ", self.width)
        canvas.Str(0, 0, content)

    @width.setter
    def width(self, value: int):
        if self.width != value:
            if value == auto:
                self._width = auto
            else:
                self._width = max(0, value)
            self.on_prop_changed(self, "tw")

    def __repr__(self) -> str:
        return f"<label {self.content()}>"

    def cache_layout(self):
        if not self.IsLayoutChanged:
            return
        self.IsLayoutChanged = False
        if self.width == auto:
            self._r_width = len(self.content())
        else:
            self._r_width = self.width

    def Arrange(self, width: Optional[int] = None, height: Optional[int] = None):
        if not self.IsLayoutChanged:
            return
        if limited:
            self.IsLayoutChanged = False
        if limited:
            if self.width == auto:
                self._r_width = min(len(self.content()), width)
            else:
                self._r_width = min(self.width, width)
        else:
            if self.width == auto:
                self._r_width = len(self.content())
            else:
                self._r_width = self.width

    @property
    def render_width(self) -> int:
        return self._r_width
