from typing import Dict, List
from collections import defaultdict
import dictries as d


class prompt:
    def __init__(self):
        self.tree = d.dictrie()
        self.last_filler = []
        self.hotwords: Dict[str, int] = defaultdict(int)
        self._max_candidate = -1
        self._has_max = False
        self._min_candidate = 2

    def add(self, word: str) -> "prompt":
        self.tree.insert_word(word)
        return self

    @property
    def has_max(self) -> bool:
        return self._has_max

    @has_max.setter
    def has_max(self, value: bool):
        self._has_max = bool(value)

    @property
    def max_candidate(self) -> int:
        return self._max_candidate

    @max_candidate.setter
    def max_candidate(self, value: int):
        value = int(value)
        self.has_max = value > 0
        self._max_candidate = max(value, self._min_candidate)

    @property
    def min_candidate(self) -> int:
        return self._max_candidate

    @min_candidate.setter
    def min_candidate(self, value: int):
        value = max((int(value), 0))
        self._min_candidate = value
        self._max_candidate = max(value, self._min_candidate)

    def autofill(self, attempt: str) -> List[str]:
        filler = self.tree.get_all_start_with(attempt, max_count=self.max_candidate if self.has_max else None)
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
