from abc import ABC, abstractmethod
from typing import Tuple, Callable,Union

builtin_themes = set()

ThemeTuple = Tuple[str, str, str, str, str, str]


class theme:
    def __init__(self, left_top: str, right_top: str, left_bottom: str, right_bottom: str, horizontal: str,
                 vertical: str):
        self.left_top: str = left_top
        self.right_top: str = right_top
        self.left_bottom: str = left_bottom
        self.right_bottom: str = right_bottom
        self.horizontal: str = horizontal
        self.vertical: str = vertical

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


theme_getter = Callable[[], theme]
ThemeGetter = Union[theme_getter,theme]

def _builtin(left_top: str, right_top: str, left_bottom: str, right_bottom: str, horizontal: str,
             vertical: str) -> theme:
    t = theme(left_top, right_top, left_bottom, right_bottom, horizontal, vertical)
    builtin_themes.add(t)
    return t

def is_theme(obj):
    return isinstance(obj,theme) or isinstance(obj,packed_theme)

vanilla: theme = _builtin('┌', '┐', '└', '┘', '─', '│')
tube: theme = _builtin('╔', '╗', '╚', '╝', '═', '║')
rounded_rectangle: theme = _builtin('╭', '╮', '╰', '╯', '─', '│')


class packed_theme(ABC):

    def __init__(self, left_top: str, right_top: str, left_bottom: str, right_bottom: str, horizontal: str,
                 vertical: str):
        self._left_top = left_top
        self._right_top = right_top
        self._left_bottom = left_bottom
        self._right_bottom = right_bottom
        self._horizontal = horizontal
        self._vertical = vertical

    @property
    @abstractmethod
    def left_top(self) -> str:
        pass

    @property
    @abstractmethod
    def right_top(self) -> str:
        pass

    @property
    @abstractmethod
    def left_bottom(self) -> str:
        pass

    @property
    @abstractmethod
    def right_bottom(self) -> str:
        pass

    @property
    @abstractmethod
    def horizontal(self) -> str:
        pass

    @property
    @abstractmethod
    def vertical(self) -> str:
        pass


def copy_packed_theme(original: theme, theme_type: type, *args, **kwargs):
    return theme_type(original.left_top, original.right_top, original.left_bottom, original.right_bottom,
                      original.horizontal, original.vertical, *args, **kwargs)


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
