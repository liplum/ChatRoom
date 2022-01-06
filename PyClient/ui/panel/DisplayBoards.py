from ui.Controls import *
from ui.themes import theme, rounded_rectangle

NoneType = type(None)
from ui.panel.Borders import Border


class DisplayBoard(Control):
    def __init__(self, theme: theme = rounded_rectangle):
        super().__init__()
        self._rWidth = 0
        self._rHeight = 0
        self.border = Border(theme)
        self.AddVElem(self.border)

    def OnAddedInfoVTree(self, parent: "VisualElement"):
        pass

    @property
    def Inner(self) -> Optional[Control]:
        return self.border.Inner

    @Inner.setter
    def Inner(self, value: Optional[Control]):
        old = self.border.Inner
        if old != value:
            self.RemoveLElem(old)
            self.border.Inner = value
            if value:
                self.AddLElem(value)

    def PaintOn(self, canvas: Canvas):
        rw = self.render_width
        rh = self.render_height
        if rw <= 0 and rh <= 0:
            return
        theme = self.Theme
        canvas.Char(0, 0, theme.left_top)  # left top
        canvas.Char(0, rh - 1, theme.left_bottom)  # left bottom
        canvas.Char(rw - 1, 0, theme.right_top)  # right top
        canvas.Char(rw - 1, rh - 1, theme.right_bottom)  # right bottom
        for w in range(1, rw - 1):
            canvas.Char(w, 0, theme.horizontal)
            canvas.Char(w, rh - 1, theme.horizontal)
        for h in range(1, rh - 1):
            canvas.Char(0, h, theme.vertical)
            canvas.Char(rw - 1, h, theme.vertical)
        if self.Inner:
            innerViewer = Viewer(1, 1, rw - 2, rh - 2, canvas)
            self.Inner.PaintOn(innerViewer)

    def Measure(self):
        dWidth = self.width
        dHeight = self.height
        inner = self.Inner
        if inner and (dWidth == auto or dHeight == auto):
            inner.Measure()
        if dWidth == auto:
            w = inner.width + 2
        else:
            w = dWidth

        if inner:
            inner.width = w - 2

        if dHeight == auto:
            h = inner.height + 2
        else:
            h = dHeight

        if inner:
            inner.height = h - 2

        self._rWidth = w
        self._rHeight = h

    def Arrange(self, width: Optional[int] = None, height: Optional[int] = None):
        dWidth = self.width
        dHeight = self.height
        inner = self.Inner
        if inner and (dWidth == auto or dHeight == auto):
            inner.Measure()
        if not self.IsLayoutChanged:
            return
        if limited:
            self.IsLayoutChanged = False
        oldw = self._rWidth
        oldh = self._rHeight

        if dWidth == auto:
            if limited:
                w = min(inner.render_width + 2, width)
            else:
                w = inner.width + 2
        else:
            w = dWidth

        if inner:
            inner.width = w - 2

        if dHeight == auto:
            if limited:
                h = min(inner.render_height + 2, height)
            else:
                h = inner.height + 2
        else:
            h = dHeight

        if inner:
            inner.height = h - 2

        self._rWidth = w
        self._rHeight = h
        if oldw != w or oldh != h:
            self.OnLayoutChanged(self)
            inner.Arrange(self.render_width - 2, self.render_height - 2)

    @property
    def render_height(self) -> int:
        return self._rHeight

    @property
    def render_width(self) -> int:
        return self._rWidth

    @property
    def focusable(self) -> bool:
        return True
