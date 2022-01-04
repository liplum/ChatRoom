import os
from abc import ABC, abstractmethod
from typing import Iterable, Tuple, Optional

from numpy import ndarray

Buffer = ndarray


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
    def Str(self, x: int, y: int, string: str):
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


def WidthHeight(canvas: Canvas) -> Tuple[int, int]:
    return canvas.Width, canvas.Height


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


"""
      [0]   [1]   [2]   [3]   [4]
[0]    A     n           a     p
[1]    p     l     e           a
[2]          d     a     y          
[3]    ,     k     e     e     p      
[4]          t     h     e               
[5]    d     o     c     t     o          
[6]    r           a     w     a     
[7]    y     .
"""


class StrWriter:

    def __init__(self, canvas: Canvas, x: int = 0, y: int = 0, width: int = None, height: int = None, autoWrap=False):
        """X in canvas"""
        self.X = max(x, 0)
        """Y in canvas"""
        self.Y = max(y, 0)
        self.Width = width or canvas.Width
        self.Height = height or canvas.Height
        self.xi = 0
        self.yi = 0
        self.canvas: Canvas = canvas
        self.AutoWrap = autoWrap

    def NextLine(self):
        self.xi = 0
        self.yi += 1

    def Write(self, text: str, bk=None, fg=None):
        if len(text) <= 0:
            return
        width = self.Width
        height = self.Height
        if width == 0 or height == 0:
            return
        x = self.X
        y = self.Y
        xi = self.xi
        yi = self.yi
        if bk is None:
            bk = BK.Black
        if fg is None:
            fg = FG.White
        if xi >= width and yi >= height:
            return
        canvas = self.canvas
        autoWrap = self.AutoWrap
        for ch in text:
            if xi >= width:
                if autoWrap:
                    xi = 0
                    yi += 1
                else:
                    break
            if yi >= height:
                break
            canvas.Char(xi + x, yi + y, ch)
            canvas.Color(xi + x, yi + y, bk, fg)
            xi += 1
        self.xi = xi
        self.yi = yi


class DotPainter:
    def __init__(self, canvas: Canvas, bk=None, fg=None):
        self._bk = bk
        self._fg = fg
        self.canvas = canvas

    @property
    def BK(self):
        return self._bk

    @BK.setter
    def BK(self, value):
        self._bk = value

    @property
    def FG(self):
        return self._bk

    @FG.setter
    def FG(self, value):
        self._bk = value

    def Char(self, x: int, y: int, char: Optional[str], useBoundColor=True, bk=None, fg=None):
        if useBoundColor:
            bk = self.BK
            fg = self.FG

        if char is not None:
            if bk is None:
                bk = BK.Black
            if fg is None:
                fg = FG.White
            self.canvas.Char(x, y, char)
        if not (fg is None or bk is None):
            self.canvas.Color(x, y, bk, fg)

    def Str(self, x: int, y: int, string: str, useBoundColor=True, bk=None, fg=None):
        if useBoundColor:
            bk = self.BK
            fg = self.FG
        if bk is None:
            bk = BK.Black
        if fg is None:
            fg = FG.White

        if char is not None:
            if bk is None:
                bk = BK.Black
            if fg is None:
                fg = FG.White
            self.canvas.Str(x, y, string)
        if not (fg is None or bk is None):
            self.canvas.Colors(x, x + len(string), y, bk, fg)
