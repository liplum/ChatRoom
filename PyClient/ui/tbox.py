from io import StringIO
from typing import List

import utils
from events import event
from ui.ctrl import control
from ui.outputs import CmdBkColor, CmdFgColor
from ui.outputs import buffer


class textbox(control):

    @property
    def focused(self) -> bool:
        return self._focused

    def on_focused(self):
        self._focused = True

    def on_lost_focus(self):
        self._focused = False

    @property
    def focusable(self) -> bool:
        return True

    @property
    def width(self) -> int:
        return self._width + len(self.cursor_icon)

    @width.setter
    def width(self, value: int):
        self._width = max(self._min_width, value)
        self.width_limited = True

    @property
    def height(self) -> int:
        return self._height

    @property
    def width_limited(self) -> bool:
        return self._width_limited

    @width_limited.setter
    def width_limited(self, value):
        self._width_limited = bool(value)

    def draw_on(self, buf: buffer):
        bk = CmdBkColor.White if self.focused else None
        fg = CmdFgColor.Black if self.focused else None
        buf.addtext(self.limited_distext, end='', fgcolor=fg, bkcolor=bk)

    def __init__(self, cursor_icon: str = "^"):
        super().__init__()
        self._input_list: List[str] = []
        self.cursor_icon = cursor_icon
        self._cursor: int = 0
        self._cursor: int = 0
        self._on_cursor_move = event()
        self._on_append = event()
        self._on_delete = event()
        self._on_gen_distext = event()
        self._on_list_replace = event()
        self._min_width = 6
        self._width = self._min_width
        self._width_limited = False
        self._height = 1
        self._focused = False

    @property
    def on_gen_distext(self) -> event:
        """
        Para 1:textbox object

        Para 2:the final string which will be displayed soon(list[0]=str)

        :return: event(textbox,list)
        """
        return self._on_gen_distext

    @property
    def on_cursor_move(self) -> event:
        """
        Para 1:textbox object

        Para 2:former cursor position

        Para 3:current cursor position

        :return: event(textbox,int,int)
        """
        return self._on_cursor_move

    @property
    def on_append(self) -> event:
        """
        Para 1:textbox object

        Para 2:cursor position

        Para 3:char appended

        :return: event(textbox,int,str)
        """
        return self._on_append

    @property
    def on_delete(self) -> event:
        """
        Para 1:textbox object

        Para 2:cursor position

        Para 3:char deleted

        :return: event(textbox,int,str)
        """
        return self._on_delete

    @property
    def on_list_replace(self) -> event:
        """
        Para 1:textbox object

        Para 2:former list

        Para 3:current list

        :return: event(textbox,list,list)
        """
        return self._on_list_replace

    @property
    def input_list(self) -> List[str]:
        return self._input_list[:]

    @property
    def input_count(self) -> int:
        return len(self._input_list)

    @input_list.setter
    def input_list(self, value):
        former = self._input_list
        if isinstance(value, list):
            self._input_list = value[:]
        else:
            self._input_list = list(value)
        self.cursor = 0
        self.on_list_replace(self, former, self._input_list)

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

    def home(self):
        self.cursor = 0

    def left(self):
        self.cursor -= 1

    def right(self):
        self.cursor += 1

    def end(self):
        self.cursor = self.input_count

    @property
    def limited_distext(self):
        if not self.width_limited:
            return self.distext
        w = max(self._width, 3)
        cursor_pos = self._cursor
        start = max(0, cursor_pos - w // 2)
        end = min(self.input_count, cursor_pos + w // 2)
        with StringIO() as s:
            cur = start
            for char in self._input_list[start:end]:
                if cur == cursor_pos:
                    s.write(self.cursor_icon)
                s.write(char)
                cur += 1
            if cur == cursor_pos:
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
            for char in self._input_list:
                if cur == cursor_pos:
                    s.write(self.cursor_icon)
                s.write(char)
                cur += 1
            if cur == cursor_pos:
                s.write(self.cursor_icon)

            res = s.getvalue()
            displayed = [res]
            self.on_gen_distext(self, [res])
            return displayed[0]

    def append(self, char):
        self._input_list.insert(self.cursor, char)
        self.on_append(self, self.cursor, char)
        self.cursor += 1

    def addtext(self, text: str):
        """
        Not raise on_append event
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

    def delete(self, left=True):
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
