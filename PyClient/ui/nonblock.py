from ui.input import i_input
from ui.output import i_display, CmdColor
import msvcrt
from threading import Thread, RLock
from utils import lock


def is_key(str_or_bytes, key: bytes):
    if isinstance(str_or_bytes, str):
        b = str_or_bytes.encode()
    elif isinstance(str_or_bytes, bytes):
        b = str_or_bytes
    elif isinstance(str_or_bytes, bytearray):
        b = bytes(bytearray)
    else:
        return False
    return b == key


class nbdispaly(i_display):

    def display_text(self, text: str = "", end: str = "", color: CmdColor = None):
        msvcrt.putwch(text + end)


class nbinput(i_input):
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
