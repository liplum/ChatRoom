import os
from threading import RLock
from typing import Dict, List, Tuple
import time
from io import StringIO


def get(dic: Dict, key):
    if key in dic:
        return dic[key]
    else:
        return None


def get_not_none_one(*args):
    """
    :param args:all selections
    :return: the first not none one otherwise None
    """
    for arg in args:
        if arg is not None:
            return arg
    return None


def not_none(*args) -> bool:
    for arg in args:
        if arg is None:
            return False
    return True


def clear_screen():
    os.system("cls")


def lock(lock: RLock, func, *args, **kwargs):
    lock.acquire()
    _return = func(*args, **kwargs)
    lock.release()
    return _return


def get_cur_time_milisecs() -> int:
    return get_milisecs(time.time())


def get_milisecs(time) -> int:
    return int(round(time * 1000))


class clock:
    def __init__(self, tps: int):
        self.tps = tps
        self.interval = 1000 / tps
        self.last = None

    def delay(self):
        if self.last is None:
            self.last = get_cur_time_milisecs()
            return
        else:
            cur = get_cur_time_milisecs()
            real_interval = self.last - cur
            sleep_time = real_interval - self.interval
            self.last = cur
            if sleep_time > 0:
                time.sleep(float(sleep_time) / 1000)


def separate(text: str, separator: str, number: int = None, allow_emptychar: bool = True) -> List[str]:
    """

    :param text:
    :param separator:the character used to be separate.
    :param number:the max separation count.
    :param allow_emptychar:If true,it skips the empty char.Otherwise the item which result contains can be a empty char.
    :return:
    """
    if len(separator) > 1:
        raise ValueError(f"separator length is {len(separator)},it needs 1")
    total_len = len(text)
    if number is None or number < 0:
        number = total_len
    res = []
    temp = StringIO()
    char_count = 0
    finished = False
    if allow_emptychar:
        for char in text:
            if number <= 0:
                finished = True
                break
            char_count += 1
            if char == separator:
                cur = temp.getvalue()
                res.append(cur)
                number -= 1
                temp.close()

                temp = StringIO()
            else:
                temp.write(char)

        if not finished:
            cur = temp.getvalue()
            res.append(cur)
        else:
            rest_len = total_len - char_count
            if rest_len > 0:
                res.append(text[-rest_len:])

    else:  # not allow empty char
        for char in text:
            if number <= 0:
                finished = True
                break
            char_count += 1
            if char == separator:
                cur = temp.getvalue()
                if len(cur) > 0:
                    res.append(cur)
                    number -= 1
                    temp.close()
                    temp = StringIO()
            else:
                temp.write(char)

        cur = temp.getvalue()
        if not finished:
            if len(cur) > 0:
                res.append(cur)
        else:
            rest_len = total_len - char_count
            if rest_len > 0:
                res.append(text[-rest_len:])

    temp.close()
    return res


def compose(seq, connector: str = ",", pretreat=str, end: str = ""):
    with StringIO() as temp:
        c = 0
        max_len = len(seq)
        if pretreat is None:
            for item in seq:
                c += 1
                temp.write(item)
                if c < max_len:
                    temp.write(connector)
        else:
            for item in seq:
                c += 1
                temp.write(pretreat(item))
                if c < max_len:
                    temp.write(connector)
        temp.write(end)
        return temp.getvalue()


def get_mid(a: int, b: int) -> int:
    return int((a + b) / 2)


def find_range(sequential, item, offset: int = 0) -> Tuple[int, int]:
    seql = len(sequential)
    rest = seql - offset
    if rest < 0:
        raise ValueError(f"offset is {offset} and greater than whole's length")
    if rest == 1:
        return offset, offset
    else:
        lefti = offset
        righti = seql - 1
        if item <= sequential[lefti]:
            return lefti, lefti
        if item >= sequential[righti]:
            return righti, righti

        while lefti < righti:
            midi = get_mid(lefti, righti)
            mid = sequential[midi]
            if item < mid:
                righti = midi
            elif item > mid:
                lefti = midi
            else:
                return midi, midi
            if lefti + 1 == righti:
                return lefti, righti
