from typing import Optional, List
from select import select
import tty
import termios
from chars import char
from utils import lock
from ui.inputs import i_nbinput
from threading import Thread, RLock
import sys
import linuxchars


class nbinput(i_nbinput):
    """
    non-blocking input on linux
    """

    def __init__(self):
        super().__init__()
        self.input_thread = None
        self._lock = RLock()

    def get_input(self, tip: str = None):
        rs, ws, xs = select(self.rlist, self.wlist, self.xlist)
        for r in rs:
            if r is sys.stdin:
                cs = []
                if sys.stdin.readable():
                    c: str = sys.stdin.read(1)
                    cs.append(ord(c))
                    l = len(cs)
                    if l == 1:
                        self._input_new(char(cs[0]))
                    elif l > 1 and cs[1] == linuxchars.linux_esc:
                        self._input_new(linuxchars.from_tuple(cs))

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
        tty.setcbreak(sys.stdin.fileno())

        """ if self.input_thread is not None:
            self.listen_thread = Thread(target=self._listen_input)
            self.listen_thread.daemon = True
            self.listen_thread.start()
            self._lock = RLock()"""

    def _listen_input(self):
        rlist = [sys.stdin]
        wlist = []
        xlist = []
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setcbreak(sys.stdin.fileno())
            while True:
                rs, ws, xs = select(rlist, wlist, xlist)
                for r in rs:
                    if r in sys.stdin:
                        cs = []
                        while sys.stdin.readable():
                            c: str = sys.stdin.read(1)
                            cs.append(ord(c))
                        l = len(cs)
                        if l == 1:
                            self._input_new(char(cs[0]))
                        elif l > 1 and cs[1] == linuxchars.linux_esc:
                            self._input_new(linuxchars.from_tuple(cs))

        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

    def _input_new(self, char: char):
        lock(self._lock, lambda: self._input_list.append(char))
        self.on_input(self, char)

    @property
    def input_list(self) -> List[char]:
        return lock(self._lock, self.__get_input_list)

    def __get_input_list(self) -> List[char]:
        return super().input_list
