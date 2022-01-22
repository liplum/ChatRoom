import msvcrt
import traceback
from threading import Thread, RLock
from typing import Optional, List

import chars
from ui.Core import IClient
from ui.inputs import inbinput
from ui.outputs import ilogger
from ui import InitKeys


class nbinput(inbinput):
    """
    non-blocking input on wins
    """

    def __init__(self):
        super().__init__()
        self.input_thread = None

    def InitInput(self):
        if self.input_thread is None:
            InitKeys()
            self.input_thread = Thread(target=self._listen_input, name="Input")
            self.input_thread.daemon = True
            self.input_thread.start()
            self._lock = RLock()

    def init(self, container):
        self.client: IClient = container.resolve(IClient)
        self.logger: ilogger = container.resolve(ilogger)

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
            self.logger.error(f"[Input]{e}\n{traceback.format_exc()}")
            self.client.stop()

    def input_new(self, char: chars.char):
        with self._lock:
            self._input_list.append(char)
            self.on_input(self, char)

    def consume_char(self) -> Optional[chars.char]:
        with self._lock:
            if len(self._input_list) == 0:
                return None
            first = self._input_list.popleft()
            return first

    def get_input(self, tip: str = None):
        self.InitInput()

    @property
    def input_list(self) -> List[chars.char]:
        with self._lock:
            return list(self._input_list)

    @property
    def is_end(self):
        return True
