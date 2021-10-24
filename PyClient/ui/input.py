from typing import Union, Optional, List
from chars import *
from core.event import event


class i_input:
    def __init__(self):
        self._input_list: List[char] = []
        self._on_input = event()
        self._on_inputli_changed = event()

    def get_input(self, tip: str = None):
        pass

    @property
    def input_list(self) -> List[chars.char]:
        return self._input_list[:]

    def flush(self):
        self._input_list = []
        self._on_inputli_changed(self, self._input_list)

    @property
    def on_input(self) -> event:
        """
        First para is the i_input object
        Second para is the char object

        :return: None
        """
        return self._on_input

    @property
    def on_inputli_changed(self) -> event:
        """
        First para is the i_input object
        Second para is the input list object

        :return: None
        """
        return self._on_inputli_changed


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

        self._input_list.append(res)
