from typing import Dict, List, Optional, Tuple, NoReturn
from io import StringIO
from dataclasses import dataclass


def insert_word(nd, word: str) -> int:
    """

    :param nd:
    :param word:
    :return:number of added nodes
    """
    if word is None:
        raise ValueError("word cannot be none.")
    if word == "":
        raise ValueError("word cannot be empty.")
    added_num = 0
    cur = nd
    for ch in word:
        if cur.has(ch):
            next_node = cur[ch]
        else:
            next_node = node(cur, ch)
            cur[ch] = next_node
            added_num += 1
        cur = next_node
    cur.is_word = True
    return added_num


def has(nd, word: str) -> bool:
    if word is None:
        raise ValueError("word cannot be none.")
    if word == "":
        raise ValueError("word cannot be empty.")
    cur = nd
    for ch in word:
        if cur.has(ch):
            next_node = cur[ch]
        else:
            return False
        cur = next_node
    return cur.is_word


def has_prefix(nd, prefix: str) -> bool:
    if prefix is None:
        raise ValueError("prefix cannot be none.")
    if prefix == "":
        raise ValueError("prefix cannot be empty.")
    cur = nd
    for ch in prefix:
        if cur.has(ch):
            next_node = cur[ch]
        else:
            return False
        cur = next_node
    return True


def remove_word(nd, word: str) -> bool:
    if word is None:
        raise ValueError("word cannot be none.")
    if word == "":
        raise ValueError("word cannot be empty.")
    cur = nd
    for ch in word:
        if cur.has(ch):
            next_node = cur[ch]
            cur = next_node
        else:
            return False

    deleted = False
    pre = cur.parent
    if cur.is_word:
        if cur.is_leaf:
            del pre[cur.char_pointing_this]
            deleted = True
        else:
            cur.is_word = False
            return True

    cur = pre
    pre = cur.parent
    while pre is not None:
        if not cur.is_word and cur.is_leaf:
            del pre[cur.char_pointing_this]
            deleted = True
            cur = pre
            pre = cur.parent
        else:
            break
    return deleted


def get_subnode_count(nd):
    count = [0]

    def it(n):
        if n.parent:
            count[0] += 1
        for n in n.nodes:
            it(n)

    it(nd)

    return count[0]


def get_wordnode_count(nd: "node"):
    count = [0]

    def it(n: "node"):
        if n.is_word:
            count[0] += 1
        for n in n.nodes:
            it(n)

    it(nd)

    return count[0]


def remove_start_with(nd, prefix: str) -> Tuple[int, int]:
    if prefix is None:
        raise ValueError("prefix cannot be none.")
    if prefix == "":
        raise ValueError("prefix cannot be empty.")
    if has_prefix(nd, prefix):
        need_removed = nd[prefix[0]]
        subnode_count = need_removed.subnode_count
        word_count = get_wordnode_count(subnode_count)
        del nd[prefix[0]]
        return subnode_count, word_count
    else:
        return 0, 0


def get_subnodes_str(nd) -> List[str]:
    stack = []
    all_matches = []
    res = []
    top_parent = nd.parent

    def it(n):
        if n.parent is not top_parent and n.char_pointing_this:
            stack.append(n.char_pointing_this)
        if n.is_word:
            all_matches.append(stack[:])
        for n in n.nodes:
            it(n)
        if stack:
            stack.pop()

    it(nd)
    for match in all_matches:
        with StringIO() as s:
            for ch in match:
                s.write(ch)
            res.append(s.getvalue())
    return res


def get_partial_start_with(nd, prefix: str, max_count: int) -> List[str]:
    if max_count < 0:
        raise ValueError("max count cannot be negative")
    if max_count == 0:
        return []

    cur = nd
    for ch in prefix:
        if cur.has(ch):
            cur = cur[ch]
        else:
            return []
    stack = []
    all_matches = []
    count = [max_count]
    top_parent = cur.parent

    def it(n):
        if count[0] <= 0:
            return
        if n.parent is not top_parent and n.char_pointing_this:
            stack.append(n.char_pointing_this)
        if n.is_word:
            all_matches.append(stack[:])
            count[0] -= 1
        for n in n.nodes:
            it(n)
        if stack:
            stack.pop()

    it(cur)
    res = []
    for match in all_matches:
        with StringIO() as s:
            s.write(prefix)
            for ch in match:
                s.write(ch)
            res.append(s.getvalue())

    return res


def get_all_start_with(nd, prefix: str) -> List[str]:
    if prefix is None:
        raise ValueError("prefix cannot be none.")
    if prefix == "":
        raise ValueError("prefix cannot be empty.")

    cur = nd
    for ch in prefix:
        if cur.has(ch):
            cur = cur[ch]
        else:
            return []

    stack = []
    all_matches = []
    top_parent = cur.parent

    def it(n):
        if n.parent is not top_parent and n.char_pointing_this:
            stack.append(n.char_pointing_this)
        if n.is_word:
            all_matches.append(stack[:])
        for n in n.nodes:
            it(n)
        if stack:
            stack.pop()

    it(cur)
    res = []
    for match in all_matches:
        with StringIO() as s:
            s.write(prefix)
            for ch in match:
                s.write(ch)
            res.append(s.getvalue())

    return res


