from itertools import islice
from typing import List

from ui.controls import *
from ui.outputs import buffer, CmdBkColor, CmdFgColor
from ui.shared import IsConsumed, NotConsumed, Consumed


class textbox(text_control):

    def __init__(self, cursor_icon: str = "^", init: Optional[Iterable[str]] = None):
        super().__init__()
        self._input_list: List[str] = []
        self.cursor_icon = cursor_icon
        self._cursor: int = 0
        self._on_cursor_move = Event(textbox, int, int)
        self._on_append = Event(textbox, int, str)
        self._on_delete = Event(textbox, int, str)
        self._on_gen_distext = Event(textbox, list)
        self._on_list_replace = Event(textbox, list, list)
        self._on_pre_append = Event(textbox, str, cancelable=True)
        self._r_width = 0
        self._r_height = 1
        self._max_inputs_count = unlimited
        self._space_placeholder = " "
        self._locked = False

        def on_append_or_delete_or_replace(_, _1, _2):
            self.on_content_changed(self)
            self.IsLayoutChanged = True

        self._on_append.Add(on_append_or_delete_or_replace)
        self._on_delete.Add(on_append_or_delete_or_replace)
        self._on_cursor_move.Add(lambda _, _1, _2: self.on_content_changed(self))
        self._on_list_replace.Add(on_append_or_delete_or_replace)

        if init is not None:
            self.input_list = init

    def cache_layout(self):
        if not self.IsLayoutChanged:
            return
        self.IsLayoutChanged = False
        if self.width == auto:
            self._r_width = self.input_count + len(self.cursor_icon)
        else:
            self._r_width = self.width

    def Arrange(self, canvas: Canvas):
        if not self.IsLayoutChanged:
            return
        self.IsLayoutChanged = False
        num = self.input_count + len(self.cursor_icon)
        if self.width == auto:
            w = min(num, canvas.Width)
            if self.height == auto:
                h = min(int(num / w + 1), canvas.Height)
            else:
                h = min(self.height, canvas.Height)
        else:
            w = min(self.width, canvas.Width)
            if self.height == auto:
                h = min(int(num / w + 1), canvas.Height)
            else:
                h = min(self.height, canvas.Height)
        self._r_height = h
        self._r_width = w

    @property
    def render_width(self) -> int:
        return self._r_width

    @property
    def render_height(self) -> int:
        return self._r_height

    @property
    def show_cursor(self) -> bool:
        if self.in_container:
            return self.is_focused
        else:
            return True

    @property
    def focusable(self) -> bool:
        return True

    @property
    def max_inputs_count(self) -> PROP:
        return self._max_inputs_count

    @max_inputs_count.setter
    def max_inputs_count(self, value: PROP):
        if self._max_inputs_count != value:
            if value == unlimited:
                self._max_inputs_count = unlimited
            else:
                self._max_inputs_count = max(0, value)
            self.on_prop_changed(self, "max_inputs_count")

    def paint_on(self, buf: buffer):
        if self.IsLayoutChanged:
            self.cache_layout()
        if self.left_margin > 0:
            buf.addtext(utils.repeat(' ', self.left_margin), end='')
        bk = CmdBkColor.White if self.is_focused else None
        fg = CmdFgColor.Black if self.is_focused else None
        drawn = self.limited_distext
        if self.max_inputs_count != unlimited:
            max_render_width = min(self.max_inputs_count, self.render_width)
            drawn = utils.fillto(drawn, self.space_placeholder, max_render_width)
        elif len(drawn) < self.render_width:
            drawn = utils.fillto(drawn, self.space_placeholder, self.width)
        buf.addtext(self._render_chars(drawn), end='', fgcolor=fg, bkcolor=bk)

    def PaintOn(self, canvas: Canvas):
        if self.IsLayoutChanged:
            self.Arrange(canvas)
        bk = BK.White if self.is_focused else None
        fg = FG.Black if self.is_focused else None
        drawn = self.limited_distext
        if self.max_inputs_count != unlimited:
            max_render_width = min(self.max_inputs_count, self.render_width)
            drawn = utils.fillto(drawn, self.space_placeholder, max_render_width)
        elif len(drawn) < self.render_width:
            drawn = utils.fillto(drawn, self.space_placeholder, self.width)
        buf = StrWriter(canvas, 0, 0, self.render_width, self.render_height, autoWrap=True)
        buf.Write(drawn, bk, fg)

    def on_input(self, char: chars.char) -> IsConsumed:
        return self.append(str(char))

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
    def on_gen_distext(self) -> Event:
        """
        Para 1:textbox object

        Para 2:the final string which will be displayed soon(list[0]=str)

        :return: Event(textbox,list)
        """
        return self._on_gen_distext

    @property
    def on_cursor_move(self) -> Event:
        """
        Para 1:textbox object

        Para 2:former cursor position

        Para 3:current cursor position

        :return: Event(textbox,int,int)
        """
        return self._on_cursor_move

    @property
    def on_pre_append(self) -> Event:
        """
        Para 1:textbox object

        Para 2:char appended

        :return: Event(textbox,str)
        """
        return self._on_pre_append

    @property
    def on_append(self) -> Event:
        """
        Para 1:textbox object

        Para 2:cursor position

        Para 3:char appended

        :return: Event(textbox,int,str)
        """
        return self._on_append

    @property
    def on_delete(self) -> Event:
        """
        Para 1:textbox object

        Para 2:cursor position

        Para 3:char deleted

        :return: Event(textbox,int,str)
        """
        return self._on_delete

    @property
    def on_list_replace(self) -> Event:
        """
        Para 1:textbox object

        Para 2:former list

        Para 3:current list

        :return: Event(textbox,list,list)
        """
        return self._on_list_replace

    @property
    def input_list(self) -> List[str]:
        return self._input_list[:]

    @property
    def input_count(self) -> int:
        return len(self._input_list)

    @input_list.setter
    def input_list(self, value: Iterable[str]):
        former = self._input_list
        if not isinstance(value, list):
            value = list(value)
        if self.max_inputs_count != unlimited:
            value = value[0:self.max_inputs_count]
        self._input_list = value
        self.on_list_replace(self, former, self._input_list)
        self.end()

    @property
    def inputs(self) -> str:
        return utils.compose(self.input_list, connector='')

    def clear(self):
        if len(self._input_list) != 0:
            self.input_list = []

    @property
    def cursor(self):
        return self._cursor

    @cursor.setter
    def cursor(self, value):
        list_len = len(self._input_list)
        former = self._cursor
        current = min(max(0, value), list_len)
        if former != current:
            self._cursor = current
            self.on_cursor_move(self, former, current)

    def home(self) -> bool:
        self.cursor = 0
        return True

    def left(self, unit: int = 1) -> bool:
        self.cursor -= abs(unit)
        return True

    def right(self, unit: int = 1) -> bool:
        self.cursor += abs(unit)
        return True

    def end(self) -> bool:
        self.cursor = self.input_count
        return True

    @property
    def render_input_list(self) -> Iterable[str]:
        return self._input_list

    @property
    def limited_distext(self):
        if self.width == auto:
            return self.distext
        w = self.render_width
        cursor_pos = self.cursor
        start = cursor_pos - w // 2  # may be negative
        end = cursor_pos + w // 2  # may be over length of all inputs
        if start < 0:
            left_leftover = abs(start)
            start = 0
            end += left_leftover
            end = min(end, self.input_count)
        if end > self.input_count:
            right_leftover = end - self.input_count
            end = self.input_count
            start -= right_leftover
            start = max(start, 0)

        with StringIO() as s:
            cur = start
            for char in islice(self.render_input_list, start, end):
                if cur == cursor_pos and self.show_cursor:
                    s.write(self.cursor_icon)
                s.write(char)
                cur += 1
            if cur == cursor_pos and self.show_cursor:
                s.write(self.cursor_icon)

            res = s.getvalue()
            displayed = [res]
            self.on_gen_distext(self, [res])
            return displayed[0]

    @property
    def distext(self) -> str:
        cursor_pos = self._cursor
        with StringIO() as s:
            cur = 0
            for char in self.render_input_list:
                if cur == cursor_pos and self.show_cursor:
                    s.write(self.cursor_icon)
                s.write(char)
                cur += 1
            if cur == cursor_pos and self.show_cursor:
                s.write(self.cursor_icon)

            res = s.getvalue()
            displayed = [res]
            self.on_gen_distext(self, [res])
            return displayed[0]

    def append(self, char: str) -> IsConsumed:
        if self.locked:
            return NotConsumed
        if self.max_inputs_count != unlimited:
            if self.input_count >= self.max_inputs_count:
                return NotConsumed
        char = str(char)
        if char == "":
            return NotConsumed
        if self.on_pre_append(self, char):
            return NotConsumed
        self._input_list.insert(self.cursor, char)
        self.on_append(self, self.cursor, char)
        self.cursor += 1
        return Consumed

    def addtext(self, text: str):
        """
        Not raise on_append Event
        :param text:
        :return:
        """
        self._input_list.insert(self.cursor, text)
        self.cursor += len(text)

    def rmtext(self, count: int):
        if count <= 0:
            return
        cursor_pos = self.cursor
        while count > 0:
            self._input_list.pop(cursor_pos)
            cursor_pos -= 1
            count -= 1
        self.cursor = cursor_pos

    def delete(self, left=True) -> bool:
        if left:
            if self.cursor > 0:
                n = self.cursor - 1
                if n < len(self._input_list):
                    ch = self._input_list.pop(n)
                    self.on_delete(self, self.cursor, ch)
                    self.cursor -= 1
        else:
            if self.cursor < self.input_count:
                n = self.cursor
                if n < len(self._input_list):
                    ch = self._input_list.pop(n)
                    self.on_delete(self, self.cursor, ch)
        return True

    def lock(self):
        self._locked = True

    def unlock(self):
        self._locked = False

    @property
    def locked(self) -> bool:
        return self._locked

    def __repr__(self) -> str:
        return f"<textbox {self.inputs}>"
