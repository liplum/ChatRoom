from typing import List

from chars import *
from core.events import event


class i_input:
    def __init__(self):
        self._input_list: List[char] = []
        self._on_input = event(cancelable=True)

    def get_input(self, tip: str = None):
        pass

    @property
    def input_list(self) -> List[char]:
        return self._input_list[:]

    def flush(self):
        self._input_list = []
        self.on_inputli_changed(self, self._input_list)

    @property
    def on_input(self) -> event:
        """
        Para 1:i_input object


        Para 2:char object

        Canceled:The behavior will be determined by it's implement

        :return: event(i_input,char)
        """
        return self._on_input

    @property
    def input_len(self):
        return len(self._input_list)

    def consume_char(self) -> Optional[char]:
        if len(self._input_list) == 0:
            return None
        else:
            return self._input_list.pop(0)

    def initialize(self):
        pass


class i_nbinput(i_input):
    pass
