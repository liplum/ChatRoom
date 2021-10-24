from ui.inputs import i_nbinput
from ui.outputs import i_display, CmdColor
import msvcrt
from threading import Thread, RLock
from utils import lock
from typing import Optional, List
import chars


class nbdispaly(i_display):

    def display_text(self, text: str = "", end: str = "", color: CmdColor = None):
        msvcrt.putwch(text + end)


class nbinput(i_nbinput):
    """
    non-blocking input
    """

    def start_listen(self):
        if self.input_thread is None:
            self.input_thread = Thread(target=self._listen_input)
            self.input_thread.start()
            self._lock = RLock()

    def __init__(self):
        super().__init__()
        self.input_thread = None

    def _listen_input(self):
        while True:
            if msvcrt.kbhit():
                ch = msvcrt.getwch()
                ch_number = ord(ch)
                if ch_number == chars.control_keycode_1:
                    ch_full = chars.control(ord(msvcrt.getwch()))
                    self._input_new(ch_full)
                elif ch_number == f_keycode_1:
                    ch_full = chars.f(ord(msvcrt.getwch()))
                    self._input_new(ch_full)
                else:
                    ch_full = chars.char(ch_number)
                    self._input_new(ch_full)

    def _input_new(self, char: chars.char):
        lock(self._lock, lambda: self._input_list.append(c))
        self.on_input(self, char)

    def consume_char(self) -> Optional[chars.char]:
        def get_first() -> Optional[chars.char]:
            if len(self._input_list) == 0:
                return None
            first = self._input_list.pop(0)
            return first

        return lock(self._lock, get_first)

    def get_input(self, tip: str = None):
        self.start_listen()

    @property
    def input_list(self) -> List[chars.char]:
        return lock(self._lock, self.__get_input_list)

    def __get_input_list(self) -> List[chars.char]:
        return super().input_list
