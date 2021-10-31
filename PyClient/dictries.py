from typing import Dict, List
from io import StringIO


class dictrie:
    def __init__(self):
        self.root = root_node()

    def insert_word(self, word: str):
        if word is None:
            raise ValueError("word cannot be none.")
        if word == "":
            raise ValueError("word cannot be empty.")
        cur = self.root
        for ch in word:
            if cur.has(ch):
                next_node = cur[ch]
            else:
                next_node = node()
                cur[ch] = next_node
            cur = next_node

    def has(self, word: str):
        if word is None:
            raise ValueError("word cannot be none.")
        if word == "":
            raise ValueError("word cannot be empty.")
        cur = self.root
        for ch in word:
            if cur.has(ch):
                next_node = cur[ch]
            else:
                return False
            cur = next_node
        return cur.is_word

    def has_start_with(self, prefix: str):
        if prefix is None:
            raise ValueError("prefix cannot be none.")
        if prefix == "":
            raise ValueError("prefix cannot be empty.")
        cur = self.root
        for ch in prefix:
            if cur.has(ch):
                next_node = cur[ch]
            else:
                return False
            cur = next_node
        return True

    def remove_word(self, word: str) -> bool:
        if word is None:
            raise ValueError("prefix cannot be none.")
        if word == "":
            raise ValueError("prefix cannot be empty.")
        cur = self.root
        parent = None
        for ch in word:
            if cur.has(ch):
                next_node = cur[ch]
                parent = cur
                cur = next_node
            else:
                return False
        if cur.is_word:
            del parent[ch]
            return True
        else:
            return False

    def remove_start_with(self, prefix: str) -> bool:
        if prefix is None:
            raise ValueError("prefix cannot be none.")
        if prefix == "":
            raise ValueError("prefix cannot be empty.")
        if self.has_start_with(prefix):
            del self.root[prefix[0]]
            return True
        else:
            return False

    def match_word(self, prefix: str) -> List[str]:
        pass

    def __repr__(self):
        return repr(self.root)


class node:
    def __init__(self):
        self.sub_nodes: Dict[str, "node"] = {}

    @property
    def is_word(self) -> bool:
        return len(self.sub_nodes) == 0

    def has(self, ch: str) -> bool:
        return ch in self.sub_nodes

    def all_subs(self) -> List[str]:
        total: List[str] = []

    def _all_subs(self) -> List[str]:
        chs: List[str] = []
        for ch, n in self:
            chs.append(ch)

    def __repr__(self) -> str:
        return repr(self.sub_nodes)

    def __getitem__(self, item):
        return self.sub_nodes[item]

    def __delitem__(self, key):
        del self.sub_nodes[key]

    def __setitem__(self, key, value):
        self.sub_nodes[key] = value

    def __iter__(self):
        return self.sub_nodes.items()

    def nodes(self) -> ["node"]:
        return self.sub_nodes.values()

    def chars(self) -> [str]:
        return self.sub_nodes.keys()


class root_node(node):

    @property
    def is_word(self) -> bool:
        return False
