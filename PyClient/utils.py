import os
from threading import RLock
from typing import Dict
import time


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
