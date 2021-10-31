from typing import Union, Optional, List
from chars import *
from core.events import event
from keys import k_enter, k_quit


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


class cmd_input(i_input):
    """
    If the on_input event is canceled, it'll abandon all remaining chars in input list
    """

    def __init__(self):
        super().__init__()

    def get_input(self, tip: str = None):
        try:
            if tip is None:
                res = input()
            else:
                res = input(str)
            for ch in res:
                ch = printable(ch)
                self._input_list.append(ch)
                canceled = self.on_input(self, ch)
                if canceled:
                    return
            self._input_list.append(k_enter)
            self.on_input(self, k_enter)
        except EOFError:
            quit_ch = k_quit

            self._input_list.append(quit_ch)
            self.on_input(self, quit_ch)
        """if tip is None:
            res = input()
        else:
            res = input(str)
        for ch in res:
            ch = printable(ch)
            self._input_list.append(ch)
            canceled = self.on_input(self, ch)
            if canceled:
                return
        self._input_list.append(k_enter)
        self.on_input(self, k_enter)"""

