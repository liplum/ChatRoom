import math
from io import StringIO

from ui.Controls import *

AreaExtendMode = str
Extend = "Extend"
Minimum = "Minimum"


class TextArea(text_control):
    TextProp: DpProp
    CursorIndexProp: DpProp

    def __init__(self, cursor_icon: str = "^", init: Optional[Iterable[str]] = None):
        super().__init__()
        self._cursorIcon = cursor_icon
        self._onCursorMove = Event(TextArea, int)
        self._onAppend = Event(TextArea, int, str)
        self._onDelete = Event(TextArea, int, str)
        self._onPreGenDistext = Event(TextArea, list)
        self._onListReplaced = Event(TextArea, list, list)
        self._onPreAppend = Event(TextArea, str, cancelable=True)
        self._areaExtendMode: AreaExtendMode = Extend
        self._maxInputsCount = unlimited
        self._locked = False
        self.OnAppend.Add(self._onAppendOrDeleteOrReplace)
        self.OnDelete.Add(self._onAppendOrDeleteOrReplace)
        self.OnListReplaced.Add(self._onAppendOrDeleteOrReplace)
        self.OnCursorMove.Add(lambda _, _2: self.on_content_changed(self))

        if init is not None:
            self.InputList = init

    def _onAppendOrDeleteOrReplace(self, _, _1, _2):
        self.on_content_changed(self)
        self.IsLayoutChanged = True
        self.NeedRerender()

    @property
    def CursorIndex(self) -> int:
        return self.GetValue(self.CursorIndexProp)

    @CursorIndex.setter
    def CursorIndex(self, value: int):
        self.SetValue(self.CursorIndexProp, value)

    @property
    def Text(self) -> List[str]:
        return self.GetValue(self.TextProp)

    @Text.setter
    def Text(self, value: List[str]):
        self.SetValue(self.TextProp, value)

    @property
    def AreaExtendMode(self):
        return self._areaExtendMode

    @AreaExtendMode.setter
    def AreaExtendMode(self, value):
        self._areaExtendMode = value

    def Measure(self):
        if not self.IsVisible:
            self.DWidth = 0
            self.DHeight = 0
            return
        num = self.InputLength + len(self.CursorIcon)
        dwidth = self.Width
        dheight = self.Height
        if dwidth == Auto:
            w = num
        else:
            w = dwidth
        if dheight == Auto:
            h = math.ceil(num / w)
        else:
            h = dheight
        self.DWidth = w
        self.DHeight = h

    def Arrange(self, width: int, height: int) -> Tuple[int, int]:
        if not self.IsVisible:
            self.RenderWidth = 0
            self.RenderHeight = 0
            return 0, 0
        num = self.InputLength + len(self.CursorIcon)
        dwidth = self.Width
        dheight = self.Height
        if dwidth == Auto:
            mode = self.AreaExtendMode
            if mode == Extend:
                w = max(num, width)
            elif mode == Minimum:
                w = min(num, width)
        else:
            w = min(dwidth, width)
        if dheight == Auto:
            if w != 0:
                dh = math.ceil(num / w)
            else:
                dh = 1
            h = min(dh, height)
        else:
            h = min(dheight, height)
        self.RenderWidth = w
        self.RenderHeight = h
        return self.RenderWidth, self.RenderHeight

    def PaintOn(self, canvas: Canvas):
        bk = BK.White if self.IsFocused else None
        fg = FG.Black if self.IsFocused else None
        drawn = self.DisplayedText()
        buf = StrWriter(canvas, 0, 0, self.RenderWidth, self.RenderHeight, autoWrap=True)
        buf.Write(drawn, bk, fg)

    def on_input(self, char: chars.char) -> IsConsumed:
        return self.Append(str(char))

    def getRenderInputList(self) -> Iterable[str]:
        return self.Text

    def Clear(self):
        if len(self.Text) != 0:
            self.InputList = []

    def Append(self, char: str) -> IsConsumed:
        if self.Locked:
            return NotConsumed
        if self.MaxInputCount != unlimited:
            if self.InputLength >= self.MaxInputCount:
                return NotConsumed
        char = str(char)
        if char == "":
            return NotConsumed
        if self.OnPreAppend(self, char):
            return NotConsumed
        self.Text.insert(self.CursorIndex, char)
        self.OnAppend(self, self.CursorIndex, char)
        self.NeedRerender()
        self.CursorIndex += 1
        return Consumed

    def Delete(self, left=True) -> bool:
        length = self.InputLength
        if length == 0:
            return False
        if left:
            if self.CursorIndex > 0:
                n = self.CursorIndex - 1
                if n < length:
                    ch = self.Text.pop(n)
                    self.OnDelete(self, self.CursorIndex, ch)
                    self.CursorIndex -= 1
        else:
            if self.CursorIndex < length:
                n = self.CursorIndex
                if n < length:
                    ch = self.Text.pop(n)
                    self.OnDelete(self, self.CursorIndex, ch)
        self.NeedRerender()
        return True

    @property
    def ShowCursor(self) -> bool:
        if self.in_container:
            return self.is_focused
        else:
            return True

    @property
    def MaxInputCount(self) -> PROP:
        return self._maxInputsCount

    @MaxInputCount.setter
    def MaxInputCount(self, value: PROP):
        if self._maxInputsCount != value:
            if value == unlimited:
                self._maxInputsCount = unlimited
            else:
                self._maxInputsCount = max(0, value)
            self.OnNormalPropChanged(self, "MaxInputCount")

    def Home(self) -> bool:
        self.CursorIndex = 0
        return True

    def Left(self, unit: int = 1) -> bool:
        self.CursorIndex -= abs(unit)
        return True

    def Right(self, unit: int = 1) -> bool:
        self.CursorIndex += abs(unit)
        return True

    def End(self) -> bool:
        self.CursorIndex = self.InputLength
        return True

    @property
    def InputLength(self) -> int:
        return len(self.Text)

    @property
    def InputList(self) -> List[str]:
        return self.Text[:]

    @property
    def InputListRaw(self):
        return self.Text

    @InputList.setter
    def InputList(self, value: Iterable[str]):
        former = self.Text
        if not isinstance(value, list):
            value = list(value)
        if self.MaxInputCount != unlimited:
            value = value[0:self.MaxInputCount]
        self.Text = value
        self.OnListReplaced(self, former, self.Text)
        self.End()

    @property
    def InputString(self) -> str:
        with StringIO() as temp:
            c = 0
            cursor = self.CursorIndex
            icon = self.CursorIcon
            for res in self.Text:
                if c == cursor:
                    temp.write(icon)
                c += 1
                temp.write(res)
            if c == cursor:
                temp.write(icon)
            return temp.getvalue()

    def DisplayedText(self) -> str:
        with StringIO() as temp:
            c = 0
            cursor = self.CursorIndex
            icon = self.CursorIcon
            for res in self.Text:
                if c == cursor:
                    temp.write(icon)
                c += 1
                temp.write(res)
            if c == cursor:
                temp.write(icon)
            return temp.getvalue()

    def Lock(self):
        self._locked = True

    def Unlock(self):
        self._locked = False

    @property
    def Locked(self) -> bool:
        return self._locked

    @property
    def CursorIcon(self) -> str:
        return self._cursorIcon

    @CursorIcon.setter
    def CursorIcon(self, value: str):
        self._cursorIcon = value

    @property
    def focusable(self) -> bool:
        return True

    @property
    def OnPreGenDistext(self) -> Event:
        """
        Para 1:TextArea object

        Para 2:the final string which will be displayed soon(list[0]=str)

        :return: Event(TextArea,list)
        """
        return self._onPreGenDistext

    @property
    def OnCursorMove(self) -> Event:
        """
        Para 1:TextArea object

        Para 2:current cursor position

        :return: Event(TextArea,int)
        """
        return self._onCursorMove

    @property
    def OnPreAppend(self) -> Event:
        """
        Para 1:TextArea object

        Para 2:Char appended

        :return: Event(TextArea,str)
        """
        return self._onPreAppend

    @property
    def OnAppend(self) -> Event:
        """
        Para 1:TextArea object

        Para 2:cursor position

        Para 3:Char appended

        :return: Event(TextArea,int,str)
        """
        return self._onAppend

    @property
    def OnDelete(self) -> Event:
        """
        Para 1:TextArea object

        Para 2:cursor position

        Para 3:Char deleted

        :return: Event(TextArea,int,str)
        """
        return self._onDelete

    @property
    def OnListReplaced(self) -> Event:
        """
        Para 1:TextArea object

        Para 2:former list

        Para 3:current list

        :return: Event(TextArea,list,list)
        """
        return self._onListReplaced


TextArea.TextProp = DpProp.Register("Text", list, TextArea, DpPropMeta(list))


def _CursorIndexCoerceCallback(ta: TextArea, value):
    return min(max(0, value), ta.InputLength)


def _OnCursorIndexChangedCallback(elemt: "UIElement", value):
    elemt.OnCursorMove(elemt, value)
    elemt.NeedRerender()


TextArea.CursorIndexProp = DpProp.Register(
    "CursorIndex", int, TextArea,
    DpPropMeta(
        0, False,
        coerceValueCallback=_CursorIndexCoerceCallback,
        propChangedCallback=_OnCursorIndexChangedCallback))
