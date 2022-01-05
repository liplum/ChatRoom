from typing import Collection, Generator, Callable, Iterable, TypeVar, Optional, List, Tuple

import chars
from Events import Event
from NAryTrees import PreItGen, PostItGen, LevelItGen, LeafItGen, PrintTreeGen
from ui.Renders import Painter

IsConsumed = bool
Consumed = True
NotConsumed = False
auto = "auto"
PROP = TypeVar('PROP', str, int)
T = TypeVar('T')


class RoutedEvent:
    pass


class VisualElement(Painter):
    def __init__(self):
        super().__init__()
        self._subVElems: List["VisualElement"] = []
        self._vElemParent = None
        self._onPropChanged = Event(VisualElement, str)
        self._onAttachPropChanged = Event(VisualElement, str)
        self._onLayoutPropChanged = self._onPropChanged.Sub()
        self._onNormalPropChanged = self._onPropChanged.Sub()
        self._width = 0
        self._height = 0
        self._dWidth = 0
        self._dHeight = 0
        self._renderWidth = 0
        self._renderHeight = 0

    def OnAddedInfoVTree(self, parent: "VisualElement"):
        self.VElemParent = parent

    @property
    def VElemParent(self) -> Optional["VisualElement"]:
        return self._vElemParent

    @VElemParent.setter
    def VElemParent(self, value: Optional["VisualElement"]):
        self._vElemParent = value

    def GetSubVElems(self) -> Collection["VisualElement"]:
        return self._subVElems

    def AddVElem(self, subElem: "VisualElement"):
        self._subVElems.append(subElem)

    def RemoveVElem(self, subElem: "VisualElement"):
        self._subVElems.remove(subElem)

    def IsVElemLeaf(self) -> bool:
        return len(self.GetSubVElems()) == 0

    @property
    def OnPropChanged(self) -> Event:
        """
        Para 1:VisualElement object

        Para 2:property name

        :return: Event(VisualElement,str)
        """
        return self._onPropChanged

    @property
    def OnAttachPropChanged(self) -> Event:
        """
        Para 1:VisualElement object

        Para 2:property name

        :return: Event(VisualElement,str)
        """
        return self._onAttachPropChanged

    @property
    def OnLayoutPropChanged(self) -> Event:
        """
        Para 1:VisualElement object

        Para 2:property name

        :return: Event(VisualElement,str)
        """
        return self._onLayoutPropChanged

    @property
    def OnNormalPropChanged(self) -> Event:
        """
        Para 1:VisualElement object

        Para 2:property name

        :return: Event(VisualElement,str)
        """
        return self._onNormalPropChanged

    @property
    def Width(self):
        return self._width

    @Width.setter
    def Width(self, value: PROP):
        if self._width != value:
            self._width = value

    @property
    def Height(self):
        return self._height

    @Height.setter
    def Height(self, value: PROP):
        if self._height != value:
            self._height = value

    @property
    def DWidth(self):
        return

    @DWidth.setter
    def DWidth(self, value):
        pass

    @property
    def DHeight(self):
        return

    @DHeight.setter
    def DHeight(self, value):
        pass

    @property
    def RenderWidth(self):
        return

    @RenderWidth.setter
    def RenderWidth(self, value):
        pass

    @property
    def RenderHeight(self):
        return

    @RenderHeight.setter
    def RenderHeight(self, value):
        pass

    def Measure(self):
        pass

    def Arrange(self, width: int, height: int) -> Tuple[int, int]:
        """

        :param width:
        :param height:
        :return: (real width,real height)
        """
        pass


_VElemItType = Callable[[VisualElement], Iterable[VisualElement]]

PreItV: _VElemItType = PreItGen(VisualElement.GetSubVElems)
PostItV: _VElemItType = PostItGen(VisualElement.GetSubVElems)
LevelItV: _VElemItType = LevelItGen(VisualElement.GetSubVElems)
LeafItV: _VElemItType = LeafItGen(VisualElement.GetSubVElems, VisualElement.IsVElemLeaf)
PrintVTree: Callable[[VisualElement], Collection[str]] = PrintTreeGen(VisualElement.GetSubVElems)

DefaultNotConsumed = (NotConsumed,)


class LogicalElement:
    def __init__(self):
        super().__init__()
        self._subLElems: Collection["LogicalElement"] = []
        self._lElemParent = None
        self._isFocused = False

    def OnAddedInfoLTree(self, parent: "LogicalElement"):
        self.LElemParent = parent

    def IsLElemLeaf(self) -> bool:
        return len(self.GetSubLElems()) == 0

    @property
    def LElemParent(self) -> Optional["LogicalElement"]:
        return self._lElemParent

    @LElemParent.setter
    def LElemParent(self, value: Optional["LogicalElement"]):
        self._lElemParent = value

    def GetSubLElems(self) -> Collection["LogicalElement"]:
        return self._subLElems

    def AddLElem(self, subElem: "LogicalElement"):
        self._subLElems.append(subElem)

    def RemoveLElem(self, subElem: "LogicalElement"):
        self._subLElems.remove(subElem)

    def OnInput(self, char: chars.char) -> Generator:
        """
        When user types a char
        :param char: which be typed
        :return:whether this object consumed the char
        """
        yield from DefaultNotConsumed

    @property
    def Focusable(self) -> bool:
        return False

    def OnFocused(self):
        self._isFocused = True

    def OnLostFocused(self):
        self._isFocused = False


def GetLElemsSubs(ve: LogicalElement):
    return ve.GetSubVElems()


_LElemItType = Callable[[LogicalElement], Iterable[LogicalElement]]

PreItL: _LElemItType = PreItGen(LogicalElement.GetSubLElems)
PostItL: _LElemItType = PostItGen(LogicalElement.GetSubLElems)
LevelItL: _LElemItType = LevelItGen(LogicalElement.GetSubLElems)
LeafItL: _LElemItType = LeafItGen(LogicalElement.GetSubLElems, LogicalElement.IsLElemLeaf)
PrintLTree: Callable[[LogicalElement], Collection[str]] = PrintTreeGen(LogicalElement.GetSubLElems)


class FocusWalker:
    def __init__(self):
        super().__init__()
        self._root: Optional[LogicalElement] = None
        self.seq = []
        self._curIndex: Optional[int] = None
        self._curFocused: Optional[LogicalElement] = None

    @property
    def CurFocused(self) -> Optional[LogicalElement]:
        return self._curFocused

    @CurFocused.setter
    def CurFocused(self, value: Optional[LogicalElement]):
        old = self._curFocused
        if old != value:
            self._curFocused = value
            if old:
                old.OnLostFocused()
            if value:
                value.OnFocused()

    @property
    def CurIndex(self) -> Optional[int]:
        return self._curIndex

    @CurIndex.setter
    def CurIndex(self, value: Optional[int]):
        oldIndex = self._curIndex
        if oldIndex != value:
            seqLen = len(self.seq)
            if seqLen == 0:
                value = None
            if value is None:
                self._curIndex = None
                self.CurFocused = None
            else:
                value %= seqLen
                self._curIndex = value
                self.CurFocused = self.seq[value]

    @property
    def Root(self) -> Optional[LogicalElement]:
        return self._root

    @Root.setter
    def Root(self, value: Optional[LogicalElement]):
        self._root = value

    def Next(self):
        if self.CurIndex is not None:
            self.CurIndex += 1

    def Back(self):
        if self._curIndex is not None:
            self.CurIndex -= 1

    def ReGen(self):
        root = self.Root
        if root:
            self.seq = list(elem for elem in LeafItL(root) if elem.Focusable)
            self.CurIndex = 0
