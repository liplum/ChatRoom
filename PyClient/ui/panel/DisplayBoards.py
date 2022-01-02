from ui.controls import *
from ui.themes import theme, rounded_rectangle

NoneType = type(None)


class DisplayBoard(control):
    def __init__(self, theme: theme = rounded_rectangle):
        super().__init__()
        self.Theme = theme
        self._onInnerChanged = Event(DisplayBoard, (control, NoneType), (control, NoneType))
        self.OnInnerChanged.Add(lambda _, _1, _2: self.on_content_changed)
        self._rWidth = 0
        self._rHeight = 0
        self._inner: Optional[control] = None

    @property
    def Inner(self) -> Optional[control]:
        return self._inner

    @Inner.setter
    def Inner(self, value: Optional[control]):
        old = self._inner
        if old != value:
            self._inner = value
            self.OnInnerChanged(self, old, value)

    def PaintOn(self, canvas: Canvas):
        if self.IsLayoutChanged:
            self.Arrange(canvas)
        rw = self.render_width
        rh = self.render_height
        if rw <= 0 and rh <= 0:
            return
        if self.Inner:
            innerViewer = Viewer(1, 1, rw - 2, rh - 2, canvas)
            self.Inner.PaintOn(innerViewer)
        theme = self.Theme
        # top->y=0
        # left->x=0
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

    def Arrange(self, canvas: Optional[Canvas]):
        if not self.IsLayoutChanged:
            return
        self.IsLayoutChanged = False
        inner = self.Inner
        if inner:
            inner.Arrange(None)
        width = self.width
        height = self.height
        if width == auto:
            if canvas:
                self._rWidth = canvas.Width
                if inner:
                    inner.width = self.render_width - 2
            else:
                self._rWidth = inner.width + 2
        else:
            self._rWidth = width
            if inner:
                inner.width = self.render_width - 2
        if height == auto:
            if canvas:
                self._rHeight = canvas.Height
                if inner:
                    inner.height = self.render_height - 2
            else:
                self._rHeight = inner.height + 2
        else:
            self._rHeight = height
            if inner:
                inner.height = self.render_height - 2

    @property
    def render_height(self) -> int:
        return self._rHeight

    @property
    def render_width(self) -> int:
        return self._rWidth

    @property
    def OnInnerChanged(self) -> Event:
        """
        Para 1:DisplayBoard object

        Para 2:old inner control

        Para 3:new inner control

        :return: Event(panel,Optional[control],Optional[control])
        """
        return self._onInnerChanged

    @property
    def focusable(self) -> bool:
        return True
