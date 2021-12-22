import os
from typing import Tuple


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
    def Char(self, x, y, char: str):
        pass

    def Str(self, x, y, string: str):
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
