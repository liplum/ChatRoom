import os
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

from abc import ABC, abstractmethod


class Canvas:
    @abstractmethod
    def Char(self, x: int, y: int, char: str):
        pass

    @abstractmethod
    def Str(self, x: int, y: int, string: Iterable[str]):
        pass

    @abstractmethod
    def Color(self, x: int, y: int, color):
        pass

    @abstractmethod
    def Colors(self, x1: int, x2: int, y1: int, y2: int, color):
        pass

    @property
    @abstractmethod
    def Width(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def Height(self):
        raise NotImplementedError()


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

    def __init__(self):
        self.X = 0
        self.Y = 0
        self._width = 0
        self._height = 0
        self.canvas: Optional[Canvas] = None

    def Bind(self, canvas: Canvas):
        self.canvas = canvas

    def Char(self, x: int, y: int, char: str):
        canvas = self.canvas
        if canvas and 0 <= x < self.Width and 0 <= y < self.Height:
            canvas.Char(self.X + x, self.Y + y, char)

    def Str(self, x: int, y: int, string: str):
        canvas = self.canvas
        if canvas and 0 <= x < self.Width and 0 <= y < self.Height:
            rest = self.Width - x
            if len(string) > rest:
                string = string[0:rest]
            canvas.Str(self.X + x, self.Y + y, string)

    def Color(self, x: int, y: int, color):
        pass

    def Colors(self, x1: int, x2: int, y1: int, y2: int, color):
        pass

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
