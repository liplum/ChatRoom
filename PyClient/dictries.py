from typing import Dict, List, Optional, Tuple
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
                next_node = node(cur, ch)
                cur[ch] = next_node
            cur = next_node
        cur.is_word = True

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
            raise ValueError("word cannot be none.")
        if word == "":
            raise ValueError("word cannot be empty.")
        cur = self.root
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
    
    def get_all_start_with(self,prefix:str)->List[str]:
        if prefix is None:
            raise ValueError("prefix cannot be none.")
        if prefix == "":
            raise ValueError("prefix cannot be empty.")
        stack=[]
        all_matchs=[]
        def it(nd):
            if nd.char_pointing_this:
                stack.append(nd.char_pointing_this)
            if nd.is_word:
                all_matchs.append(stack[:])
            for n in nd.nodes:
                it(n)
            stack.pop()
        
        cur=self.root
        for ch in prefix:
            if cur.has(ch):
                cur = cur[ch]
            else:
                return []

        it(cur)
        prefix=prefix[:-1]
        res=[]
        for match in all_matchs:
            with StringIO() as s:
                s.write(prefix)
                for ch in match:
                    s.write(ch)
                res.append(s.getvalue())

        return res
    
    def get_all_start_with2(self, prefix: str) -> List[str]:
        if prefix is None:
            raise ValueError("prefix cannot be none.")
        if prefix == "":
            raise ValueError("prefix cannot be empty.")
        cur = self.root
        for ch in prefix:
            if cur.has(ch):
                next_node = cur[ch]
                cur = next_node
            else:
                return []
        all_match: List[List[str]] = []
        start_node = cur
        stack = []
        first_start = True

        while True:
            if len(stack) == 0 and not first_start:
                break
            else:
                first_start = True

            for ch, node in cur:
                if node.is_leaf:
                    stack.append(node.char_pointing_this)
                    all_match.append(stack[:])
                    last_branch = get_last_branch_node(cur)
                    cur = node.parent
                    pre = cur.parent
                    while cur is not last_branch:
                        stack.pop()
                        if cur.is_word:
                            all_match.append(stack[:])
                        cur = pre
                        pre = cur.parent
                    cur = last_branch
                    continue
                else:
                    stack.append(ch)
                    cur = cur[ch]
                    break

    """  while True:
          if not cur.is_leaf:
              for ch, node in cur:
                  if node.is_leaf:
                      all_match.append(stack[:])
                      cur = cur.parent
                      break
                  else:
                      stack.append(ch)
                      cur = cur[ch]
          else:
              all_match.append(stack[:])
              pre = cur.parent
              while pre is not None and cur is not start_node.parent:
                  stack.pop()
                  if cur.is_word:
                      all_match.append(stack[:])
                  if not cur.is_leaf:
                      break"""

    def __repr__(self):
        return repr(self.root)


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
        self.sub_nodes: Dict[str, "node"] = {}
        self._is_word = False
        self.parent: Optional["node"] = parent
        self.char_pointing_this: Optional[str] = char_pointing_this

    @property
    def has_parent(self):
        return self.parent is None and self.char_pointing_this is None

    @property
    def is_leaf(self):
        return len(self.sub_nodes) == 0

    @property
    def is_word(self) -> bool:
        return self._is_word

    @is_word.setter
    def is_word(self, value: bool):
        self._is_word = value

    @property
    def is_branch(self):
        return len(self.sub_nodes) > 1

    def has(self, ch: str) -> bool:
        return ch in self.sub_nodes

    def __repr__(self) -> str:
        return repr(self.sub_nodes)

    def __getitem__(self, item):
        return self.sub_nodes[item]

    def __delitem__(self, key):
        del self.sub_nodes[key]

    def __setitem__(self, key, value):
        self.sub_nodes[key] = value

    def __iter__(self):
        return iter(self.sub_nodes.items())

    @property
    def nodes(self) -> ["node"]:
        return self.sub_nodes.values()

    @property
    def chars(self) -> [str]:
        return self.sub_nodes.keys()

    def items(self) -> [Tuple[str, "node"]]:
        return self.sub_nodes.items()


class root_node(node):

    def __init__(self):
        super().__init__(None, None)

    @property
    def is_word(self) -> bool:
        return False

    @property
    def is_leaf(self):
        return False
