from typing import Union, Optional, List
from chars import *
from core.events import event


class i_input:
    def __init__(self):
        self._input_list: List[char] = []
        self._on_input = event()

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
        First para is the i_input object


        Second para is the char object

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


class cmd_input(i_input):
    def __init__(self):
        super().__init__()

    def get_input(self, tip: str = None):
        if tip is None:
            res = input()
        else:
            res = input(str)
        for char in res:
            ch = printable(char)
            self._input_list.append(ch)
            self.on_input(self,ch)
