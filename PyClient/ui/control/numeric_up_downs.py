import keys
import utils
from ui.ctrl import *
from ui.outputs import tintedtxt, CmdBkColor, CmdFgColor
from ui.themes import plus_minus_theme

operator = plus_minus_theme("-", "+")
arrow = plus_minus_theme("<", ">")


def sign(number: int):
    return 1 if number >= 0 else -1


class numeric_up_down(control):

    def __init__(self, minv: Optional[int] = None, maxv: Optional[int] = None, pg_updown_step: Optional[int] = 10,
                 theme: plus_minus_theme = operator):
        super().__init__()
        self.theme = theme
        self._number = 0
        if minv and maxv:
            _min = min(minv, maxv)
            _max = max(minv, maxv)
        else:
            _min = minv
            _max = maxv
        self._min_value: Optional[int] = None
        self._max_value: Optional[int] = None
        self.min_value = _min
        self.max_value = _max
        self._max_value_str = ""
        self._min_value_str = ""
        self._r_width = 0

    @property
    def max_value(self) -> Optional[int]:
        return self._max_value

    @max_value.setter
    def max_value(self, value: Optional[int]):
        if self.min_value:
            value = max(self.min_value, value)
        if self._max_value != value:
            self._max_value = value
            if value:
                self._max_value_str = str(value)
            self.on_prop_changed(self, "max_value")

    @property
    def min_value(self) -> Optional[int]:
        return self._min_value

    @min_value.setter
    def min_value(self, value: Optional[int]):
        if self.max_value:
            value = min(self.max_value, value)
        if self._min_value != value:
            self._min_value = value
            if value:
                self._min_value_str = str(value)
            self.on_prop_changed(self, "min_value")

    @property
    def max_number_len(self) -> int:
        return max(len(self._max_value_str), len(self._min_value_str))

    def cache_layout(self):
        if self.width == auto:
            if self.max_value:
                self._r_width = self.max_number_len + 2
            else:
                self._r_width = 2 + 4
        else:
            self._r_width = self.width

    def paint_on(self, buf: buffer):
        rw = self.render_width
        theme = self.theme
        if rw == 0:
            return
        with StringIO() as s:
            utils.repeatIO(s, ' ', self.left_margin)
            if rw == 1:
                minus = theme.minus
                if self.is_focused:
                    minus = tintedtxt(minus, fgcolor=CmdFgColor.Black, bkcolor=CmdBkColor.White)
                s.write(minus)
            if rw == 2:
                minus = theme.minus
                plus = theme.plus
                if self.is_focused:
                    minus = tintedtxt(minus, fgcolor=CmdFgColor.Black, bkcolor=CmdBkColor.White)
                if self.is_focused:
                    plus = tintedtxt(plus, fgcolor=CmdFgColor.Black, bkcolor=CmdBkColor.White)
                s.write(minus)
                s.write(plus)
            else:
                minus = theme.minus
                plus = theme.plus
                if self.is_focused:
                    minus = tintedtxt(minus, fgcolor=CmdFgColor.Black, bkcolor=CmdBkColor.White)
                if self.is_focused:
                    plus = tintedtxt(plus, fgcolor=CmdFgColor.Black, bkcolor=CmdBkColor.White)
                s.write(minus)

                area = rw - 2
                num = self.number
                num_str = str(num)
                num_strl = len(num_str)
                if area < num_strl:
                    rest = num_strl - area
                    s.write(num_str[:-rest])
                elif area == num_strl:
                    s.write(num_str)
                else:
                    rest = area - num_strl
                    utils.repeatIO(s, ' ', rest)
                    s.write(num_str)

                s.write(plus)

            buf.addtext(s.getvalue())

    @property
    def number(self) -> int:
        return self._number

    @number.setter
    def number(self, value: int):
        if self.max_value:
            value = min(self.max_value, value)
        if self.min_value:
            value = max(self.min_value, value)
        if self._number != value:
            self._number = value
            self.on_content_changed(self)

    def on_input(self, char: chars.char) -> IsConsumed:
        if keys.k_left == char:
            return self.decrease()
        elif keys.k_right == char:
            return self.increase()
        else:
            return NotConsumed

    def increase(self, number: int = 1) -> bool:
        number = abs(number)
        maxv = self.max_value
        res = self.number + number
        if maxv and res > maxv:
            final = min(res, maxv)
            if final != self.number:
                self.number = final
                return True
            else:
                return False
        else:
            self.number = res
            return True

    def decrease(self, number: int = 1) -> bool:
        number = abs(number)
        minv = self.min_value
        res = self.number - number
        if minv and res < minv:
            final = max(res, minv)
            if final != self.number:
                self.number = final
                return True
            else:
                return False
        else:
            self.number = res
            return True

    @property
    def focusable(self) -> bool:
        return True

    @property
    def height(self) -> int:
        return 1

    @height.setter
    def height(self, value: int):
        if value != auto:
            value = 1
        self._height = value

    @property
    def render_height(self) -> int:
        return 1

    @property
    def render_width(self) -> int:
        return self._r_width
