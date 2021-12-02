import utils
from ui.ctrl import *
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
        if self._layout_changed:
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

    @width.setter
    def width(self, value: int):
        if self.width != value:
            if value == auto:
                self._width = auto
            else:
                self._width = max(0, value)
            self.on_prop_changed(self, "width")

    def __repr__(self) -> str:
        return f"<label {self.content()}>"

    def cache_layout(self):
        if not self._layout_changed:
            return
        self._layout_changed = False
        if self.width == auto:
            self._r_width = len(self.content())
        else:
            self._r_width = self.width

    @property
    def render_width(self) -> int:
        return self._r_width
