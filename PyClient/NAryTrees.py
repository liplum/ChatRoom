from typing import Collection, Iterable

EmptyTuple = ()


class Node:

    def __init__(self, parent=None):
        self._parent = parent

    @property
    def Parent(self):
        return self._parent

    @Parent.setter
    def Parent(self, value):
        self._parent = value

    def GetSubNodes(self) -> Collection["Node"]:
        return EmptyTuple

    def AddNode(self, subNode: "Node"):
        pass

    def IsLeaf(self) -> bool:
        return len(self.GetSubNodes()) == 0


def PreIt(cur: Node) -> Iterable[Node]:
    yield cur
    for node in cur.GetSubNodes():
        yield from PreIt(node)


def PostIt(cur: Node) -> Iterable[Node]:
    for node in cur.GetSubNodes():
        yield from PostIt(node)
    yield cur
