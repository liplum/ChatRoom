import sys
import termios
import tty
from threading import Thread, RLock
from typing import List

from linuxchars import *
from ui.inputs import inbinput

class nbinput(inbinput):
    """
    non-blocking input on linux
    """

    def __init__(self):
        super().__init__()
        self.input_thread = None
        self._lock = RLock()
        self.old_settings = termios.tcgetattr(sys.stdin)

    def initialize(self):
        if self.input_thread is None:
            self.input_thread = Thread(target=self._listen_input,name="Input")
            self.input_thread.daemon = True
            self.input_thread.start()
            self._lock = RLock()

    def get_input(self, tip: str = None):
        self.initialize()

    def _listen_input(self):
        try:
            tty.setcbreak(sys.stdin.fileno())
            while True:
                cs = []
                if sys.stdin.readable():
                    c1: str = sys.stdin.read(1)
                    nc1 = ord(c1)
                    cs.append(nc1)
                    if nc1 == linux_esc:
                        c2: str = sys.stdin.read(1)
                        nc2 = ord(c2)
                        cs.append(nc2)
                        if nc2 == linux_csi:
                            c3: str = sys.stdin.read(1)
                            nc3 = ord(c3)
                            cs.append(nc3)
                        elif nc2 == linux_o:
                            c3: str = sys.stdin.read(1)
                            nc3 = ord(c3)
                            cs.append(nc3)

                    l = len(cs)
                    if l == 1:
                        self._input_new(char(cs[0]))
                    elif l > 1:
                        self._input_new(lc.from_tuple(cs))
        except:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

    def __del__(self):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

    def consume_char(self) -> Optional[char]:
        with self._lock:
            if len(self._input_list) == 0:
                return None
            first = self._input_list.popleft()
            return first

    def _input_new(self, char: char):
        with self._lock:
            self._input_list.append(char)
            self.on_input(self, char)

    @property
    def input_list(self) -> List[char]:
        with self._lock:
            return list(self._input_list)
