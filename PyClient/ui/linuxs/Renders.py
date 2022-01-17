import curses
from curses import window, color_pair
from threading import Thread, RLock

import numpy as np

import chars
import utils
from ui.Renders import *
from ui.inputs import inbinput

"""
|---x--------->
| 0 1 2 3 4 5 6
y 1 2 3 4 5 6 7
| 2 3 4 5 6 7 8
v 3 4 5 6 7 8 9
"""


def ToColorPair(bk, fg):
    return bk | (fg << 3)


_ColorPairsInited = False


def ColorPairsInited() -> bool:
    return _ColorPairsInited


def SetColorPairsInited(v: bool):
    _ColorPairsInited = v


def InitColorPairs():
    for fg in FG.AllColors:
        for bk in BK.AllColors:
            pairID = ToColorPair(bk, fg)
            if pairID == 0:
                continue
            curses.init_pair(pairID, fg, bk)


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


class LinuxRender(IRender, inbinput):

    def __init__(self):
        super().__init__()
        self.CharMatrix: Optional[Buffer] = None
        self.Screen: Optional[window] = None
        self.NeedRegen = True
        self.Width: int = 0
        self.Height: int = 0
        self._inputThread = None

    def InitInput(self):
        if self._inputThread is None:
            self._inputThread = Thread(target=self._ListenInput, name="Input")
            self._inputThread.daemon = True
            self._inputThread.start()
            self._lock = RLock()

    def init(self, container):
        self.logger: "ilogger" = container.resolve("ilogger")

    def _GetCurScreen(self)->window:
        return self.Screen

    def _ListenInput(self):
        try:
            while True:
                scr = self._GetCurScreen()
                self.logger.msg(f"{scr=}")
                if scr is not None:
                    self.logger.msg("Get begins")
                    ch = scr.get_wch()
                    self.logger.msg("Get ends")
                    self.logger.msg(ch)
                    self.InputNew(chars.printable(ch))
        except Exception as e:
            self.logger.error(e)

    def InputNew(self, char: chars.char):
        with self._lock:
            self._input_list.append(char)
            self.on_input(self, char)

    def RegenScreen(self):
        scr = self.Screen
        curses.noecho()
        curses.cbreak()
        scr.keypad(True)
        scr.nodelay(True)
        scr.clear()
        size = GetTerminalScreenSize()
        self.Width = size.columns
        self.Height = size.lines
        size = self.Height, self.Width
        if not self.CharMatrix or self.CharMatrix.shape != size:
            self.CharMatrix = np.full(size, " ", dtype=str)
        self.NeedRegen = False

    def OnResized(self):
        self.NeedRegen = True

    def InitRender(self):
        self.Screen = curses.initscr()
        self.logger.msg(f"{self.Screen=}")

    def CreateCanvas(self) -> LinuxCanvas:
        if self.NeedRegen:
            self.RegenScreen()
        return LinuxCanvas(self.Width, self.Height, self.CharMatrix)

    def Render(self, canvas: Canvas):
        if isinstance(canvas, LinuxCanvas):
            cm = canvas.buffer
            screen = self.Screen
            height = min(self.Height, canvas.Height)
            for i in range(height):
                line = utils.chain(Iterate2DRow(cm, i))
                try:
                    screen.addstr(i, 0, line)
                except:
                    pass
            screen.refresh()

    def Dispose(self):
        curses.endwin()

    @property
    def is_end(self):
        return True


class LinuxColoredCanvas(LinuxCanvas):
    def __init__(self, width: int, height: int, buffer: Buffer, colors: Buffer):
        super().__init__(width, height, buffer)
        self.colors: Buffer = colors

    def Clear(self, x: int, y: int):
        NoColor = ToColorPair(BK.Black, FG.White)
        if 0 <= x < self.Width and 0 <= y < self.Height:
            self.buffer[y, x] = " "
            self.colors[y, x] = NoColor

    def ClearArea(self, x1: int, y1: int, x2: int, y2: int):
        x1 = max(x1, 0)
        y1 = max(y1, 0)
        x2 = min(x2, self.Width)
        y2 = min(y2, self.Height)
        buffer = self.buffer
        NoColor = ToColorPair(BK.Black, FG.White)
        for j in range(y1, y2):
            for i in range(x1, x2):
                buffer[j, i] = " "
                colors[j, i] = NoColor

    def ClearAll(self):
        width = self.Width
        height = self.Height
        buffer = self.buffer
        colors = self.colors
        NoColor = ToColorPair(BK.Black, FG.White)
        for j in range(height):
            for i in range(width):
                buffer[j, i] = " "
                colors[j, i] = NoColor

    def Color(self, x: int, y: int, bk, fg):
        if 0 <= x < self.Width and 0 <= y < self.Height:
            self.colors[y, x] = ToColorPair(bk, fg)

    def Colors(self, x1: int, x2: int, y: int, bk, fg):
        width = self.Width
        height = self.Height
        colors = self.colors
        color = ToColorPair(bk, fg)
        for i, char in enumerate(string):
            nx = x + i
            if 0 <= nx < width and 0 <= y < height:
                colors[y, nx] = color


class LinuxColoredRender(LinuxRender):

    def __init__(self):
        super().__init__()
        self.ColorMatrix: Optional[Buffer] = None

    def RegenScreen(self):
        super().RegenScreen()
        if not self.ColorMatrix or self.ColorMatrix.shape != size:
            self.ColorMatrix = np.full((self.Height, self.Width), ToColorPair(BK.Black, FG.White), dtype=int)

    def CreateCanvas(self) -> LinuxColoredCanvas:
        if self.NeedRegen:
            self.RegenScreen()
        return LinuxColoredCanvas(self.Width, self.Height, self.CharMatrix, self.ColorMatrix)

    def InitRender(self):
        super().InitRender()
        curses.start_color()
        if not ColorPairsInited():
            InitColorPairs()
            SetColorPairsInited(True)

    def Render(self, canvas: Canvas):
        if isinstance(canvas, LinuxColoredCanvas):
            cm = canvas.buffer
            cc = canvas.colors
            screen = self.Screen
            height = min(self.Height, canvas.Height)
            width = min(self.Width, canvas.Width)
            for i in range(height):
                for j in range(width):
                    try:
                        screen.addstr(i, j, cm[i, j], color_pair(cc[i, j]))
                    except:
                        pass
            screen.refresh()
