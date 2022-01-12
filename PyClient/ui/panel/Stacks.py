from typing import List, Optional, Tuple

import utils
from ui.Controls import auto, Control, PROP
from ui.Renders import Canvas
from ui.Renders import Viewer
from ui.outputs import buffer
from ui.panels import Panel

Alignment = str
Horizontal_Alignment = str
align_left = "align_left"
align_right = "align_right"
expend = "expend"
center = "center"
Orientation = str
horizontal = "Horizontal"
vertical = "Vertical"
OverRange = str
discard = "discard"


class Stack(Panel):
    Horizontal_Alignment: str = "Stack.horizontal_alignment"

    def PaintOn(self, canvas: Canvas):
        elements = self.elements
        dx = 0
        dy = 0
        if self.orientation == horizontal:
            for e in elements:
                if not e.IsVisible:
                    continue
                rew = e.RenderWidth
                reh = e.RenderHeight
                e.PaintOn(Viewer(dx, dy, rew, reh, canvas))
                dx += rew
        else:
            for e in elements:
                if not e.IsVisible:
                    continue
                rew = e.RenderWidth
                reh = e.RenderHeight
                e.PaintOn(Viewer(dx, dy, rew, reh, canvas))
                dy += reh

    def Measure(self):
        if not self.IsVisible:
            return
        if self.orientation == horizontal:
            self.DWidth = sum(elem.DWidth for elem in self.elements if elem.IsVisible)
            self.DHeight = max(elem.DHeight for elem in self.elements if elem.IsVisible)
        else:
            self.DWidth = max(elem.DWidth for elem in self.elements if elem.IsVisible)
            self.DHeight = sum(elem.DHeight for elem in self.elements if elem.IsVisible)

    def Arrange(self, width: int, height: int) -> Tuple[int, int]:
        if not self.IsVisible:
            return 0, 0
        rw = width
        rh = height
        elements = self.elements
        elen = len(elements)
        formerElemtCount = 0
        if self.orientation == horizontal:
            for e in elements:
                if not e.IsVisible:
                    continue
                dew = rw // (elen - formerElemtCount)
                rew, reh = e.Arrange(dew, rh)
                rw -= rew
                self.RenderWidth = width - rw
                self.RenderHeight = height
                formerElemtCount += 1
        else:
            for e in elements:
                if not e.IsVisible:
                    continue
                deh = rh // (elen - formerElemtCount)
                rew, reh = e.Arrange(rw, deh)
                rh -= reh
                formerElemtCount += 1
            self.RenderWidth = width
            self.RenderHeight = height - rh
        return self.RenderWidth, self.RenderHeight

    def cache_layout(self):
        for c in self.elements:
            c.cache_layout()

        if not self.IsLayoutChanged:
            return
        self.IsLayoutChanged = False
        if self.orientation == vertical:
            if self.elemt_interval == auto:
                if self.height == auto:
                    self._r_elemt_interval = 0
                else:
                    self._r_elemt_interval = self.height // self.elemts_total_height
            else:
                self._r_elemt_interval = self.elemt_interval
        else:  # Horizontal
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
            if self.width != auto and w >= self.width and self.over_range == discard:
                continue
            if self.height != auto and h >= self.height and self.over_range == discard:
                continue
            h += elemt.render_height
            w = max(elemt.render_width, w)
            if 0 < i < self.elemt_count - 1:
                if self.orientation == horizontal:
                    h += self._r_elemt_interval
                else:
                    w += self._r_elemt_interval

        self._r_width = w
        self._r_height = h

        if self.orientation == vertical:
            for item in self._elements_stack:
                if item.gprop(Panel.No_Left_Margin) is not True:
                    item.left_margin = self.left_margin
        else:
            for i, e in enumerate(self._elements_stack):
                if i == 0 and e.gprop(Panel.No_Left_Margin) is not True:
                    e.left_margin = self.left_margin
                else:
                    e.left_margin = 0

    def _get_final_horizontal_alignment(self, elemt: Control) -> Alignment:
        elemt_align = elemt.gprop(Stack.Horizontal_Alignment)
        if elemt_align is not None:
            return elemt_align
        else:
            return self.horizontal_alignment

    def paint_on(self, buf: buffer):
        for c in self.elements:
            c.cache_layout()

        if self.IsLayoutChanged:
            self.cache_layout()

        if self.orientation == vertical:
            h = 0
            if self.top_margin > 0:
                buf.addtext(utils.repeat("\n", self.top_margin), end="")
            for i, elemt in enumerate(self._elements_stack):
                h += elemt.render_height
                if i > 0:
                    h += self._r_elemt_interval
                if self.height != auto and h >= self.height and self.over_range == discard:
                    break
                elemt: Control
                if elemt.render_height == 1:
                    halign = self._get_final_horizontal_alignment(elemt)
                    if halign == align_left:
                        cur_left_margin = 0
                    elif halign == center:
                        cur_left_margin = (self.render_width - elemt.render_width) // 2
                    else:  # align right
                        cur_left_margin = self.render_width - elemt.render_width
                    buf.addtext(utils.repeat(' ', cur_left_margin), end='')
                elemt.paint_on(buf)
                buf.addtext(utils.repeat("\n", self._r_elemt_interval))
        else:
            w = 0
            if self.top_margin > 0:
                buf.addtext(utils.repeat("\n", self.top_margin), end="")
            for i, elemt in enumerate(self._elements_stack):
                w += elemt.render_width
                if i > 0:
                    w += self._r_elemt_interval
                if self.width != auto and w >= self.width and self.over_range == discard:
                    break
                if self.left_margin > 0:
                    buf.addtext(utils.repeat(" ", self.left_margin), end="")
                elemt: Control
                elemt.paint_on(buf)
                interval = utils.repeat(" ", self._r_elemt_interval)
                buf.addtext(text=interval, end="")
        if not self.in_container:
            buf.addtext()

    def __init__(self):
        super().__init__()
        self._elements_stack: List[Control] = []
        self._elemt_interval = auto
        self._r_elemt_interval = 0
        self._orientation = vertical
        self._over_range = discard
        self._cur_focused_index = None
        self._r_width = 0
        self._r_height = 0
        self._horizontal_alignment = center

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

    def switch_to(self, elemt: Control):
        if elemt.focusable:
            for i, e in enumerate(self.elements):
                if e == elemt:
                    self.cur_focused_index = i

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
                return True
        return False

    def go_pre_focusable(self):
        if self.cur_focused_index is None:
            return
        else:
            i = self.cur_focused_index
        for ci in range(i - 1, -1, -1):
            c = self._elements_stack[ci]
            if c.focusable:
                self.cur_focused_index = ci
                return True
        return False

    def insert(self, index, elemt: Control):
        self._elements_stack.insert(index, elemt)
        return super().add(elemt)

    def add(self, elemt: Control):
        self._elements_stack.append(elemt)
        return super().add(elemt)

    def remove(self, elemt: Control):
        try:
            self._elements_stack.remove(elemt)
        except:
            pass
        return super().remove(elemt)

    def _on_elemt_exit_focus(self, elemt) -> bool:
        if super()._on_elemt_exit_focus(elemt):
            if self.cur_focused is None:
                self.on_exit_focus(self)
                self._is_selected = False
            return True
        return False

    @property
    def render_height(self) -> int:
        return self._r_height

    @property
    def render_width(self) -> int:
        return self._r_width

    def on_focused(self):
        super().on_focused()
        self.switch_to_first_or_default_item()

    def on_lost_focus(self):
        super().on_lost_focus()
        self.cur_focused = None

    def switch_to_first_or_default_item(self):
        self.cur_focused_index = None
        self.go_next_focusable()

    @property
    def left_margin(self) -> int:
        return self._left_margin

    @left_margin.setter
    def left_margin(self, value: int):
        if value < 0:
            return
        if self._left_margin != value:
            self._left_margin = value
            self.on_prop_changed(self, "left_margin")

    @property
    def horizontal_alignment(self) -> Horizontal_Alignment:
        return self._horizontal_alignment

    @horizontal_alignment.setter
    def horizontal_alignment(self, value: Horizontal_Alignment):
        if self._horizontal_alignment != value:
            self._horizontal_alignment = value
            self.on_prop_changed(self, "horizontal_alignment")
