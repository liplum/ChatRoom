from typing import Callable, Optional, Set

import chars
from events import event
from utils import get


class kbinding:
    def __init__(self):
        self.bindings = {}
        self._on_any = None

    def bind(self, ch: chars.char, func: Callable[[chars.char], Optional[bool]]):
        self.bindings[ch] = func

    @property
    def on_any(self) -> Callable[[chars.char], Optional[bool]]:
        return self._on_any

    @on_any.setter
    def on_any(self, func: Callable[[chars.char], Optional[bool]]):
        self._on_any = func

    def trigger(self, ch: chars.char) -> Optional[bool]:
        func: Callable[[chars.char], Optional[bool]] = get(self.bindings, ch)
        if func is not None:
            return func(ch)
        if self.on_any is not None:
            return self.on_any(ch)
        return False


class cmdkey:
    def __init__(self):
        self.mappings: Set[chars.char] = set()
        self._on_map = event()
        self._on_demap = event()

    @property
    def on_map(self):
        """
        Para 1:cmdkey object

        Para 2:mapped char

        :return: event(textbox,int,str)
        """
        return self._on_map

    @property
    def on_demap(self):
        """
        Para 1:cmdkey object

        Para 2:demapped char

        :return: event(textbox,int,str)
        """
        return self._on_demap

    def map(self, char: chars.char) -> "cmdkey":
        self.mappings.add(char)
        self.on_map(self, char)
        return self

    def demap(self, char: chars.char, rematch: bool) -> "cmdkey":
        if rematch:
            for ch in self.mappings:
                if ch == char:
                    self.mappings.remove(ch)
                    self.on_demap(self, ch)
                    break
        else:
            try:
                self.mappings.remove(char)
                self.on_demap(self, char)
            except KeyError:
                pass
        return self

    def __eq__(self, other) -> bool:
        for ch in self.mappings:
            if ch == other:
                return True
        return False
