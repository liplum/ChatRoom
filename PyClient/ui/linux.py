import sys
import termios
import tty
from threading import RLock
from typing import List

from select import select

from core.utils import lock
from linuxchars import *
from ui.inputs import i_nbinput


class nbinput(i_nbinput):
    """
    non-blocking input on linux
    """

    def __init__(self):
        super().__init__()
        self.input_thread = None
        self._lock = RLock()

    def get_input(self, tip: str = None):
        try:
            tty.setcbreak(sys.stdin.fileno())
            rs, ws, xs = select(self.rlist, self.wlist, self.xlist)
            for r in rs:
                if r is sys.stdin:
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
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

    def __del__(self):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

    def consume_char(self) -> Optional[char]:
        def get_first() -> Optional[char]:
            if len(self._input_list) == 0:
                return None
            first = self._input_list.pop(0)
            return first

        return lock(self._lock, get_first)

    def initialize(self):
        self.rlist = [sys.stdin]
        self.wlist = []
        self.xlist = []
        self.old_settings = termios.tcgetattr(sys.stdin)

    def _input_new(self, char: char):
        lock(self._lock, lambda: self._input_list.append(char))
        self.on_input(self, char)

    @property
    def input_list(self) -> List[char]:
        return lock(self._lock, self.__get_input_list)

    def __get_input_list(self) -> List[char]:
        return super().input_list
