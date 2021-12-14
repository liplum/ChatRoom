import math
from collections import deque
from typing import Iterable

import utils
from ui.control.display_boards import horizontal_lineIO
from ui.ctrl import *
from ui.outputs import buffer
from ui.themes import theme, vanilla

Word = str
Words = Iterable[str]
words_getter = Callable[[], Words]
WordsGetter = Union[Words, words_getter]


class textblock(text_control):
    """
    ┌────────────────────────────────┐
    │Beautiful is better than ugly.  │
    │Explicit is better than         │
    │implicit.Simple is better than  │
    │complex.Complex is better than  │
    │complicated...                  │
    └────────────────────────────────┘
    """

    def __init__(self, words: WordsGetter, theme: theme = vanilla):
        super().__init__()
        if isinstance(words, Iterable):
            self.words = lambda: words
        else:
            self.words = words
        self.theme = theme
        self._width = auto
        self._height = auto
        self._r_width = 0
        self._r_height = 0

    def paint_on(self, buf: buffer):
        if self._layout_changed:
            self.cache_layout()
        render_width = self.render_width
        render_height = self.render_height
        if render_width == 0 or render_height == 0:
            return
        with StringIO() as s:
            words = deque(self.words())
            theme = self.theme
            utils.repeatIO(s, ' ', self.left_margin)
            horizontal_lineIO(s, render_width, theme.left_top, theme.right_top, theme.horizontal)
            if render_height == 1:
                buf.addtext(s.getvalue(), end='')
                return
            if render_height == 2:
                utils.repeatIO(s, ' ', self.left_margin)
                horizontal_lineIO(s, render_width, theme.left_bottom, theme.right_bottom, theme.horizontal)
                buf.addtext(s.getvalue(), end='')
                return

            cur_pos = 0
            text_area_width = render_width - 2
            s.write('\n')

            def write_word(word: Word) -> bool:
                nonlocal cur_pos
                word_len = len(word)
                rest_len = text_area_width - cur_pos
                if rest_len >= word_len:
                    self._render_charsIO(s, word)
                    cur_pos += word_len
                    return True
                else:
                    utils.repeatIO(s, ' ', rest_len)
                    cur_pos += rest_len
                    return False

            while len(words) > 0:
                cur = words.popleft()
                if cur_pos == text_area_width:
                    s.write(theme.vertical)
                    s.write('\n')
                    cur_pos = 0
                if cur_pos == 0:
                    utils.repeatIO(s, ' ', self.left_margin)
                    s.write(theme.vertical)
                used = write_word(cur)
                if not used:
                    words.appendleft(cur)

            rest_len = text_area_width - cur_pos
            utils.repeatIO(s, ' ', rest_len)
            s.write(theme.vertical)

            s.write('\n')
            utils.repeatIO(s, ' ', self.left_margin)
            horizontal_lineIO(s, render_width, theme.left_bottom, theme.right_bottom, theme.horizontal)

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
        sum_len = 0
        max_width = 0
        for word in self.words():
            word_len = len(word)
            sum_len += word_len
            max_width = max(max_width, word_len)
        a = math.sqrt(sum_len) / 7

        if self.width == auto:
            self._r_width = max(round(a * 30), 2 + max_width)
        else:
            self._r_width = max(self.width, 2 + max_width)

        if self.height == auto:
            self._r_height = round(a * 11)
        else:
            self._r_height = self.height