class dictrie:
    def __init__(self):
        self.root = root_node()
        self._len = 0
        self._word_count = 0

    def insert_word(self, word: str) -> "dictrie":
        added_num = insert_word(self.root, word)
        self._len += added_num
        self._word_count += 1
        return self

    def has(self, word: str) -> bool:
        return has(self.root, word)

    def has_start_with(self, prefix: str) -> bool:
        return has_prefix(self.root, prefix)

    def remove_word(self, word: str) -> bool:
        is_removed = remove_word(self.root, word)
        if is_removed:
            self._len -= 1
            self._word_count -= 1
        return is_removed

    def remove_start_with(self, prefix: str) -> bool:
        node_count, word_count = remove_start_with(self.root, prefix)
        self._len -= node_count
        self._word_count -= word_count
        return node_count > 0

    def get_all_start_with(self, prefix: str, max_count: Optional[int] = None) -> List[str]:
        if max_count is None or max_count < 0:
            return get_all_start_with(self.root, prefix)
        else:
            return get_partial_start_with(self.root, prefix, max_count)

    def __repr__(self) -> str:
        return repr(self.root)

    def __str__(self) -> str:
        return str(self.root)

    def __getitem__(self, item) -> "node":
        return self.root[item]

    def __iadd__(self, other) -> "dictrie":
        if not isinstance(other, str):
            other = str(other)
        self.insert_word(other)
        return self

    def __len__(self) -> int:
        return self._len

    @property
    def word_count(self) -> int:
        return self._word_count


def get_last_branch_node(n: "node") -> Optional["node"]:
    """
    Gets the last branch node(which contains 2 or more nodes).If n is a branch, return itself.
    :param n:
    :return:
    """
    if n.is_branch:
        return n
    if node.has_parent:
        cur = n
        pre = cur.parent
        while True:
            if pre is None:
                return None
            if pre.is_branch:
                return pre
            cur = pre
            pre = cur.parent
    else:
        return None


def get_last_branch_nodeXn(n: "node") -> Optional["node"]:
    """
    Gets the last branch node(which contains 2 or more nodes).Although n is a branch, not return itself.
    :param n:
    :return:
    """
    if node.has_parent:
        cur = n
        pre = cur.parent
        while True:
            if pre is None:
                return None
            if pre.is_branch:
                return pre
            cur = pre
            pre = cur.parent
    else:
        return None


class node:
    def __init__(self, parent: Optional["node"], char_pointing_this: Optional[str]):
        self.subnodes: Dict[str, "node"] = {}
        self._is_word = False
        self._parent: Optional["node"] = parent
        self._char_pointing_this: Optional[str] = char_pointing_this

    @property
    def parent(self) -> Optional["node"]:
        return self._parent

    @property
    def char_pointing_this(self) -> Optional[str]:
        return self._char_pointing_this

    @property
    def has_parent(self) -> bool:
        return self.parent is None and self.char_pointing_this is None

    @property
    def is_leaf(self) -> bool:
        return len(self.subnodes) == 0

    @property
    def is_word(self) -> bool:
        return self._is_word

    @is_word.setter
    def is_word(self, value: bool):
        self._is_word = value

    @property
    def is_branch(self) -> bool:
        return len(self.subnodes) > 1

    def has(self, ch: str) -> bool:
        return ch in self.subnodes

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        all_subnodes = get_subnodes_str(self)
        l = len(all_subnodes)
        with StringIO() as res:
            res.write('[')
            c = 0
            for subnode in all_subnodes:
                res.write(subnode)
                c += 1
                if c < l:
                    res.write(',')
            res.write(']')
            return res.getvalue()

    @property
    def subnodes_str(self) -> List[str]:
        return get_subnodes_str(self)

    def __getitem__(self, item):
        return self.subnodes[item]

    def __delitem__(self, key):
        del self.subnodes[key]

    def __setitem__(self, key, value):
        self.subnodes[key] = value

    def __iter__(self):
        return iter(self.subnodes.items())

    @property
    def nodes(self) -> ["node"]:
        return self.subnodes.values()

    @property
    def chars(self) -> [str]:
        return self.subnodes.keys()

    def items(self) -> [Tuple[str, "node"]]:
        return self.subnodes.items()

    @property
    def subnode_count(self) -> int:
        return get_subnode_count(self)


class root_node(node):

    def __init__(self):
        super().__init__(None, None)

    @property
    def parent(self) -> Optional["node"]:
        return None

    @property
    def char_pointing_this(self) -> Optional[str]:
        return None

    @property
    def has_parent(self) -> bool:
        return False

    @property
    def is_word(self) -> bool:
        return False

    @property
    def is_leaf(self) -> bool:
        return False
