from abc import ABC, abstractmethod
from collections import deque
from typing import List

from Events import Event
from chars import *


class iinput(ABC):
    def __init__(self):
        self._input_list: deque[char] = deque()
        self._on_input = Event(iinput, char, cancelable=True)

    def get_input(self, tip: str = None):
        pass

    @property
    def input_list(self) -> List[char]:
        return list(self._input_list)

    def flush(self):
        self._input_list = []
        self.on_inputli_changed(self, self._input_list)

    @property
    def on_input(self) -> Event:
        """
        Para 1:iinput object

        Para 2:Char object

        Canceled:The behavior will be determined by it's implement

        :return: Event(iinput,Char)
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

    def InitInput(self):
        pass

    @property
    @abstractmethod
    def is_end(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def is_blocked_input(self):
        raise NotImplementedError()


class inbinput(iinput, ABC):

    @property
    def is_blocked_input(self):
        return False
