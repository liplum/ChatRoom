from io import StringIO
from typing import Iterable

import utils
from ui.ctrl import *
from ui.outputs import buffer
from ui.themes import theme, vanilla
from ui.control.display_boards import horizontal_lineIO
Word = str
Words = Iterable[str]
WordsGetter = Callable[[], Words]


# TODO:Complete This
class textblock(control):
    """
    ┌────────────────────────────────┐
    │Beautiful is better than ugly.  │
    │Explicit is better than         │
    │implicit.Simple is better than  │
    │complex.Complex is better than  │
    │complicated...                  │
    └────────────────────────────────┘
    """

    def __init__(self, contents: WordsGetter, theme: theme = vanilla):
        super().__init__()
        if isinstance(contents, str):
            self.contents = lambda: contents
        else:
            self.contents = contents
        self.theme = theme
        self._width = auto
        self._height = auto
        self._r_width = 0
        self._r_height = 0

    def paint_on(self, buf: buffer):
        if self._layout_changed:
            self.cache_layout()
        render_width = self.render_width
        if render_width == 0 or self.render_height == 0:
            return
        with StringIO() as s:
            contents = self.contents()
            theme = self.theme
            left_top = theme.left_top
            left_bottom = theme.left_bottom
            right_top = theme.right_top
            right_bottom = theme.right_bottom
            horizontal = theme.horizontal
            vertical = theme.vertical
            start = 0
            end = self.render_height - 1
            render_height = self.render_height


            for i in range(self.render_height):
                utils.repeatIO(s, ' ', self.left_margin)
                if i == start:  # first line-- a horizontal line
                    horizontal_lineIO(s, render_width, left_top, right_top, horizontal)
                    s.write('\n')
                elif i == end:  # last line -- a horizontal line
                    horizontal_lineIO(s, render_width, left_bottom, right_bottom, horizontal)
                    s.write('\n')
                else:  # content in the middle
                    index = i - self._vertical_margin - 1
                    content = contents[index]
                    content_len = len(content)
                    if content_len >= render_width - 2:
                        content = content[0:render_width - 2]
                        s.write(vertical)
                        s.write(content)
                        s.write(vertical)
                    else:
                        s.write(vertical)
                        s.write(content)
                        rest = render_width - 2 - content_len
                        utils.repeatIO(s, ' ', rest)
                        s.write(vertical)
                    s.write('\n')

            buf.addtext(s.getvalue(), end='')

    @property
    def focusable(self) -> bool:
        return False

    @property
    def width(self) -> PROP:
        return self._width

    @width.setter
    def width(self, value: PROP):
        if self.width != value:
            if value == auto:
                self._width = auto
            else:
                self._width = max(0, value)
            self.on_prop_changed(self, "width")

    @property
    def render_height(self) -> int:
        return self._r_height

    @property
    def render_width(self) -> int:
        return self._r_width

    @property
    def height(self) -> PROP:
        return self._height

    @height.setter
    def height(self, value: PROP):
        if self._height != value:
            if value == auto:
                self._height = auto
            else:
                self._height = max(0, value)
            self.on_prop_changed(self, "height")

    def cache_layout(self):
        if not self._layout_changed:
            return
        self._layout_changed = False
        contents = self.contents()
        if self.width == auto:
            max_width = max(len(t) for t in contents)
            self._r_width = max_width + 2
            self._horizontal_margin = 0
        else:
            self._r_width = self.width
            max_width = max(len(t) for t in contents)
            difference = self.width - (max_width + 2)
            if difference >= 0:
                self._horizontal_margin = difference // 2
            else:
                self._horizontal_margin = 0

        contentlen = len(contents)
        if self.height == auto:
            self._r_height = len(contents) + 2
            self._vertical_margin = 0
        else:
            self._r_height = self.height
            difference = self.height - (contentlen + 2)
            if difference >= 0:
                self._vertical_margin = difference // 2
            else:
                self._vertical_margin = 0

    def notify_content_changed(self):
        self.on_content_changed(self)
        self._layout_changed = True
