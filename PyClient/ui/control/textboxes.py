from typing import Optional, Iterable, List

import chars
import utils
from GLOBAL import StringIO
from events import event
from ui.ctrl import auto, unlimited, PROP, text_control
from ui.outputs import buffer, CmdBkColor, CmdFgColor
from ui.shared import IsConsumed, NotConsumed, Consumed


class textbox(text_control):

    def __init__(self, cursor_icon: str = "^", init: Optional[Iterable[str]] = None):
        super().__init__()
        self._input_list: List[str] = []
        self.cursor_icon = cursor_icon
        self._cursor: int = 0
        self._on_cursor_move = event()
        self._on_append = event()
        self._on_delete = event()
        self._on_gen_distext = event()
        self._on_list_replace = event()
        self._on_pre_append = event(cancelable=True)
        self._width = auto
        self._r_width = 0
        self._max_inputs_count = unlimited
        self._space_placeholder = " "
        self._locked = False

        def on_append_or_delete_or_replace(_, _1, _2):
            self.on_content_changed(self)
            self._layout_changed = True

        self._on_append.add(on_append_or_delete_or_replace)
        self._on_delete.add(on_append_or_delete_or_replace)
        self._on_cursor_move.add(lambda _, _1, _2: self.on_content_changed(self))
        self._on_list_replace.add(on_append_or_delete_or_replace)

        if init is not None:
            self.input_list = init

    def cache_layout(self):
        if not self._layout_changed:
            return
        self._layout_changed = False
        if self.width == auto:
            self._r_width = self.input_count + len(self.cursor_icon)
        else:
            self._r_width = self.width

    @property
    def render_width(self) -> int:
        return self._r_width

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
    def width(self) -> PROP:
        return self._width

    @width.setter
    def width(self, value: PROP):
        if self.width != value:
            if value == auto:
                self._width = auto
            else:
                self._width = max(0, value)
            self.on_prop_changed(self, "width")

    @property
    def height(self) -> int:
        return 1

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
        if self._layout_changed:
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
    def on_pre_append(self) -> event:
        """
        Para 1:textbox object

        Para 2:char appended

        :return: event(textbox,str)
        """
        return self._on_pre_append

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
            # TODO:Use itertools.islice
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
