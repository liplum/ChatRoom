from ui.input import i_nbinput
from ui.output import i_display, CmdColor
import msvcrt
from threading import Thread, RLock
from utils import lock
from typing import Union, Optional


def is_key(char: Union[str, bytes, bytearray], key: Union[str, bytes]):
    if isinstance(char, str):
        b = char.encode()
    elif isinstance(char, bytes):
        b = char
    elif isinstance(char, bytearray):
        b = bytes(bytearray)
    else:
        return False

    if isinstance(key, bytes):
        k = key
    elif isinstance(key, str):
        k = key.encode()
    return b == k


class nbdispaly(i_display):

    def display_text(self, text: str = "", end: str = "", color: CmdColor = None):
        msvcrt.putwch(text + end)


class nbinput(i_nbinput):
    """
    non-blocking input
    """

    def __init__(self):
        super().__init__()
        self.input_thread = None

    def _listen_input(self):
        while True:
            if msvcrt.kbhit():
                c_b: bytes = msvcrt.getwch()
                c = c_b.decode()
                lock(self._lock, lambda: self._input_list.append(c))

    def get_input(self, tip: str = None):
        if self.input_thread is None:
            self.input_thread = Thread(target=self._listen_input)
            self.input_thread.start()
            self._lock = RLock()

    def get_input_list(self) -> list:
        return lock(self._lock, self.__get_input_list)

    def __get_input_list(self) -> list:
        return super().get_input_list()
