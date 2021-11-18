from typing import Optional

from ui.ctrl import control, content_getter
from ui.outputs import buffer
import utils

class label(control):
    def __init__(self, content: Optional[content_getter] = None):
        super().__init__()
        self.content = content
        self._width_limited = False
        self._min_width = 1
        self._width = 1

    @property
    def width(self) -> int:
        if self.width_limited:
            return self._width
        else:
            return len(self.content())

    @property
    def height(self) -> int:
        return 1

    @property
    def focusable(self) -> bool:
        return False

    def draw_on(self, buf: buffer):
        content = self.content()
        if self.width_limited:
            if self.width < len(content):
                content = content[0:self.width]
            elif self.width > len(content):
                content = utils.fillto(content," ",self.width)
        buf.addtext(content, end="")

    @property
    def width_limited(self) -> bool:
        return self._width_limited

    @width_limited.setter
    def width_limited(self, value):
        self._width_limited = bool(value)

    @width.setter
    def width(self, value: int):
        self._width = max(self._min_width, value)
        self.width_limited = True
