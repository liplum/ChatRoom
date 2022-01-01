import numpy as np
import win32con
import win32console
from win32console import PyConsoleScreenBufferType, PyCOORDType

import utils
from ui.Renders import *

XY = PyCOORDType
CSBuffer = PyConsoleScreenBufferType

"""
|---x--------->
| 0 1 2 3 4 5 6
y 1 2 3 4 5 6 7
| 2 3 4 5 6 7 8
v 3 4 5 6 7 8 9
"""


class WinCanvas(Canvas):

    def __init__(self, width: int, height: int, buffer: Buffer, colors: Buffer, dirty_marks: DirtyMarks):
        self.__width = width
        self.__height = height
        self.buffer: Buffer = buffer
        self.colors: Buffer = colors
        self.DirtyMarks: DirtyMarks = dirty_marks

    @property
    def Width(self):
        return self.__width

    @property
    def Height(self):
        return self.__height

    def Char(self, x, y, char: str):
        if 0 <= x < self.Width and 0 <= y < self.Height:
            self.buffer[y, x] = char
            self.DirtyMarks[y] = True

    def Str(self, x, y, string: Iterable[str]):
        width = self.Width
        height = self.Height
        buffer = self.buffer
        marks = self.DirtyMarks
        for i, char in enumerate(string):
            nx = x + i
            if 0 <= nx < width and 0 <= y < height:
                buffer[y, nx] = char
        if 0 <= y < height:
            marks[y] = True

    def Color(self, x: int, y: int, bk, fg):
        if 0 <= x < self.Width and 0 <= y < self.Height:
            self.colors[y, x] = bk | fg
            self.DirtyMarks[y] = True

    def Colors(self, x1: int, x2: int, y: int, bk, fg):
        width = self.Width
        height = self.Height
        colors = self.colors
        marks = self.DirtyMarks
        for i, char in enumerate(string):
            nx = x + i
            if 0 <= nx < width and 0 <= y < height:
                colors[y, nx] = bk | fg
        if 0 <= y < height:
            marks[y] = True

    def Clear(self, x: int, y: int):
        NoColor = BK.Black | FG.White
        if 0 <= x < self.Width and 0 <= y < self.Height:
            self.buffer[y, x] = " "
            self.colors[y, x] = NoColor
            self.DirtyMarks[y] = True

    def ClearAll(self):
        width = self.Width
        height = self.Height
        buffer = self.buffer
        marks = self.DirtyMarks
        colors = self.colors
        NoColor = BK.Black | FG.White
        for j in range(height):
            for i in range(width):
                buffer[j, i] = " "
                colors[j, i] = NoColor
            marks[j] = True

    def ClearArea(self, x1: int, y1: int, x2: int, y2: int):
        x1 = max(x1, 0)
        y1 = max(y1, 0)
        x2 = min(x2, self.Width)
        y2 = min(y2, self.Height)
        buffer = self.buffer
        marks = self.DirtyMarks
        colors = self.colors
        NoColor = BK.Black | FG.White
        for j in range(y1, y2):
            for i in range(x1, x2):
                buffer[j, i] = " "
                colors[j, i] = NoColor
            marks[j] = True


class WinRender(IRender):

    def __init__(self):
        super().__init__()
        self.CharMatrix: Optional[Buffer] = None
        self.ColorMatrix: Optional[Buffer] = None
        self.DirtyMarks: Optional[DirtyMarks] = None
        self.buffer: Optional[CSBuffer] = None
        self.width: int = 0
        self.height: int = 0
        self.NeedRegen = True

    def Initialize(self):
        pass

    def RegenBuffer(self):
        self.buffer = win32console.CreateConsoleScreenBuffer(
            DesiredAccess=win32con.GENERIC_READ | win32con.GENERIC_WRITE,
            ShareMode=0, SecurityAttributes=None, Flags=1)
        buf = self.buffer
        buf.SetConsoleActiveScreenBuffer()
        info = buf.GetConsoleScreenBufferInfo()
        size = info["Size"]
        self.width = size.X
        self.height = size.Y
        size = self.height, self.width
        heights = self.height,
        if self.CharMatrix is None or self.CharMatrix.shape != size:
            self.CharMatrix = np.full(size, " ", dtype=str)
        if self.ColorMatrix is None or self.ColorMatrix.shape != size:
            self.ColorMatrix = np.full(size, BK.Black | FG.White, dtype=int)
        if self.DirtyMarks is None or self.DirtyMarks.shape != heights:
            self.DirtyMarks = np.full(heights, False, dtype=bool)
        self.NeedRegen = False

    def OnResized(self):
        self.NeedRegen = True

    def CreateCanvas(self) -> WinCanvas:
        if self.NeedRegen:
            self.RegenBuffer()
        return WinCanvas(self.width, self.height, self.CharMatrix, self.ColorMatrix, self.DirtyMarks)

    def Render(self, canvas: Canvas):
        if isinstance(canvas, WinCanvas):
            cm = canvas.buffer
            colorm = canvas.colors
            buf = self.buffer
            dm = canvas.DirtyMarks
            for i, dirty in enumerate(dm):
                if dirty:
                    line = utils.chain(Iterate2DRow(cm, i))
                    buf.WriteConsoleOutputCharacter(
                        line, XY(0, i)
                    )
                    colors = Iterate2DRow(colorm, i)
                    buf.WriteConsoleOutputAttribute(
                        colors, XY(0, i)
                    )
                    dm[i] = False

    def Dispose(self):
        pass
