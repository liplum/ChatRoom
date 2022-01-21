from ui.Controls import *
from ui.panel.ContentControls import ContentControl
from ui.themes import BorderTheme, rounded_rectangle

NoneType = type(None)


class Border(ContentControl):

    def __init__(self, theme: BorderTheme = rounded_rectangle):
        super().__init__()
        self.Theme = theme

    def Measure(self):
        if not self.IsVisible:
            self.DWidth = 0
            self.DHeight = 0
            return
        content = self.Content
        if content and content.IsVisible:
            idw = content.DWidth
            idh = content.DHeight
            self.DWidth = idw + 2
            self.DHeight = idh + 2
        else:
            self.DWidth = 2
            self.DHeight = 2

    def Arrange(self, width: int, height: int) -> Tuple[int, int]:
        if not self.IsVisible:
            self.RenderWidth = 0
            self.RenderHeight = 0
            return 0, 0
        content = self.Content
        if content and content.IsVisible:
            iw, ih = content.Arrange(width - 2, height - 2)
            self.RenderWidth = iw + 2
            self.RenderHeight = ih + 2
        else:
            self.RenderWidth = 2
            self.RenderHeight = 2
        return self.RenderWidth, self.RenderHeight

    def PaintOn(self, canvas: Canvas):
        rw = self.RenderWidth
        rh = self.RenderHeight
        if rw <= 0 and rh <= 0:
            return
        theme = self.Theme
        canvas.Char(0, 0, theme.LeftTop)  # left top
        canvas.Char(0, rh - 1, theme.LeftBottom)  # left bottom
        canvas.Char(rw - 1, 0, theme.RightTop)  # right top
        canvas.Char(rw - 1, rh - 1, theme.RightBottom)  # right bottom
        for w in range(1, rw - 1):
            canvas.Char(w, 0, theme.Horizontal)
            canvas.Char(w, rh - 1, theme.Horizontal)
        for h in range(1, rh - 1):
            canvas.Char(0, h, theme.Vertical)
            canvas.Char(rw - 1, h, theme.Vertical)
        content = self.Content
        if content:
            content.PaintOn(Viewer(1, 1, rw - 2, rh - 2, canvas))
