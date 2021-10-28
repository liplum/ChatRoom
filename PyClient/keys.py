"""from typing import Union, Tuple, Dict, List, Any, Optional

from chars import char
from utils import get, addmultidic, multiget"""
"""
__kregistry: Dict["controlk", List[char]] = {}


class controlk:

    def __eq__(self, other: Union[char, str, bytes, int, Tuple[int, int], Tuple[int, int, int, int]]):
        return is_key(other, self)

    def __hash__(self):
        li = multiget(__kregistry, self)
        tp = tuple(li)
        return hash(tp)

    def register(self, ch: char):
        register(ch, self)


def register(ch: char, key: controlk):
    addmultidic(__kregistry, key, ch)


def is_key(ch: Union[char, bytes, int, Tuple[int, int], Tuple[int, int, int, int]], target: controlk) -> bool:
    li = multiget(__kregistry, target)
    for realchar in li:
        if realchar == ch:
            return True
    return False
"""

k_up = None
k_down = None
k_left = None
k_right = None

k_pgdown = None
k_pgup = None

k_end = None
k_home = None

k_insert = None
k_delete = None

k_backspace = None

k_enter = None

k_f1 = None
k_f2 = None
k_f3 = None
k_f4 = None

k_f5 = None
k_f6 = None
k_f7 = None
k_f8 = None

k_f9 = None
k_f10 = None

k_f12 = None
