from collections import deque
from typing import List

from chars import *
from events import event


class iinput:
    def __init__(self):
        self._input_list: deque[char] = deque()
        self._on_input = event(cancelable=True)

    def get_input(self, tip: str = None):
        pass

    @property
    def input_list(self) -> List[char]:
        return list(self._input_list)

    def flush(self):
        self._input_list = []
        self.on_inputli_changed(self, self._input_list)

    @property
    def on_input(self) -> event:
        """
        Para 1:iinput object

        Para 2:char object

        Canceled:The behavior will be determined by it's implement

        :return: event(iinput,char)
        """
        return self._on_input

    @property
    def input_len(self):
        return len(self._input_list)

    def consume_char(self) -> Optional[char]:
        if len(self._input_list) == 0:
            return None
        else:
            return self._input_list.popleft()

    def initialize(self):
        pass


class inbinput(iinput):
    pass
