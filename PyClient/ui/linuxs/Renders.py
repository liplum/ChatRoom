import curses
from curses import window

import numpy as np

import utils
from ui.Renders import *

"""
|---x--------->
| 0 1 2 3 4 5 6
y 1 2 3 4 5 6 7
| 2 3 4 5 6 7 8
v 3 4 5 6 7 8 9
"""


class LinuxCanvas(Canvas):

    def __init__(self, width: int, height: int, buffer: Buffer):
        self.__width = width
        self.__height = height
        self.buffer: Buffer = buffer

    @property
    def Width(self):
        return self.__width

    @property
    def Height(self):
        return self.__height

    def Char(self, x, y, char: str):
        if 0 <= x < self.Width and 0 <= y < self.Height:
            self.buffer[y, x] = char

    def Str(self, x, y, string: Iterable[str]):
        width = self.Width
        height = self.Height
        buffer = self.buffer
        for i, char in enumerate(string):
            nx = x + i
            if 0 <= nx < width and 0 <= y < height:
                buffer[y, nx] = char

    def Clear(self, x: int, y: int):
        if 0 <= x < self.Width and 0 <= y < self.Height:
            self.buffer[y, x] = " "

    def ClearArea(self, x1: int, y1: int, x2: int, y2: int):
        x1 = max(x1, 0)
        y1 = max(y1, 0)
        x2 = min(x2, self.Width)
        y2 = min(y2, self.Height)
        buffer = self.buffer
        for j in range(y1, y2):
            for i in range(x1, x2):
                buffer[j, i] = " "

    def ClearAll(self):
        width = self.Width
        height = self.Height
        buffer = self.buffer
        for j in range(height):
            for i in range(width):
                buffer[j, i] = " "

    def Color(self, x: int, y: int, bk, fg):
        pass

    def Colors(self, x1: int, x2: int, y: int, bk, fg):
        pass


class LinuxRender(IRender):

    def __init__(self):
        self.CharMatrix: Optional[ndarray] = None
        self.Screen: Optional[window] = None
        self.NeedRegen = True
        self.Width: int = 0
        self.Height: int = 0

    def RegenScreen(self):
        scr = curses.initscr()
        self.Screen = scr
        curses.noecho()
        curses.cbreak()
        scr.keypad(True)
        scr.nodelay(True)
        scr.clear()
        size = GetTerminalScreenSize()
        print(size)
        self.Width = size.columns
        self.Height = size.lines
        size = self.Height, self.Width
        if not self.CharMatrix or self.CharMatrix.shape != size:
            self.CharMatrix = np.full(size, " ", dtype=str)
        self.NeedRegen = False

    def OnResized(self):
        self.NeedRegen = True

    def Initialize(self):
        pass

    def CreateCanvas(self) -> LinuxCanvas:
        if self.NeedRegen:
            self.RegenScreen()
        return LinuxCanvas(self.Width, self.Height, self.CharMatrix)

    def Render(self, canvas: Canvas):
        if isinstance(canvas, LinuxCanvas):
            cm = self.CharMatrix
            screen = self.Screen
            for i in range(self.Height):
                line = utils.chain(Iterate2DRow(cm, i))
                try:
                    screen.addstr(i, 0, line)
                except:
                    pass
            screen.refresh()

    def Dispose(self):
        curses.endwin()
