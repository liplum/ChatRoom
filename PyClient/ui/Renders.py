import os
from abc import ABC, abstractmethod
from typing import Iterable, Tuple, Optional

from numpy import ndarray

Buffer = ndarray
DirtyMarks = ndarray


def Iterate2DRow(array2D: ndarray, row_index: int) -> Iterable:
    column = array2D.shape[1]
    for j in range(column):
        yield array2D[row_index, j]


def Iterate2DColumn(array2D: ndarray, column_index: int) -> Iterable:
    row = array2D.shape[0]
    for j in range(row):
        yield array2D[i, column_index]


def get_winsize() -> Tuple[int, int]:
    return os.get_terminal_size()


def get_winsize_default() -> Tuple[int, int]:
    return 180, 30


try:
    os.get_terminal_size()
except:
    get_winsize = get_winsize_default


class BK:
    Red = None
    Green = None
    Blue = None
    Yellow = None
    Violet = None
    White = None
    Black = None
    Cyan = None


class FG:
    Red = None
    Green = None
    Blue = None
    Yellow = None
    Violet = None
    White = None
    Black = None
    Cyan = None


class Canvas:
    @abstractmethod
    def Char(self, x: int, y: int, char: str):
        pass

    @abstractmethod
    def Str(self, x: int, y: int, string: Iterable[str]):
        pass

    @abstractmethod
    def Color(self, x: int, y: int, bk, fg):
        pass

    @abstractmethod
    def Colors(self, x1: int, x2: int, y: int, bk, fg):
        pass

    @abstractmethod
    def Clear(self, x: int, y: int):
        pass

    @abstractmethod
    def ClearArea(self, x1: int, y1: int, x2: int, y2: int):
        pass

    @abstractmethod
    def ClearAll(self):
        pass

    @property
    @abstractmethod
    def Width(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def Height(self):
        raise NotImplementedError()


def ColoredText(canvas: Canvas, text: str, x: int, y: int, bk, fg):
    pass


class IRender(ABC):
    @abstractmethod
    def Initialize(self):
        pass

    @abstractmethod
    def OnResized(self):
        pass

    @abstractmethod
    def CreateCanvas(self) -> Canvas:
        pass

    @abstractmethod
    def Render(self, canvas: Canvas):
        pass

    @abstractmethod
    def Dispose(self):
        pass


class Painter:
    def PaintOn(self, canvas: Canvas):
        pass


class Viewer(Canvas):

    def __init__(self, x=0, y=0, width=0, height=0, canvas: Canvas = None):
        self.X = x
        self.Y = y
        self._width = width
        self._height = height
        self._canvas: Optional[Canvas] = canvas

    @staticmethod
    def ByCanvas(canvas: Canvas):
        return Viewer(0, 0, canvas.Width, canvas.Height, canvas)

    def Bind(self, canvas: Canvas):
        self._canvas = canvas

    def Sub(self, dx, dy, width, height) -> "Viewer":
        return SubViewer(dx, dy, width, height, self)

    def Char(self, x: int, y: int, char: str):
        canvas = self.Canvas
        if canvas and 0 <= x < self.Width and 0 <= y < self.Height:
            canvas.Char(self.X + x, self.Y + y, char)

    def Str(self, x: int, y: int, string: str):
        canvas = self.Canvas
        if canvas and 0 <= x < self.Width and 0 <= y < self.Height:
            rest = self.Width - x
            if len(string) > rest:
                string = string[0:rest]
            canvas.Str(self.X + x, self.Y + y, string)

    def Color(self, x: int, y: int, bk, fg):
        canvas = self.Canvas
        if canvas and 0 <= x < self.Width and 0 <= y < self.Height:
            canvas.Color(self.X + x, self.Y + y, bk, fg)

    def Colors(self, x1: int, x2: int, y: int, bk, fg):
        canvas = self.Canvas
        if canvas and 0 <= x1 < self.Width and 0 <= y < self.Height:
            x1 = self.X + x1
            x2 = self.X + x2
            canvas.Colors(x1, x2, self.Y + y, fg, bk)

    def Clear(self, x: int, y: int):
        canvas = self.Canvas
        if canvas and 0 <= x < self.Width and 0 <= y < self.Height:
            canvas.Clear(self.X + x, self.Y + y)

    def ClearAll(self):
        canvas = self.Canvas
        canvas.ClearArea(self.X, self.Y, self.X + self.Width, self.Y + self.Height)

    def ClearArea(self, x1: int, y1: int, x2: int, y2: int):
        canvas = self.Canvas
        x1 = max(x1, 0)
        y1 = max(y1, 0)
        x2 = min(x2, self.Width)
        y2 = min(y2, self.Height)
        canvas.ClearArea(self.X + x1, self.Y + y1, self.X + x2, self.Y + y2)

    @property
    def Width(self) -> int:
        return self._width

    @Width.setter
    def Width(self, value: int):
        self._width = max(value, 0)

    @property
    def Height(self) -> int:
        return self._height

    @Height.setter
    def Height(self, value: int):
        self._height = max(value, 0)

    @property
    def Canvas(self):
        return self._canvas


class SubViewer(Viewer):
    def __init__(self, x, y, width, height, parent: Viewer):
        super().__init__(x, y, width, height)
        self.parent = parent

    def Bind(self, canvas: Canvas):
        pass

    @property
    def Canvas(self):
        return self.parent.Canvas


class StrWriter:
    def __init__(self, canvas: Canvas, x, y, width, height, autoWrap=False):
        self.X = max(x, 0)
        self.Y = max(y, 0)
        self.Width = width or canvas.Width
        self.Height = height or canvas.Height
        self.xi = 0
        self.yi = 0
        self.canvas: Canvas = canvas
        self.AutoWrap = autoWrap

    def Write(self, text: str, bk=None, fg=None):
        x = self.X
        y = self.Y
        xi = self.xi
        yi = self.yi
        width = self.Width
        height = self.Height
        if bk is None:
            bk = BK.Black
        if fg is None:
            fg = FG.White
        if xi - x >= width and yi - y >= height:
            return
        canvas = self.canvas
        autoWrap = self.AutoWrap
        for ch in text:
            if xi - x >= width:
                if autoWrap:
                    xi = 0
                    yi += 1
                else:
                    break
            if yi - y >= height:
                break
            canvas.Char(xi + x, yi + y, ch)
            canvas.Color(xi + x, yi + y, bk, fg)
            xi += 1
        self.xi = xi
        self.yi = yi
