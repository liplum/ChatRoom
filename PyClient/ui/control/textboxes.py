from itertools import islice

from ui.control.TextAreas import TextArea
from ui.Controls import *
from ui.outputs import buffer, CmdBkColor, CmdFgColor


class textbox(TextArea):

    def __init__(self, cursor_icon: str = "^", init: Optional[Iterable[str]] = None):
        super().__init__(cursor_icon, init)
        self._space_placeholder = " "

    def cache_layout(self):
        if not self.IsLayoutChanged:
            return
        self.IsLayoutChanged = False
        if self.width == auto:
            self._rWidth = self.input_count + len(self.cursor_icon)
        else:
            self._rWidth = self.width

    def Arrange(self, width: Optional[int] = None, height: Optional[int] = None):
        if not self.IsLayoutChanged:
            return
        self.IsLayoutChanged = False
        if self.width == auto:
            self._rWidth = min(self.InputLength + len(self.CursorIcon), canvas.Width)
        else:
            self._rWidth = min(self.width, canvas.Width)

    def paint_on(self, buf: buffer):
        if self.IsLayoutChanged:
            self.cache_layout()
        if self.left_margin > 0:
            buf.addtext(utils.repeat(' ', self.left_margin), end='')
        bk = CmdBkColor.White if self.is_focused else None
        fg = CmdFgColor.Black if self.is_focused else None
        drawn = self.limited_distext
        if self.MaxInputCount != unlimited:
            max_render_width = min(self.MaxInputCount, self.render_width)
            drawn = utils.fillto(drawn, self.space_placeholder, max_render_width)
        elif len(drawn) < self.render_width:
            drawn = utils.fillto(drawn, self.space_placeholder, self.width)
        buf.addtext(self._render_chars(drawn), end='', fgcolor=fg, bkcolor=bk)

    def PaintOn(self, canvas: Canvas):
        bk = BK.White if self.is_focused else None
        fg = FG.Black if self.is_focused else None
        drawn = self.limited_distext
        if self.MaxInputCount != unlimited:
            max_render_width = min(self.MaxInputCount, self.render_width)
            drawn = utils.fillto(drawn, self.space_placeholder, max_render_width)
        elif len(drawn) < self.render_width:
            drawn = utils.fillto(drawn, self.space_placeholder, self.width)
        buf = StrWriter(canvas, 0, 0, self.render_width, self.render_height, autoWrap=True)
        buf.Write(drawn, bk, fg)

    @property
    def space_placeholder(self) -> str:
        return self._space_placeholder

    @space_placeholder.setter
    def space_placeholder(self, value: str):
        value = str(value)[0]
        if value != "" and self._space_placeholder != value:
            self._space_placeholder = value
            self.on_prop_changed(self, "space_placeholder")

    @property
    def limited_distext(self):
        if self.width == auto:
            return self.distext
        w = self.render_width
        cursor_pos = self.Cursor
        start = cursor_pos - w // 2  # may be negative
        end = cursor_pos + w // 2  # may be over length of all inputs
        length = self.InputLength
        if start < 0:
            left_leftover = abs(start)
            start = 0
            end += left_leftover
            end = min(end, length)
        if end > length:
            right_leftover = end - length
            end = length
            start -= right_leftover
            start = max(start, 0)
        cursor_icon = self.CursorIcon
        show_cursor = self.ShowCursor
        with StringIO() as s:
            cur = start
            for char in islice(self.getRenderInputList(), start, end):
                if cur == cursor_pos and show_cursor:
                    s.write(cursor_icon)
                s.write(char)
                cur += 1
            if cur == cursor_pos and show_cursor:
                s.write(cursor_icon)

            res = s.getvalue()
            displayed = [res]
            self.OnPreGenDistext(self, [res])
            return displayed[0]

    @property
    def distext(self) -> str:
        cursor_pos = self.Cursor
        show_cursor = self.ShowCursor
        cursor_icon = self.CursorIcon
        with StringIO() as s:
            cur = 0
            for char in self.getRenderInputList():
                if cur == cursor_pos and show_cursor:
                    s.write(cursor_icon)
                s.write(char)
                cur += 1
            if cur == cursor_pos and show_cursor:
                s.write(cursor_icon)

            res = s.getvalue()
            displayed = [res]
            self.OnPreGenDistext(self, [res])
            return displayed[0]

    def addtext(self, text: str):
        """
        Not raise on_append Event
        :param text:
        :return:
        """
        self._inputList.insert(self.Cursor, text)
        self.Cursor += len(text)

    def rmtext(self, count: int):
        if count <= 0:
            return
        cursor_pos = self.Cursor
        while count > 0:
            self._inputList.pop(cursor_pos)
            cursor_pos -= 1
            count -= 1
        self.Cursor = cursor_pos

    def __repr__(self) -> str:
        return f"<textbox {self.inputs}>"


TextBox = textbox
