from ui.Controls import *
from ui.themes import BorderTheme, rounded_rectangle

NoneType = type(None)
from ui.panel.Borders import Border


class DisplayBoard(Control):
    def __init__(self, theme: BorderTheme = rounded_rectangle):
        super().__init__()
        self._rWidth = 0
        self._rHeight = 0
        self.border = Border(theme)
        self.AddChild(self.border)

    @property
    def Inner(self) -> Optional[Control]:
        return self.border.Inner

    @Inner.setter
    def Inner(self, value: Optional[Control]):
        old = self.border.Inner
        if old != value:
            self.border.Inner = value

    def PaintOn(self, canvas: Canvas):
        rw = self.RenderWidth
        rh = self.RenderHeight
        if rw <= 0 and rh <= 0:
            return
        self.border.PaintOn(Viewer.ByCanvas(canvas))

    def Measure(self):
        if not self.IsVisible:
            return
        dWidth = self.Width
        dHeight = self.Height
        border = self.border
        if dWidth == auto:
            w = border.DWidth
        else:
            w = dWidth

        if dHeight == auto:
            h = border.DHeight
        else:
            h = dHeight
        self.DWidth = w
        self.DHeight = h

    def Arrange(self, width: int, height: int) -> Tuple[int, int]:
        if not self.IsVisible:
            return 0, 0
        dWidth = self.Width
        dHeight = self.Height
        border = self.border
        if dWidth == auto:
            bw = min(border.DWidth, width)
        else:
            bw = min(border.Width, width, dWidth)

        if dHeight == auto:
            bh = min(border.DWidth, width)
        else:
            bh = min(border.Width, width, dHeight)
        rbw, rbh = border.Arrange(bw, bh)
        self.RenderWidth = rbw
        self.RenderHeight = rbh
        return self.RenderWidth, self.RenderHeight

    @property
    def render_height(self) -> int:
        return self._rHeight

    @property
    def render_width(self) -> int:
        return self._rWidth

    @property
    def focusable(self) -> bool:
        return True
