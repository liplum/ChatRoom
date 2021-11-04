import math
from threading import RLock
from time import time
from typing import List

from autofill import prompt


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
        self.max_candidate = 10

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
        filler = self.tree.get_all_start_with(attempt, False, self.max_candidate)
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

        history_count = len(self.history)
        if self._plan_rate + 2 > history_count:  # plus two tails
            return

        # get trimmed mean
        self.history.sort()
        min_time = self.history[0]
        max_time = self.history[-1]
        self.history.remove(min_time)
        self.history.remove(max_time)

        average = sum(self.history) // history_count
        if average <= 0:
            return
        if self.target_delay > average:
            delta = self.target_delay - average
            self.max_candidate += int(math.ceil(delta / self.target_delay))
            self.history.clear()
        elif average > self.target_delay:
            delta = average - self.target_delay
            self.max_candidate -= int(math.ceil(delta / self.target_delay))
            self.history.clear()
