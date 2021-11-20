from io import StringIO
from typing import List, NoReturn, Union

import keys
import utils
from ui.ctrl import *
from ui.outputs import buffer, CmdBkColor, CmdFgColor


class label(control):
    def __init__(self, content: Union[content_getter, str]):
        super().__init__()
        if isinstance(content, str):
            self.content = lambda: content
        else:
            self.content = content
        self._width_limited = False
        self._min_width = 1
        self._width = 1

    @property
    def width(self) -> int:
        if self.width_limited:
            return self._width
        else:
            return len(self.content())

    @property
    def height(self) -> int:
        return 1

    @property
    def focusable(self) -> bool:
        return False

    def draw_on(self, buf: buffer):
        content = self.content()
        if self.width_limited:
            if self.width < len(content):
                content = content[0:self.width]
            elif self.width > len(content):
                content = utils.fillto(content, " ", self.width)
        buf.addtext(content, end="")

    @property
    def width_limited(self) -> bool:
        return self._width_limited

    @width_limited.setter
    def width_limited(self, value):
        self._width_limited = bool(value)

    @width.setter
    def width(self, value: int):
        self._width = max(self._min_width, value)
        self.width_limited = True


def fix_text_label(text: str) -> label:
    return label(CGT_fix_text(text))


class textbox(control):

    @property
    def render_width(self) -> int:
        return self.input_count + len(self.cursor_icon)

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

    @property
    def max_inputs_count(self) -> int:
        return self._max_inputs_count

    @max_inputs_count.setter
    def max_inputs_count(self, value: int):
        self._max_inputs_count = max(0, value)
        self.inputs_count_limited = True

    @property
    def inputs_count_limited(self) -> bool:
        return self._inputs_count_limited

    @inputs_count_limited.setter
    def inputs_count_limited(self, value: bool):
        self._inputs_count_limited = value

    def draw_on(self, buf: buffer):
        bk = CmdBkColor.White if self.is_focused else None
        fg = CmdFgColor.Black if self.is_focused else None
        drawn = self.limited_distext
        if len(drawn) < self.width:
            drawn = utils.fillto(drawn, self.space_placeholder, self.width)
        buf.addtext(drawn, end='', fgcolor=fg, bkcolor=bk)

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
        self._inputs_count_limited = False
        self._max_inputs_count = 10
        self._space_placeholder = " "

        self._on_append.add(lambda _, _1, _2: self.on_content_changed(self))
        self._on_delete.add(lambda _, _1, _2: self.on_content_changed(self))
        self._on_cursor_move.add(lambda _, _1, _2: self.on_content_changed(self))
        self._on_list_replace.add(lambda _, _1, _2: self.on_content_changed(self))

    def on_input(self, char: chars.char) -> bool:
        return self.append(char)

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
            for char in self._input_list[start:end]:
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
            for char in self._input_list:
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

    def append(self, char) -> bool:
        if self.inputs_count_limited:
            if self.input_count >= self.max_inputs_count:
                return False
        char = str(char)
        self._input_list.insert(self.cursor, char)
        self.on_append(self, self.cursor, char)
        self.cursor += 1
        return True

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


class button(control):
    def draw_on(self, buf: buffer):
        bk = CmdBkColor.White if self.is_focused else None
        fg = CmdFgColor.Black if self.is_focused else None
        buf.addtext(self.distext, end='', fgcolor=fg, bkcolor=bk)

    @property
    def distext(self) -> str:
        if self.margin > 0:
            if self.is_focused:
                margin = utils.repeat(" ", self.margin)
                return f"{margin}{self.content()}{margin}"
            else:
                margin = utils.repeat(" ", self.margin - 2)
                return f"[{margin}{self.content()}{margin}]"

        else:
            return self.content()

    def __init__(self, content:Union[content_getter, str], on_press: Callable[[], NoReturn]):
        super().__init__()
        if isinstance(content, str):
            self.content = lambda: content
        else:
            self.content = content
        self._margin = 0
        self.on_press_func = on_press

    def press(self):
        self.on_press_func()

    def on_input(self, char: chars.char) -> bool:
        if keys.k_enter == char:
            self.on_press_func()
            return True
        elif chars.c_esc == char:
            self.on_exit_focus(self)
            return True
        return False

    @property
    def margin(self) -> int:
        return self._margin

    @margin.setter
    def margin(self, value: int):
        value = max(0, value)
        self._margin = value

    @property
    def width(self) -> int:
        return len(self.content()) + 2 * self.margin

    @width.setter
    def width(self, value: int):
        pass

    @property
    def height(self) -> int:
        return 1

    @height.setter
    def height(self, value: int):
        pass

    @property
    def focusable(self) -> bool:
        return True
