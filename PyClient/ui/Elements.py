from typing import Collection, Generator, TypeVar, Iterable

import chars
from DpProps import *
from Events import Event
from NAryTrees import PreItGen, PostItGen, LevelItGen, LeafItGen, PrintTreeGen
from ui.Renders import Painter

EmptyTuple = ()
IsConsumed = bool
Consumed = True
NotConsumed = False
Auto = "Auto"
WidthHeightType = Union[int, str]
PROP = TypeVar('PROP', str, int)
T = TypeVar('T')

DefaultNotConsumed = (NotConsumed,)


class UIElement(Painter, DpObj):
    NeedRerenderEvent: RoutedEventType
    IsVisibleProp: DpProp
    WidthProp: DpProp
    HeightProp: DpProp
    IsFocusedProp: DpProp

    def __init__(self):
        super().__init__()
        self._children: List["UIElement"] = []
        self._parent = None
        self._dWidth = 0
        self._dHeight = 0
        self._renderWidth = 0
        self._renderHeight = 0
        # ------------Legacy------------
        self._onRenderContentChanged = Event(UIElement)
        self._onPropChanged = Event(UIElement, str)
        self._onAttachPropChanged = Event(UIElement, str)
        self._onLayoutPropChanged = self._onPropChanged.Sub()
        self._onNormalPropChanged = self._onPropChanged.Sub()
        # ------------Legacy------------

    @property
    def IsVisible(self) -> bool:
        return self.GetValue(self.IsVisibleProp)

    @IsVisible.setter
    def IsVisible(self, value: bool):
        for subElemt in PreItV(self):
            subElemt.SetValue(UIElement.IsVisibleProp, value)

    @property
    def Width(self) -> WidthHeightType:
        return self.GetValue(self.WidthProp)

    @Width.setter
    def Width(self, value: WidthHeightType):
        self.SetValue(self.WidthProp, value)

    @property
    def Height(self) -> WidthHeightType:
        return self.GetValue(self.HeightProp)

    @Height.setter
    def Height(self, value: WidthHeightType):
        self.SetValue(self.HeightProp, value)

    def NeedRerender(self):
        if self.IsVisible:
            self.Raise(self.NeedRerenderEvent, self, RoutedEventArgs(False))

    @staticmethod
    def Raise(eventType: RoutedEventType, sender: "UIElement", args: RoutedEventArgs):
        if eventType.Strategy == RoutedStrategy.Bubble:
            chain = BubbleParentChain(sender)
        elif eventType.Strategy == RoutedStrategy.Tunnel:
            chain = reversed(BubbleParentChain(sender))
        elif eventType.Strategy == RoutedStrategy.Tunnel:
            chain = (sender,)
        else:
            chain = ()
        if not isinstance(args, eventType.ArgsType):
            raise EventTypeError(f"{args},{type(args)} in type,doesn't match required type {self.ArgsType}.")
        for elemt in chain:
            if args.Cancelable and args.IsHandled:
                break
            elemt.TryCatchEvent(eventType, sender, args)

    def ShowInLTree(self) -> bool:
        return False

    @property
    def Parent(self) -> Optional["UIElement"]:
        return self._parent

    @Parent.setter
    def Parent(self, value: Optional["UIElement"]):
        self._parent = value

    def GetChildren(self) -> Collection["UIElement"]:
        return self._children

    def AddChild(self, subElem: "UIElement"):
        self._children.append(subElem)
        subElem.Parent = self

    def RemoveChild(self, subElem: "UIElement") -> bool:
        if subElem in self._children:
            self._children.remove(subElem)
            subElem.Parent = None
            return True
        else:
            return False

    def IsLeaf(self) -> bool:
        return len(self.GetChildren()) == 0

    @property
    def DWidth(self):
        return self._dWidth

    @DWidth.setter
    def DWidth(self, value):
        self._dWidth = value

    @property
    def DHeight(self):
        return self._dHeight

    @DHeight.setter
    def DHeight(self, value):
        self._dHeight = value

    @property
    def RenderWidth(self):
        return self._renderWidth

    @RenderWidth.setter
    def RenderWidth(self, value):
        self._renderWidth = value

    @property
    def RenderHeight(self):
        return self._renderHeight

    @RenderHeight.setter
    def RenderHeight(self, value):
        self._renderHeight = value

    def Measure(self):
        pass

    def Arrange(self, width: int, height: int) -> Tuple[int, int]:
        """

        :param width:
        :param height:
        :return: (real Width,real Height)
        """
        pass

    def OnInput(self, char: chars.char) -> Generator:
        """
        When user types a Char
        :param char: which be typed
        :return:whether this object consumed the Char
        """
        yield from DefaultNotConsumed

    @property
    def Focusable(self) -> bool:
        return False

    def OnFocused(self):
        self.IsFocused = True

    def OnLostFocused(self):
        self.IsFocused = False

    @property
    def IsFocused(self) -> bool:
        return self.GetValue(self.IsFocusedProp)

    @IsFocused.setter
    def IsFocused(self, value: bool):
        self.SetValue(self.IsFocusedProp, value)

    # ------------Legacy------------
    @property
    def OnRenderContentChanged(self) -> Event:
        """
        Para 1:UIElement object

        :return: Event(UIElement)
        """
        return self._onRenderContentChanged

    @property
    def OnPropChanged(self) -> Event:
        """
        Para 1:UIElement object

        Para 2:property name

        :return: Event(UIElement,str)
        """
        return self._onPropChanged

    @property
    def OnAttachPropChanged(self) -> Event:
        """
        Para 1:UIElement object

        Para 2:property name

        :return: Event(UIElement,str)
        """
        return self._onAttachPropChanged

    @property
    def OnLayoutPropChanged(self) -> Event:
        """
        Para 1:UIElement object

        Para 2:property name

        :return: Event(UIElement,str)
        """
        return self._onLayoutPropChanged

    @property
    def OnNormalPropChanged(self) -> Event:
        """
        Para 1:UIElement object

        Para 2:property name

        :return: Event(UIElement,str)
        """
        return self._onNormalPropChanged
    # ------------Legacy------------


