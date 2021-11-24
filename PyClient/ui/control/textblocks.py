from io import StringIO

import utils
from ui.ctrl import *
from ui.outputs import buffer
from ui.themes import theme, vanilla


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

    def __init__(self, content: ContentGetter, theme: theme = vanilla):
        super().__init__()
        if isinstance(content, str):
            self.content = lambda: content
        else:
            self.content = content
        self.theme = theme
        self._width = auto
        self._height = auto
        self._r_width = 0
        self._r_height = 0
        self._horizontal_margin = 0
        self._vertical_margin = 0

    def paint_on(self, buf: buffer):
        if self._layout_changed:
            self.cache_layout()
        if self.render_width == 0 or self.render_height == 0:
            return
        with StringIO() as s:
            contents = self.contents()
            theme = self.theme
            start = 0
            end = self.render_height - 1
            for i in range(self.render_height):
                if self.left_margin > 0:
                    utils.repeatIO(s, ' ', self.left_margin)
                if i == start:
                    self.horizontal_lineIO(s, theme.left_top, theme.right_top, theme.horizontal)
                    s.write('\n')
                elif i == end:
                    self.horizontal_lineIO(s, theme.left_bottom, theme.right_bottom, theme.horizontal)
                    s.write('\n')
                elif 0 <= i - self._vertical_margin - 1 < len(contents):
                    index = i - self._vertical_margin - 1
                    content = contents[index]
                    content_len = len(content)
                    if content_len >= self.render_width - 2:
                        content = content[0:self.render_width - 2]
                        s.write(theme.vertical)
                        s.write(content)
                        s.write(theme.vertical)
                    else:
                        s.write(theme.vertical)
                        cur_hor_margin = (self.render_width - content_len - 2) // 2
                        utils.repeatIO(s, ' ', cur_hor_margin)
                        s.write(content)
                        utils.repeatIO(s, ' ', cur_hor_margin)
                        missing = self.render_width - 1 - (content_len + 1 + cur_hor_margin * 2)
                        if missing > 0:
                            utils.repeatIO(s, ' ', missing)
                        s.write(theme.vertical)
                    s.write('\n')
                else:
                    s.write(theme.vertical)
                    utils.repeatIO(s, ' ', self.render_width - 2)
                    s.write(theme.vertical)
                    s.write('\n')
            buf.addtext(s.getvalue(), end='')

    def horizontal_line(self, left: str, right: str, horizontal) -> str:
        width = self.render_width
        start = 0
        end = width - 1
        with StringIO() as s:
            for i in range(width):
                if i == start:
                    s.write(left)
                elif i == end:
                    s.write(right)
                else:
                    s.write(horizontal)
            return s.getvalue()

    def horizontal_lineIO(self, IO, left: str, right: str, horizontal):
        width = self.render_width
        start = 0
        end = width - 1
        for i in range(width):
            if i == start:
                IO.write(left)
            elif i == end:
                IO.write(right)
            else:
                IO.write(horizontal)

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
