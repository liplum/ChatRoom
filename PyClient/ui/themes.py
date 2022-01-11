from abc import abstractmethod
from typing import Tuple, Callable, Union

builtin_themes = set()

ThemeTuple = Tuple[str, str, str, str, str, str]


class BorderTheme:
    @property
    @abstractmethod
    def LeftTop(self) -> str:
        pass

    @property
    @abstractmethod
    def RightTop(self) -> str:
        pass

    @property
    @abstractmethod
    def LeftBottom(self) -> str:
        pass

    @property
    @abstractmethod
    def RightBottom(self) -> str:
        pass

    @property
    @abstractmethod
    def Horizontal(self) -> str:
        pass

    @property
    @abstractmethod
    def Vertical(self) -> str:
        pass

    def __eq__(self, other):
        if isinstance(other, BorderTheme):
            return self.Tuple() == other.Tuple()
        return False

    def __hash__(self):
        return hash(self.Tuple())

    Copy: Callable[[], "SimpleBorderTheme"]
    Tuple: Callable[[], ThemeTuple]
    FromTuple: Callable[[ThemeTuple], "SimpleBorderTheme"]


class SimpleBorderTheme(BorderTheme):
    @classmethod
    def FromOther(cls, theme: BorderTheme) -> "SimpleBorderTheme":
        return cls(
            theme.LeftTop, theme.RightTop, theme.LeftBottom, theme.RightBottom,
            theme.Horizontal, theme.Vertical)

    def __init__(self, left_top: str, right_top: str, left_bottom: str, right_bottom: str, horizontal: str,
                 vertical: str):
        self._leftTop: str = left_top
        self._rightTop: str = right_top
        self._leftBottom: str = left_bottom
        self._rightBottom: str = right_bottom
        self._horizontal: str = horizontal
        self._vertical: str = vertical

    @property
    def LeftTop(self) -> str:
        return self._leftTop

    @LeftTop.setter
    def LeftTop(self, value: str):
        self._leftTop = value

    @property
    def RightTop(self) -> str:
        return self._rightTop

    @RightTop.setter
    def RightTop(self, value: str):
        self._rightTop = value

    @property
    def LeftBottom(self) -> str:
        return self._leftBottom

    @LeftBottom.setter
    def LeftBottom(self, value: str):
        self._leftBottom = value

    @property
    def RightBottom(self) -> str:
        return self._rightBottom

    @RightBottom.setter
    def RightBottom(self, value: str):
        self._rightBottom = value

    @property
    def Horizontal(self) -> str:
        return self._horizontal

    @Horizontal.setter
    def Horizontal(self, value: str):
        self._horizontal = value

    @property
    def Vertical(self) -> str:
        return self._vertical

    @Vertical.setter
    def Vertical(self, value: str):
        self._vertical = value


def _borderThemeCopy(self) -> SimpleBorderTheme:
    return SimpleBorderTheme(self.LeftTop, self.RightTop, self.LeftBottom, self.RightBottom, self.Horizontal,
                             self.Vertical)


BorderTheme.Copy = _borderThemeCopy


def _borderThemeTuple(self) -> ThemeTuple:
    return self.LeftTop, self.RightTop, self.LeftBottom, self.RightBottom, self.Horizontal, self.Vertical


BorderTheme.Tuple = _borderThemeTuple


def _borderThemeFromTuple(t: ThemeTuple) -> SimpleBorderTheme:
    return SimpleBorderTheme(t[0], t[1], t[2], t[3], t[4], t[5])


BorderTheme.FromTuple = _borderThemeFromTuple

theme_getter = Callable[[], BorderTheme]
BorderThemeGetter = Union[theme_getter, BorderTheme]


def _builtin(left_top: str, right_top: str, left_bottom: str, right_bottom: str, horizontal: str,
             vertical: str) -> BorderTheme:
    t = SimpleBorderTheme(left_top, right_top, left_bottom, right_bottom, horizontal, vertical)
    builtin_themes.add(t)
    return t


vanilla: BorderTheme = _builtin('┌', '┐', '└', '┘', '─', '│')
tube: BorderTheme = _builtin('╔', '╗', '╚', '╝', '═', '║')
rounded_rectangle: BorderTheme = _builtin('╭', '╮', '╰', '╯', '─', '│')


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


class plus_minus_theme:
    def __init__(self, minus: str, plus: str):
        self._minus = minus[0]
        self._plus = plus[0]

    @property
    def plus(self) -> str:
        return self._plus

    @property
    def minus(self) -> str:
        return self._minus


class password_theme:
    def __init__(self, hidden: str):
        self._hidden = hidden[0]

    @property
    def hidden(self):
        return self._hidden
