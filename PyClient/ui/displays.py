import os
from typing import Iterable
from typing import Tuple

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


class Canvas(ABC):
    @abstractmethod
    def Char(self, x: int, y: int, char: str):
        pass

    @abstractmethod
    def Str(self, x: int, y: int, string: str):
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
