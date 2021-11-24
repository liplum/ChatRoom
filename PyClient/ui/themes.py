from typing import Tuple

builtin_themes = set()

ThemeTuple = Tuple[str, str, str, str, str, str]


class theme:
    def __init__(self, left_top: str, right_top: str, left_bottom: str, right_bottom: str, horizontal: str,
                 vertical: str):
        self.left_top: str = left_top[0]
        self.right_top: str = right_top[0]
        self.left_bottom: str = left_bottom[0]
        self.right_bottom: str = right_bottom[0]
        self.horizontal: str = horizontal[0]
        self.vertical: str = vertical[0]

    def copy(self) -> "theme":
        return theme(self.left_top, self.right_top, self.left_bottom, self.right_bottom, self.horizontal, self.vertical)

    def tuple(self) -> ThemeTuple:
        return self.left_top, self.right_top, self.left_bottom, self.right_bottom, self.horizontal, self.vertical

    @classmethod
    def from_tuple(cls, t: ThemeTuple):
        return theme(t[0], t[1], t[2], t[3], t[4], t[5])

    def __eq__(self, other):
        if isinstance(other, theme):
            return self.tuple() == other.tuple()
        return False

    def __hash__(self):
        return hash(self.tuple())


def _builtin(left_top: str, right_top: str, left_bottom: str, right_bottom: str, horizontal: str,
             vertical: str) -> theme:
    t = theme(left_top, right_top, left_bottom, right_bottom, horizontal, vertical)
    builtin_themes.add(t)
    return t


vanilla: theme = _builtin('┌', '┐', '└', '┘', '─', '│')
tube: theme = _builtin('╔', '╗', '╚', '╝', '═', '║')
rounded_rectangle: theme = _builtin('╭', '╮', '╰', '╯', '─', '│')


class check_theme:
    def __init__(self, checked: str, unchecked: str, null: str):
        self._checked = checked
        self._unchecked = unchecked
        self._null = null

    @property
    def checked(self):
        return self._checked

    @property
    def unchecked(self):
        return self._unchecked

    @property
    def null(self):
        return self._null
