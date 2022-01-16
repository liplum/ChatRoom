from ui.Controls import *
from ui.themes import BorderTheme, rounded_rectangle

NoneType = type(None)
from ui.panel.Borders import Border


class DisplayBoard(Control):
    def __init__(self, theme: BorderTheme = rounded_rectangle):
        super().__init__()
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
            self.DWidth = 0
            self.DHeight = 0
            return
        dWidth = self.Width
        dHeight = self.Height
        border = self.border
        if dWidth == Auto:
            w = border.DWidth
        else:
            w = dWidth

        if dHeight == Auto:
            h = border.DHeight
        else:
            h = dHeight
        self.DWidth = w
        self.DHeight = h

    def Arrange(self, width: int, height: int) -> Tuple[int, int]:
        if not self.IsVisible:
            self.RenderWidth = 0
            self.RenderHeight = 0
            return 0, 0
        dWidth = self.Width
        dHeight = self.Height
        border = self.border
        if dWidth == Auto:
            bw = min(border.DWidth, width)
        else:
            bw = min(border.Width, width, dWidth)

        if dHeight == Auto:
            bh = min(border.DWidth, width)
        else:
            bh = min(border.Width, width, dHeight)
        rbw, rbh = border.Arrange(bw, bh)
        self.RenderWidth = rbw
        self.RenderHeight = rbh
        return self.RenderWidth, self.RenderHeight

    @property
    def focusable(self) -> bool:
        return True
