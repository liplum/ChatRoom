from typing import Dict,List

import dictries as d


def _get_or_zero(dic, key) -> int:
    if key in dic:
        return dic[key]
    else:
        dic[key] = 0
        return 0


class prompt:
    def __init__(self):
        self.tree = d.dictrie()
        self.last_filler = []
        self.hotwords: Dict[str, int] = {}

    def add(self, word: str)->"prompt":
        self.tree.insert_word(word)
        return self

    def autofill(self, attempt: str) -> List[str]:
        filler = self.tree.get_all_start_with(attempt)
        filler.sort(key=lambda word: _get_or_zero(self.hotwords, word), reverse=True)
        self.last_filler = filler
        return filler

    def apply(self, result: str):
        if result in self.last_filler:
            hotlevel = _get_or_zero(self.hotwords, result)
            self.hotwords[result] = hotlevel + 1

    def remove(self, word: str) -> bool:
        is_removed = self.tree.remove_word(word)
        if word in self.hotwords:
            del self.hotwords[word]
        return is_removed
