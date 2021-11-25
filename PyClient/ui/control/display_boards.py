import utils
from ui.ctrl import *
from ui.outputs import buffer
from ui.themes import vanilla, ThemeGetter, is_theme

Display_alignment = int
DCenter = 0
DLeft = 1
DRight = 2

AlignmentInfo = Any
"""
Any obj which override __getitem__(self,key:int).The key will be given a index from contents.
"""
AlignmentGetter = Callable[[], AlignmentInfo]
DefaultAlignment = DCenter


def _get_alignment(alignments: Optional[AlignmentInfo], index: int) -> Display_alignment:
    if alignments is None:
        return DefaultAlignment
    try:
        return alignments[index]
    except:
        return DefaultAlignment


_GA = _get_alignment


def horizontal_lineIO(IO, width: int, left: str, right: str, horizontal: str):
    if width == 0:
        return
    IO.write(left)
    if width == 1:
        return
    if width == 2:
        IO.write(right)
        return
    utils.repeatIO(IO, horizontal, width - 2)
    IO.write(right)


class display_board(text_control):
    """
    ┌────────┐
    │  Text  │
    └────────┘
    """

    def __init__(self, contents: ContentsGetter, alignments: AlignmentGetter = None, theme: ThemeGetter = vanilla):
        super().__init__()
        if isinstance(contents, Collection):
            self.contents = lambda: contents
        else:
            self.contents = contents
        self.alignments = alignments
        if is_theme(theme):
            self.theme = lambda: theme
        else:
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
        render_width = self.render_width
        if render_width == 0 or self.render_height == 0:
            return
        with StringIO() as s:
            alignments = self.alignments() if self.alignments else None
            contents = self.contents()
            theme = self.theme()
            start = 0
            end = self.render_height - 1
            for i in range(self.render_height):
                utils.repeatIO(s, ' ', self.left_margin)
                if i == start:  # first line-- a horizontal line
                    horizontal_lineIO(s, render_width, theme.left_top, theme.right_top, theme.horizontal)
                    s.write('\n')
                elif i == end:  # last line -- a horizontal line
                    horizontal_lineIO(s, render_width, theme.left_bottom, theme.right_bottom, theme.horizontal)
                    s.write('\n')
                elif 0 <= i - self._vertical_margin - 1 < len(contents):  # content in the middle
                    index = i - self._vertical_margin - 1
                    content = contents[index]
                    content_len = len(content)
                    if content_len >= render_width - 2:
                        content = content[0:render_width - 2]
                        s.write(theme.vertical)
                        self._render_charsIO(s, content)
                        s.write(theme.vertical)
                    else:
                        s.write(theme.vertical)
                        alignment = _GA(alignments, index)
                        if alignment == DCenter:
                            cur_hor_margin = (render_width - content_len - 2) // 2
                            utils.repeatIO(s, ' ', cur_hor_margin)
                            self._render_charsIO(s, content)
                            utils.repeatIO(s, ' ', cur_hor_margin)
                            missing = render_width - 1 - (content_len + 1 + cur_hor_margin * 2)
                            utils.repeatIO(s, ' ', missing)
                        elif alignment == DLeft:
                            self._render_charsIO(s, content)
                            rest = render_width - 2 - content_len
                            utils.repeatIO(s, ' ', rest)
                        else:
                            rest = render_width - 2 - content_len
                            utils.repeatIO(s, ' ', rest)
                            self._render_charsIO(s, content)
                        s.write(theme.vertical)
                    s.write('\n')
                else:  # blank line
                    horizontal_lineIO(s, render_width, theme.vertical, theme.vertical, ' ')
                    s.write('\n')
            buf.addtext(s.getvalue(), end='')

    @property
    def focusable(self) -> bool:
        return False

    @property
    def render_height(self) -> int:
        return self._r_height

    @property
    def render_width(self) -> int:
        return self._r_width

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
