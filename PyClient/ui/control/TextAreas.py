import math
from typing import List

from ui.Controls import *


class TextArea(text_control):

    def __init__(self, cursor_icon: str = "^", init: Optional[Iterable[str]] = None):
        super().__init__()
        self._inputList: List[str] = []
        self._cursorIcon = cursor_icon
        self._cursor: int = 0
        self._onCursorMove = Event(TextArea, int, int)
        self._onAppend = Event(TextArea, int, str)
        self._onDelete = Event(TextArea, int, str)
        self._onPreGenDistext = Event(TextArea, list)
        self._onListReplaced = Event(TextArea, list, list)
        self._onPreAppend = Event(TextArea, str, cancelable=True)
        self._rWidth = 0
        self._rHeight = 0
        self._maxInputsCount = unlimited
        self._locked = False

        self.OnAppend.Add(self._onAppendOrDeleteOrReplace)
        self.OnDelete.Add(self._onAppendOrDeleteOrReplace)
        self.OnListReplaced.Add(self._onAppendOrDeleteOrReplace)
        self.OnCursorMove.Add(lambda _, _1, _2: self.on_content_changed(self))

        if init is not None:
            self.InputList = init

    def _onAppendOrDeleteOrReplace(self, _, _1, _2):
        self.on_content_changed(self)
        self.IsLayoutChanged = True

    def Measure(self):
        num = self.InputLength + len(self.CursorIcon)
        dwidth = self.width
        dheight = self.height
        if dwidth == auto:
            w = num
        else:
            w = dwidth
        if dheight == auto:
            h = math.ceil(num / w)
        else:
            h = dheight
        self._rWidth = w
        self._rHeight = h

    def Arrange(self, width: int, height: int):
        if not self.IsLayoutChanged:
            return
        self.IsLayoutChanged = False
        num = self.InputLength + len(self.CursorIcon)
        dwidth = self.width
        dheight = self.height
        oldw = self._rWidth
        oldh = self._rHeight
        if dwidth == auto:
            w = min(num, width)
        else:
            w = min(dwidth, width)
        if dheight == auto:
            h = min(math.ceil(num / w), height)
        else:
            h = min(dheight, height)
        self._rWidth = w
        self._rHeight = h
        if oldw != w or oldh != h:
            self.OnLayoutChanged(self)

    def PaintOn(self, canvas: Canvas):
        bk = BK.White if self.is_focused else None
        fg = FG.Black if self.is_focused else None
        drawn = self.InputString
        buf = StrWriter(canvas, 0, 0, self.render_width, self.render_height, autoWrap=True)
        buf.Write(drawn, bk, fg)

    def on_input(self, char: chars.char) -> IsConsumed:
        return self.Append(str(char))

    def getRenderInputList(self) -> Iterable[str]:
        return self._inputList

    def Clear(self):
        if len(self._inputList) != 0:
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
        self._inputList.insert(self.Cursor, char)
        self.OnAppend(self, self.Cursor, char)
        self.Cursor += 1
        return Consumed

    def Delete(self, left=True) -> bool:
        length = self.InputLength
        if left:
            if self.Cursor > 0:
                n = self.Cursor - 1
                if n < length:
                    ch = self._inputList.pop(n)
                    self.OnDelete(self, self.Cursor, ch)
                    self.Cursor -= 1
        else:
            if self.Cursor < length:
                n = self.Cursor
                if n < length:
                    ch = self._inputList.pop(n)
                    self.OnDelete(self, self.Cursor, ch)
        return True

    @property
    def ShowCursor(self) -> bool:
        if self.in_container:
            return self.is_focused
        else:
            return True

    @property
    def Cursor(self):
        return self._cursor

    @Cursor.setter
    def Cursor(self, value):
        list_len = self.InputLength
        former = self._cursor
        current = min(max(0, value), list_len)
        if former != current:
            self._cursor = current
            self.OnCursorMove(self, former, current)

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
        self.Cursor = 0
        return True

    def Left(self, unit: int = 1) -> bool:
        self.Cursor -= abs(unit)
        return True

    def Right(self, unit: int = 1) -> bool:
        self.Cursor += abs(unit)
        return True

    def End(self) -> bool:
        self.Cursor = self.InputLength
        return True

    @property
    def InputLength(self) -> int:
        return len(self._inputList)

    @property
    def InputList(self) -> List[str]:
        return self._inputList[:]

    @InputList.setter
    def InputList(self, value: Iterable[str]):
        former = self._inputList
        if not isinstance(value, list):
            value = list(value)
        if self.MaxInputCount != unlimited:
            value = value[0:self.MaxInputCount]
        self._inputList = value
        self.OnListReplaced(self, former, self._inputList)
        self.End()

    @property
    def InputString(self) -> str:
        return utils.compose(self._inputList, connector='')

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
    def render_height(self) -> int:
        return self._rHeight

    @property
    def render_width(self) -> int:
        return self._rWidth

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

        Para 2:former cursor position

        Para 3:current cursor position

        :return: Event(TextArea,int,int)
        """
        return self._onCursorMove

    @property
    def OnPreAppend(self) -> Event:
        """
        Para 1:TextArea object

        Para 2:char appended

        :return: Event(TextArea,str)
        """
        return self._onPreAppend

    @property
    def OnAppend(self) -> Event:
        """
        Para 1:TextArea object

        Para 2:cursor position

        Para 3:char appended

        :return: Event(TextArea,int,str)
        """
        return self._onAppend

    @property
    def OnDelete(self) -> Event:
        """
        Para 1:TextArea object

        Para 2:cursor position

        Para 3:char deleted

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
