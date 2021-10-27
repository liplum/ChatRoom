from typing import Optional
from select import select
import tty
import termios
from chars import char
from utils import lock
from ui.inputs import i_nbinput
from threading import Thread, RLock


class nbinput(i_nbinput):
    """
    non-blocking input on linux
    """

    def get_input(self, tip: str = None):
        super().get_input(tip)

    def consume_char(self) -> Optional[char]:
        def get_first() -> Optional[chars.char]:
            if len(self._input_list) == 0:
                return None
            first = self._input_list.pop(0)
            return first

        return lock(self._lock, get_first)

    def initialize(self):
        self.listen_thread = Thread(target=self._listen_input)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        self._lock = RLock()

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
                        c: str = sys.stdin.read(1)
                        # TODO:Should fix it
                        self._input_new(c)

        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

    def _input_new(self, char: chars.char):
        lock(self._lock, lambda: self._input_list.append(char))
        self.on_input(self, char)

    @property
    def input_list(self) -> List[chars.char]:
        return lock(self._lock, self.__get_input_list)

    def __get_input_list(self) -> List[chars.char]:
        return super().input_list
