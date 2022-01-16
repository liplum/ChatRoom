from ui.Controls import *
from ui.outputs import buffer


class Label(Control):
    def __init__(self, content: ContentGetter):
        super().__init__()
        if isinstance(content, str):
            self.content = lambda: content
        else:
            self.content = content
        self._width: PROP = Auto

    @property
    def width(self) -> PROP:
        return self._width

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
        return False

    def paint_on(self, buf: buffer):
        if self.IsLayoutChanged:
            self.cache_layout()
        if self.left_margin > 0:
            buf.addtext(utils.repeat(' ', self.left_margin), end='')
        content = self.content()
        if self.width != Auto:
            if self.width < len(content):
                content = content[0:self.width]
            elif self.width > len(content):
                content = utils.fillto(content, " ", self.width)
        buf.addtext(content, end="")

    @width.setter
    def width(self, value: int):
        if self.width != value:
            if value == Auto:
                self._width = Auto
            else:
                self._width = max(0, value)
            self.on_prop_changed(self, "tw")

    def __repr__(self) -> str:
        return f"<Label {self.content()}>"

    def cache_layout(self):
        if not self.IsLayoutChanged:
            return
        self.IsLayoutChanged = False
        if self.width == Auto:
            self.RenderWidth = len(self.content())
        else:
            self.RenderWidth = self.width

    def Arrange(self, width: int, height: int) -> Tuple[int, int]:
        if not self.IsVisible:
            self.RenderWidth = 0
            self.RenderHeight = 0
            return 0, 0
        if self.Width == Auto:
            self.RenderWidth = min(len(self.content()), width)
        else:
            self.RenderWidth = min(self.Width, width)
        if self.Height == Auto:
            self.RenderHeight = 1
        else:
            self.RenderHeight = min(self.Height, height)
        return self.RenderWidth, self.RenderHeight

    def Measure(self):
        if not self.IsVisible:
            self.DWidth = 0
            self.DHeight = 0
            return
        if self.Width == Auto:
            self.DWidth = len(self.content())
        else:
            self.DWidth = self.Width
        if self.Height == Auto:
            self.DHeight = 1
        else:
            self.DHeight = self.Height

    def PaintOn(self, canvas: Canvas):
        content = self.content()
        sw = StrWriter(canvas)
        sw.Write(content)
