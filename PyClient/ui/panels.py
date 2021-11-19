from typing import Optional, Tuple, Set, List

import keys
import utils
from ui.ctrl import *

CTRL = TypeVar('CTRL', covariant=True, bound=control)


class panel(control, ABC):
    def __init__(self):
        super().__init__()
        self._elements: Set[CTRL] = set()
        self._focused = False
        self._cur_focused: Optional[CTRL] = None
        self._on_elements_changed = event()
        self._on_focused_changed = event()
        self._layout_changed = True

        self.on_prop_changed.add(self._on_layout_changed)

        self._on_elements_changed.add(lambda _, _1, _2: self.on_content_changed(self))
        self._on_focused_changed.add(lambda _, _1, _2: self.on_content_changed(self))

    def _on_layout_changed(self, self2, prop_name):
        self.on_content_changed(self)
        self._layout_changed = True

    def _on_elemt_exit_focus(self, elemt) -> bool:
        """

        :param elemt:
        :return: whether current focused control exited
        """
        if elemt == self.cur_focused:
            self.cur_focused = None
            return True
        return False

    def cache_layout(self):
        pass

    def add(self, elemt: control):
        if elemt not in self._elements:
            self._elements.add(elemt)
            elemt.in_container = True
            elemt.on_content_changed.add(self._on_elemt_content_changed)
            self.on_elements_changed(self, True, elemt)
            elemt.on_exit_focus.add(self._on_elemt_exit_focus)

    def remove(self, elemt: control):
        if elemt in self._elements:
            self._elements.remove(elemt)
            elemt.in_container = False
            elemt.on_content_changed.remove(self._on_elemt_content_changed)
            self.on_elements_changed(self, False, elemt)
            elemt.on_exit_focus.remove(self._on_elemt_exit_focus)

    def _on_elemt_content_changed(self, elemt):
        self.on_content_changed(self)

    @property
    def on_elements_changed(self) -> event:
        """
        Para 1:panel object
        
        Para 2:True->Add,False->Remove
        
        Para 3:operated control

        :return: event(panel,bool,control)
        """
        return self._on_elements_changed

    @property
    def on_focused_changed(self) -> event:
        """
        Para 1:panel object

        Para 2:former focused
        
        Para 3:current focused

        :return: event(panel,control,control)
        """
        return self._on_focused_changed

    @abstractmethod
    def draw_on(self, buf: buffer):
        """
        Draw all content on the buffer
        :param buf:screen buffer
        """
        pass

    @property
    def elements(self) -> Set[CTRL]:
        return self._elements

    @property
    def elemt_count(self) -> int:
        return len(self._elements)

    @property
    def focusable(self) -> bool:
        return True

    @property
    def cur_focused(self) -> control:
        return self._cur_focused

    @cur_focused.setter
    def cur_focused(self, value: control):
        if value is None or value in self.elements:
            former: control = self._cur_focused
            if former != value:
                if former and former.focusable:
                    former.on_lost_focus()
                self._cur_focused = value
                if value and value.focusable:
                    value.on_focused()
                self.on_focused_changed(self, former, value)

    @property
    def elemts_total_width(self):
        return sum(elemt.width for elemt in self.elements)

    @property
    def elemts_total_height(self):
        return sum(elemt.height for elemt in self.elements)

    def go_next_focusable(self):
        pass

    def go_pre_focusable(self):
        pass

    def on_input(self, char: chars.char) -> bool:
        if self.cur_focused:
            return self.cur_focused.on_input(char)
        elif chars.c_esc == char:
            self.on_exit_focus(self)
            return True
        return False


Orientation = str
horizontal = "horizontal"
vertical = "vertical"

OverRange = str
discard = "discard"
expend = "expend"