_ElemItType = Callable[[UIElement], Iterable[UIElement]]


def GetChildren(elemt: UIElement) -> Collection[UIElement]:
    return elemt.GetChildren()


def IsLeaf(elemt: UIElement) -> bool:
    return elemt.IsLeaf()


def ShowInLTree(elemt: UIElement) -> bool:
    return elemt.ShowInLTree()


PreItV: _ElemItType = PreItGen(GetChildren)
PostItV: _ElemItType = PostItGen(GetChildren)
LevelItV: _ElemItType = LevelItGen(GetChildren)
LeafItV: _ElemItType = LeafItGen(GetChildren, IsLeaf)
PrintVTree: Callable[[UIElement], Collection[str]] = PrintTreeGen(GetChildren)


def isSelfSubVTreeShowInVisibleVTree(elemt: UIElement):
    return elemt.IsVisible


PrintVisibleVTree: Callable[[UIElement], Collection[str]] = PrintTreeGen(
    GetChildren, isSelfSubTreeCanPrint=isSelfSubVTreeShowInVisibleVTree
)

PreItL: _ElemItType = PreItGen(GetChildren, ShowInLTree)
PostItL: _ElemItType = PostItGen(GetChildren, ShowInLTree)
LevelItL: _ElemItType = LevelItGen(GetChildren, ShowInLTree)
LeafItL: _ElemItType = LeafItGen(GetChildren, IsLeaf, ShowInLTree)
PrintLTree: Callable[[UIElement], Collection[str]] = PrintTreeGen(GetChildren, ShowInLTree)


class FocusWalker:
    def __init__(self):
        super().__init__()
        self._root: Optional[UIElement] = None
        self.seq = []
        self._curIndex: Optional[int] = None
        self._curFocused: Optional[UIElement] = None

    @property
    def CurFocused(self) -> Optional[UIElement]:
        return self._curFocused

    @CurFocused.setter
    def CurFocused(self, value: Optional[UIElement]):
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
    def Root(self) -> Optional[UIElement]:
        return self._root

    @Root.setter
    def Root(self, value: Optional[UIElement]):
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


def BubbleParentChain(cur: UIElement) -> Tuple[UIElement]:
    parents: List[UIElement] = []
    while (parent := cur.Parent) is not None:
        parents.append(parent)
        cur = parent

    return tuple(parents)


def BubbleParentIt(cur: UIElement) -> Iterable[UIElement]:
    while (parent := cur.Parent) is not None:
        yield parent
        cur = parent


def OnRenderPropChangedCallback(elemt: "UIElement", value):
    elemt.NeedRerender()


def _WidthHeightCoerceCallback(elemt: "UIElement", value):
    if isinstance(value, str):
        return value
    return max(value, 0)


UIElement.IsVisibleProp = DpProp.Register(
    "IsVisible", bool, UIElement,
    DpPropMeta(True, propChangedCallback=OnRenderPropChangedCallback))
UIElement.IsFocusedProp = DpProp.Register(
    "IsFocused", bool, UIElement,
    DpPropMeta(False, propChangedCallback=OnRenderPropChangedCallback))
UIElement.WidthProp = DpProp.Register(
    "Width", (int, str), UIElement,
    DpPropMeta(Auto, propChangedCallback=OnRenderPropChangedCallback, coerceValueCallback=_WidthHeightCoerceCallback))
UIElement.HeightProp = DpProp.Register(
    "Height", (int, str), UIElement,
    DpPropMeta(Auto, propChangedCallback=OnRenderPropChangedCallback, coerceValueCallback=_WidthHeightCoerceCallback))
UIElement.NeedRerenderEvent = RoutedEventType.Register(
    "NeedRerender", UIElement, RoutedEventArgs, RoutedStrategy.Bubble)
