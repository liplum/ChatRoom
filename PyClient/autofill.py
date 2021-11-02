from typing import Dict, List
from collections import defaultdict
import dictries as d
from time import time
from threading import RLock
import math


class prompt:
    def __init__(self):
        self.tree = d.dictrie()
        self.last_filler = []
        self.hotwords: Dict[str, int] = defaultdict(int)
        self._max_candidate = -1

    def add(self, word: str) -> "prompt":
        self.tree.insert_word(word)
        return self

    @property
    def max_candidate(self) -> int:
        return self._max_candidate

    @max_candidate.setter
    def max_candidate(self, value: int):
        self._max_candidate = int(value)

    def autofill(self, attempt: str) -> List[str]:
        filler = self.tree.get_all_start_with(attempt)
        filler.sort(key=lambda word: self.hotwords[word], reverse=True)
        self.last_filler = filler
        return filler

    def apply(self, result: str):
        """
        For the performance, it doesn't check if para result is truly in the dictrie
        so that you have to guarantee that.
        :param result:
        :return:
        """
        self.hotwords[result] += 1

    def remove(self, word: str) -> bool:
        is_removed = self.tree.remove_word(word)
        if word in self.hotwords:
            del self.hotwords[word]
        return is_removed


def _now_milisecs() -> int:
    return int(round(time() * 1000))


def _now_microsecs() -> int:
    return int(round(time() * 1000000))


class autoprompt(prompt):

    def __init__(self):
        super().__init__()
        self.lock = RLock()
        self.history = []
        self._plan_rate = 5
        self.last_change = 0
        self.target_delay = 1000  # microseconds = 1 ms
        self.min_candidate = 2
        self.max_candidate = 10

    @property
    def max_candidate(self) -> int:
        return self._max_candidate

    @max_candidate.setter
    def max_candidate(self, value: int):
        self._max_candidate = max(self.min_candidate, int(value))

    @property
    def plan_rate(self):
        return self._plan_rate

    @plan_rate.setter
    def plan_rate(self, value: int):
        """

        :param value:belongs to [1,+infinity)
        :return:
        """
        self._plan_rate = min(int(value), 1)

    def autofill(self, attempt: str) -> List[str]:
        self.lock.acquire()
        pre = _now_microsecs()
        filler = self.tree.get_all_start_with(attempt, self.max_candidate)
        post = _now_microsecs()
        self.lock.release()
        duration = post - pre
        self.history.append(duration)

        self.replan()
        filler.sort(key=lambda word: self.hotwords[word], reverse=True)
        self.last_filler = filler
        return filler

    def replan(self):
        word_count = self.tree.word_count
        if word_count <= self.max_candidate:
            return

        history_len = len(self.history)
        if self._plan_rate > history_len:
            return
        average = sum(self.history) // history_len
        if average <= 0:
            return
        if average < self.target_delay:
            delta = self.target_delay - average
            self.max_candidate += int(math.ceil(delta / average))
            self.history.clear()
        elif average > self.target_delay:
            delta = average - self.target_delay
            self.max_candidate -= int(math.ceil(delta / self.target_delay))
            self.history.clear()
        else:
            return
