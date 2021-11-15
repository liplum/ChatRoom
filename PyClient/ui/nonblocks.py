import msvcrt
import sys
from threading import Thread, RLock
from typing import Optional, List, NoReturn

import chars
from ui.clients import client
from ui.inputs import i_nbinput
from ui.outputs import i_display, CmdFgColor, CmdBkColor, i_logger, buffer
from utils import lock


class nbdispaly(i_display):

    def gen_buffer(self) -> buffer:
        pass

    def render(self, buf: buffer) -> bool:
        pass

    def display_text(self, text: str = "", end: str = '\n', fgcolor: Optional[CmdFgColor] = None,
                     bkcolor: Optional[CmdBkColor] = None) -> NoReturn:
        msvcrt.putwch(text + end)


class nbinput(i_nbinput):
    """
    non-blocking input on windows
    """

    def __init__(self):
        super().__init__()
        self.input_thread = None

    def initialize(self):
        if self.input_thread is None:
            self.input_thread = Thread(target=self._listen_input)
            self.input_thread.daemon = True
            self.input_thread.start()
            self._lock = RLock()

    def init(self, container):
        self.client: client = container.resolve(client)
        self.logger: i_logger = container.resolve(i_logger)

    def _listen_input(self):
        try:
            while True:
                if msvcrt.kbhit():
                    ch = msvcrt.getwch()
                    ch_number = ord(ch)
                    if ch_number == chars.control_keycode_1:
                        ch_full = chars.control(ord(msvcrt.getwch()))
                        self.input_new(ch_full)
                    elif ch_number == chars.f_keycode_1:
                        ch_full = chars.f(ord(msvcrt.getwch()))
                        self.input_new(ch_full)
                    else:
                        ch_full = chars.char(ch_number)
                        self.input_new(ch_full)
        except Exception as e:
            self.logger.error(f"[Input]{e}\n{sys.exc_info()}")
            self.client.stop()

    def input_new(self, char: chars.char):
        self.client.dlock(self._input_new)(char)

    def _input_new(self, char: chars.char):
        lock(self._lock, lambda: self._input_list.append(char))
        self.on_input(self, char)

    def consume_char(self) -> Optional[chars.char]:
        def get_first() -> Optional[chars.char]:
            if len(self._input_list) == 0:
                return None
            first = self._input_list.pop(0)
            return first

        return lock(self._lock, get_first)

    def get_input(self, tip: str = None):
        self.initialize()

    @property
    def input_list(self) -> List[chars.char]:
        return lock(self._lock, self.__get_input_list)

    def __get_input_list(self) -> List[chars.char]:
        return super().input_list
