import os

from typing import Tuple


def GetTerminalScreenSize() -> Tuple[int, int]:
    return os.get_terminal_size()


try:
    os.get_terminal_size()
    _canGetTerminalScreenSize = True
except:
    _canGetTerminalScreenSize = False


def CanGetTerminalScreenSize() -> bool:
    return _canGetTerminalScreenSize
