from io import StringIO

import numpy as np

from ui.Renders import *


class CmdCanvas(Canvas):

    def __init__(self, width: int, height: int, buffer: Buffer):
        super().__init__()
        self.__width = width
        self.__height = height
        self.buffer: Buffer = buffer

    def Char(self, x: int, y: int, char: str):
        if 0 <= x < self.Width and 0 <= y < self.Height:
            self.buffer[y, x] = char

    def Str(self, x: int, y: int, string: str):
        width = self.Width
        height = self.Height
        buffer = self.buffer
        for i, char in enumerate(string):
            nx = x + i
            if 0 <= nx < width and 0 <= y < height:
                buffer[y, nx] = char

    def Color(self, x: int, y: int, bk, fg):
        pass

    def Colors(self, x1: int, x2: int, y: int, bk, fg):
        pass

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

    @property
    def Width(self):
        return self.__width

    @property
    def Height(self):
        return self.__height


class CmdRender(IRender):

    def __init__(self):
        super().__init__()
        self.CharMatrix: Optional[Buffer] = None
        self.NeedRegen = True
        self.Width: int = 0
        self.Height: int = 0

    def InitRender(self):
        pass

    def OnResized(self):
        if CanGetTerminalScreenSize():
            self.NeedRegen = True

    def CreateCanvas(self) -> CmdCanvas:
        if self.NeedRegen:
            self.RegenBuffer()
        return CmdCanvas(self.Width, self.Height, self.CharMatrix)

    def RegenBuffer(self):
        if CanGetTerminalScreenSize():
            self.Width, self.Height = GetTerminalScreenSize()
        else:
            self.Width, self.Height = 120, 20
        size = self.Height, self.Width
        if self.CharMatrix is None or self.CharMatrix.shape != size:
            self.CharMatrix = np.full(size, " ", dtype=str)
        self.NeedRegen = False

    def Render(self, canvas: Canvas):
        if isinstance(canvas, CmdCanvas):
            cm = canvas.buffer
            height = min(self.Height, canvas.Height)
            with StringIO() as o:
                for i in range(height):
                    line = Iterate2DRow(cm, i)
                    for ch in line:
                        o.write(ch)
                    o.write('\n')
                try:
                    output = o.getvalue()
                    print(output, end="\n")
                except:
                    pass

    def Dispose(self):
        pass


class CmdColoredCanvas(Canvas):

    def __init__(self, width: int, height: int, buffer: Buffer):
        super().__init__()
        self.__width = width
        self.__height = height
        self.buffer: Buffer = buffer
        self.colors: Buffer = colors

    def Char(self, x: int, y: int, char: str):
        if 0 <= x < self.Width and 0 <= y < self.Height:
            self.buffer[y, x] = char

    def Str(self, x: int, y: int, string: str):
        width = self.Width
        height = self.Height
        buffer = self.buffer
        for i, char in enumerate(string):
            nx = x + i
            if 0 <= nx < width and 0 <= y < height:
                buffer[y, nx] = char

    def Color(self, x: int, y: int, bk, fg):
        if 0 <= x < self.Width and 0 <= y < self.Height:
            self.colors[y, x] = bk | fg

    def Colors(self, x1: int, x2: int, y: int, bk, fg):
        width = self.Width
        height = self.Height
        colors = self.colors
        color = bk | fg
        for i, char in enumerate(string):
            nx = x + i
            if 0 <= nx < width and 0 <= y < height:
                colors[y, nx] = color

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

    @property
    def Width(self):
        return self.__width

    @property
    def Height(self):
        return self.__height


class CmdColoredRender(IRender):

    def __init__(self):
        super().__init__()
        self.CharMatrix: Optional[Buffer] = None
        self.NeedRegen = True
        self.Width: int = 0
        self.Height: int = 0

    def InitRender(self):
        pass

    def OnResized(self):
        if CanGetTerminalScreenSize():
            self.NeedRegen = True

    def CreateCanvas(self) -> CmdColoredCanvas:
        if self.NeedRegen:
            self.RegenBuffer()
        return CmdColoredCanvas(self.Width, self.Height, self.CharMatrix)

    def RegenBuffer(self):
        if CanGetTerminalScreenSize():
            self.Width, self.Height = GetTerminalScreenSize()
        else:
            self.Width, self.Height = 120, 20
        size = self.Height, self.Width
        if self.CharMatrix is None or self.CharMatrix.shape != size:
            self.CharMatrix = np.full(size, " ", dtype=str)
        self.NeedRegen = False

    def Render(self, canvas: Canvas):
        if isinstance(canvas, CmdColoredCanvas):
            cm = canvas.buffer
            height = min(self.Height, canvas.Height)
            with StringIO() as o:
                for i in range(height):
                    line = Iterate2DRow(cm, i)
                    for ch in line:
                        o.write(ch)
                    o.write('\n')
                try:
                    output = o.getvalue()
                    print(output, end="\n")
                except:
                    pass

    def Dispose(self):
        pass