class stack(panel):
    def cache_layout(self):
        self._layout_changed = False
        if self.orientation == vertical:
            if self.elemt_interval == auto:
                if self.height == auto:
                    self._r_elemt_interval = 0
                else:
                    self._r_elemt_interval = self.height // self.elemts_total_height
            else:
                self._r_elemt_interval = self.elemt_interval
        else:  # horizontal
            if self.elemt_interval == auto:
                if self.width == auto:
                    self._r_elemt_interval = 1
                else:
                    self._r_elemt_interval = self.width // self.elemts_total_width
            else:
                self._r_elemt_interval = self.elemt_interval
        h = 0
        w = 0
        for i, elemt in enumerate(self._elements_stack):
            h += elemt.render_height
            w += elemt.render_width
            if i > 0:
                if self.orientation == horizontal:
                    h += self._r_elemt_interval
                else:
                    w += self._r_elemt_interval
            if self.height != auto and h >= self.height and self.over_range == discard:
                break
        self._r_width = w
        self._r_height = h

    def draw_on(self, buf: buffer):
        if self._layout_changed:
            self.cache_layout()

        if self.orientation == vertical:
            h = 0
            for i, elemt in enumerate(self._elements_stack):
                h += elemt.render_height
                if i > 0:
                    h += self._r_elemt_interval
                if self.height != auto and h >= self.height and self.over_range == discard:
                    break
                elemt: control
                elemt.draw_on(buf)
                interval = utils.repeat("\n", self._r_elemt_interval)
                buf.addtext(text=interval)
        else:
            w = 0
            for i, elemt in enumerate(self._elements_stack):
                w += elemt.render_width
                if i > 0:
                    w += self._r_elemt_interval
                if self.width != auto and w >= self.width and self.over_range == discard:
                    break
                elemt: control
                elemt.draw_on(buf)
                interval = utils.repeat(" ", self._r_elemt_interval)
                buf.addtext(text=interval, end="")
        buf.addtext()

    def __init__(self):
        super().__init__()
        self._elements_stack: List[control] = []
        self._elemt_interval = auto
        self._r_elemt_interval = 0
        self._orientation = vertical
        self._over_range = discard
        self._cur_focused_index = None
        self._r_width = 0
        self._r_height = 0
        self._is_selected: bool = True

    @property
    def cur_focused_index(self) -> Optional[int]:
        return self._cur_focused_index

    @cur_focused_index.setter
    def cur_focused_index(self, value: Optional[int]):
        if value is None:
            if self._cur_focused_index != value:
                self._cur_focused_index = value
                self.cur_focused = None
        else:
            value = max(value, 0)
            value = min(value, len(self.elements) - 1)
            if self._cur_focused_index != value:
                self._cur_focused_index = value
                self.cur_focused = self._elements_stack[value]

    @property
    def elemt_interval(self) -> PROP:
        return self._elemt_interval

    @elemt_interval.setter
    def elemt_interval(self, value: PROP):
        self._elemt_interval = value
        self.on_prop_changed(self, "elemt_interval")

    @property
    def orientation(self) -> Orientation:
        return self._orientation

    @orientation.setter
    def orientation(self, value: Orientation):
        if self._orientation != value:
            self._orientation = value
            self.on_prop_changed(self, "orientation")

    @property
    def over_range(self) -> OverRange:
        return self._over_range

    @over_range.setter
    def over_range(self, value: OverRange):
        if self._over_range != value:
            self._over_range = value
            self.on_prop_changed(self, "over_range")

    def go_next_focusable(self):
        if self.cur_focused_index is None:
            i = -1
        else:
            i = self.cur_focused_index
        for ci in range(i + 1, self.elemt_count):
            c = self._elements_stack[ci]
            if c.focusable:
                self.cur_focused_index = ci
                break

    def go_pre_focusable(self):
        if self.cur_focused_index is None:
            return
        else:
            i = self.cur_focused_index
        for ci in range(i - 1, 0, -1):
            c = self._elements_stack[ci]
            if c.focusable:
                self.cur_focused_index = ci
                break

    def add(self, elemt: control):
        self._elements_stack.append(elemt)
        super().add(elemt)

    def remove(self, elemt: control):
        try:
            self._elements_stack.remove(elemt)
        except:
            pass
        super().remove(elemt)

    def on_input(self, char: chars.char) -> bool:
        if self.cur_focused and self._is_selected:
            return self.cur_focused.on_input(char)
        elif keys.k_enter == char:
            self._is_selected = True
            return True
        elif keys.k_up == char:
            self.go_pre_focusable()
            return True
        elif keys.k_down == char:
            self.go_next_focusable()
            return True
        elif chars.c_esc == char:
            self.on_exit_focus(self)
            return True
        return False

    def _on_elemt_exit_focus(self, elemt) -> bool:
        if super()._on_elemt_exit_focus(elemt):
            if self.cur_focused is None:
                self.on_exit_focus(self)
                self._is_selected = False
            # self.cur_focused_index = None
            return True
        return False

    @property
    def render_height(self) -> int:
        return self._r_height

    @property
    def render_width(self) -> int:
        return self._r_width


class _grid_layout_unit:
    def __init__(self, width=auto, height=auto):
        self.width = width
        self.height = height


_GLU = _grid_layout_unit


class grid(panel):

    def __init__(self, row: int, column: int):
        super().__init__()
        self._grid: List[List[control]] = utils.fill_2d_array(row, column, None)
        self._layout: List[List[_GLU]] = utils.gen_2d_array(row, column, _GLU)
        self._elemt_interval_w = auto
        self._elemt_interval_h = auto

    def draw_on(self, buf: buffer):
        if self._layout_changed:
            self.cache_layout()

    def cache_layout(self):
        self._layout_changed = False
        if self.width == auto:
            pass

    @property
    def elemt_interval_w(self) -> PROP:
        return self._elemt_interval_w

    @elemt_interval_w.setter
    def elemt_interval_w(self, value: PROP):
        if value != auto and value < 0:
            value = 0
        if self._elemt_interval_w != value:
            self._elemt_interval_w = value
            self.on_prop_changed(self, "elemt_interval_w")

    @property
    def elemt_interval_h(self) -> PROP:
        return self._elemt_interval_h

    @elemt_interval_h.setter
    def elemt_interval_h(self, value: PROP):
        if value != auto and value < 0:
            value = 0
        if self._elemt_interval_h != value:
            self._elemt_interval_h = value
            self.on_prop_changed(self, "elemt_interval_h")

    def __getitem__(self, item: Tuple[int, int]) -> Optional[CTRL]:
        return self._grid[item[0]][item[1]]

    def __setitem__(self, key: Tuple[int, int], value: control):
        self._grid[key[0]][key[1]] = value

    def set(self, i: int, j: int, ctrl: control):
        former: control = self[i, j]
        if former:
            self.remove(former)
        self[i, j] = ctrl
        self.add(ctrl)
