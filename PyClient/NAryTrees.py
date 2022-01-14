from typing import Collection, Iterable, Callable, TypeVar

EmptyTuple = ()

"""
         1
     /   |    \ 
    2    3     4
 /  |  \     /   \    
5   6   7   8     9

Pre:[1,2,5,6,7,3,4,8,9]
Post:[5,6,7,2,3,8,9,4,1]
Level:[1,2,3,4,5,6,7,8,9]
"""


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


def LevelIt(cur: Node) -> Iterable[Node]:
    yield cur

    def func(cur: Node):
        subNodes = cur.GetSubNodes()
        for sub in subNodes:
            yield sub
        for sub in subNodes:
            yield from func(sub)

    yield from func(cur)


def LeafIt(cur: Node) -> Iterable[Node]:
    for n in PostIt(cur):
        if n.IsLeaf():
            yield n


def PrintTree(cur: Node, toStr: Callable[[Node], str] = str) -> Collection[str]:
    res = []

    def func(n: Node, level=0):
        res.append("  " * level + toStr(n))
        for child in n.GetSubNodes():
            func(child, level + 1)
        return res

    return func(cur)


NodeT = TypeVar("NodeT")


def DefaultAcceptAll(n: NodeT) -> bool:
    return True


def PreItGen(getSubNodes: Callable[[NodeT], Collection[NodeT]]
             , canYield: Callable[[NodeT], bool] = DefaultAcceptAll
             ) -> Callable[[NodeT], Iterable[NodeT]]:
    def PreIt(cur: NodeT) -> Iterable[NodeT]:
        if canYield(cur):
            yield cur
        for node in getSubNodes(cur):
            yield from PreIt(node)

    return PreIt


def PostItGen(getSubNodes: Callable[[NodeT], Collection[NodeT]],
              canYield: Callable[[NodeT], bool] = DefaultAcceptAll
              ) -> Callable[[NodeT], Iterable[NodeT]]:
    def PostIt(cur: NodeT) -> Iterable[NodeT]:
        for node in getSubNodes(cur):
            yield from PostIt(node)
        if canYield(cur):
            yield cur

    return PostIt


def LevelItGen(getSubNodes: Callable[[NodeT], Collection[NodeT]],
               canYield: Callable[[NodeT], bool] = DefaultAcceptAll
               ) -> Callable[[NodeT], Iterable[NodeT]]:
    def LevelIt(cur: NodeT) -> Iterable[NodeT]:
        if canYield(cur):
            yield cur

        def func(cur: NodeT):
            subNodes = getSubNodes(cur)
            for sub in subNodes:
                if canYield(sub):
                    yield sub
            for sub in subNodes:
                yield from func(sub)

        yield from func(cur)

    return LevelIt


def LeafItGen(getSubNodes: Callable[[NodeT], Collection[NodeT]],
              isLeaf: Callable[[NodeT], bool],
              canYield: Callable[[NodeT], bool] = DefaultAcceptAll
              ) -> Callable[[NodeT], Iterable[NodeT]]:
    def PostIt(cur: NodeT) -> Iterable[NodeT]:
        for node in getSubNodes(cur):
            yield from PostIt(node)
        if canYield(cur):
            yield cur

    def Func():
        for n in PostIt(cur):
            if isLeaf(n):
                yield n

    return Func


def PrintTreeGen(getSubNodes: Callable[[NodeT], Collection[NodeT]],
                 canPrint: Callable[[NodeT], bool] = DefaultAcceptAll,
                 isSelfSubTreeCanPrint: Callable[[NodeT], bool] = DefaultAcceptAll,
                 toStr: Callable[[Node], str] = str) -> Callable[[NodeT], Collection[str]]:
    def PrintTree(cur: Node) -> Collection[str]:
        res = []

        def func(n: Node, level=0):
            if not isSelfSubTreeCanPrint(n):
                return
            if canPrint(n):
                res.append("  " * level + toStr(n))
            for child in getSubNodes(n):
                func(child, level + 1)

        func(cur)
        return res

    return PrintTree
