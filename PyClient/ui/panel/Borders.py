from ui.Controls import *
from ui.themes import BorderTheme, rounded_rectangle

NoneType = type(None)


class Border(UIElement):

    def __init__(self, theme: BorderTheme = rounded_rectangle):
        super().__init__()
        self.Theme = theme
        self._inner: Optional[Control] = None
        self._onInnerChanged = Event(Border, (Control, NoneType), (Control, NoneType))
        self.OnInnerChanged.Add(lambda _, _1, _2: self.OnRenderContentChanged)

    @property
    def Inner(self) -> Optional[Control]:
        return self._inner

    @Inner.setter
    def Inner(self, value: Optional[Control]):
        old = self._inner
        if old != value:
            if old:
                self.RemoveChild(old)
            self._inner = value
            if value:
                self.AddChild(value)
            self.OnInnerChanged(self, old, value)

    def Measure(self):
        if not self.IsVisible:
            return
        inner = self.Inner
        if inner and inner.IsVisible:
            idw = inner.DWidth
            idh = inner.DHeight
            self.DWidth = idw + 2
            self.DHeight = idh + 2
        else:
            self.DWidth = 2
            self.DHeight = 2

    def Arrange(self, width: int, height: int) -> Tuple[int, int]:
        if not self.IsVisible:
            return 0, 0
        inner = self.Inner
        if inner and inner.IsVisible:
            iw, ih = inner.Arrange(width - 2, height - 2)
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
        if self.Inner:
            self.Inner.PaintOn(Viewer(1, 1, rw - 2, rh - 2, canvas))

    @property
    def OnInnerChanged(self) -> Event:
        """
        Para 1:Border object

        Para 2:old inner Control

        Para 3:new inner Control

        :return: Event(Border,Optional[Control],Optional[Control])
        """
        return self._onInnerChanged
