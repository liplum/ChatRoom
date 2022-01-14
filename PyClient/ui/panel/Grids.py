import re
from typing import Tuple, List, Optional, Iterator

import utils
from ui.Controls import PROP, Control, auto
from ui.Renders import Canvas
from ui.outputs import buffer
from ui.panels import Panel, CTRL

"""
1.
Row:[10,*]<-FullWidth:100
[Row 1]=10 ; [Row 2]=90
2.
Row:[35,*,2*,*]<-FullWidth:100
[Row 1]=35 ; [Row 2]=16 ; [Row 3]=32 ; [Row 4]=17
3.
Row:[35,*,2*,10,*]<-FullWidth:100
[Row 1]=35 ; [Row 3]=14 ; [Row 4]=26 ; [Row 5]=10 ; [Row 6]=15
Prototype:
First:Rest = Full - sum(abs for each value)
Second:EveryParts = Rest // sum(proportion for each *)
"""
_MatchRowAndColumnProportion = re.compile("^[0-9]*(?=\*)")


class Row:
    @classmethod
    def ByProportion(cls, heightProportion: int) -> "Row":
        return Row(0, heightProportion, False)

    @classmethod
    def ByAbs(cls, heightAbs: int) -> "Row":
        return Row(heightAbs)

    @classmethod
    def ByStr(cls, arg: str) -> "Row":
        proportion = re.match(_MatchRowAndColumnProportion, arg)
        if proportion is not None:
            p = proportion.group()
            if len(p) == 0:
                return Row.ByProportion(1)
            else:
                try:
                    p = int(p)
                except:
                    p = 1
                return Row.ByProportion(p)
        else:
            try:
                p = int(arg)
            except:
                p = 1
            return Row.ByProportion(p)

    def __init__(self, heightAbs: int, heightProportion: int = 0, isAbs: bool = True):
        self.IsAbs = isAbs
        self.HeightAbs: int = heightAbs
        self.HeightProportion: int = heightProportion


class Column:
    @classmethod
    def ByProportion(cls, widthProportion: int) -> "Column":
        return Column(0, widthProportion, False)

    @classmethod
    def ByAbs(cls, widthAbs: int) -> "Column":
        return Column(widthAbs)

    @classmethod
    def ByStr(cls, arg: str) -> "Column":
        proportion = re.match(_MatchRowAndColumnProportion, arg)
        if proportion is not None:
            p = proportion.group()
            if len(p) == 0:
                return Column.ByProportion(1)
            else:
                try:
                    p = int(p)
                except:
                    p = 1
                return Column.ByProportion(p)
        else:
            try:
                p = int(arg)
            except:
                p = 1
            return Column.ByProportion(p)

    def __init__(self, widthAbs: int, widthProportion: int = 0, isAbs: bool = True):
        self.IsAbs = isAbs
        self.WidthAbs: int = widthAbs
        self.WidthProportion: int = widthProportion


class _unit:
    def __init__(self, row: Row, column: Column):
        self.row = row
        self.column = column

    @property
    def width(self) -> PROP:
        return self.column.width

    @property
    def height(self) -> int:
        return self.row.HeightAbs


FIndex = Tuple[int, int]
GridMatrix = List[List[Optional[Control]]]
Units = List[List[_unit]]


class Grid(Panel):
    """
    Example 1:

    3*2:
    interval tw = 2
    interval Height = 1
    Column[0] tw = 4
    Column[1] tw = 13

    Date__  1/1_______________

    Name__  Liplum____________

    Email_  Liplum@outlook.com
    Example 2:

    6*3:
    interval tw = 1
    interval Height = 0
    Column[0] tw = 4
    Column[1] tw = 13
    Column[2] tw = 13

    Day_ Event________ With whom____
    1___ Nothing______ Only me______
    2___ Stay home____ My parents___
    3___ Programming__ Only me______
    4___ Sports_______ Friends______
    5___ Study________ Classmates___
    """

    def __init__(self, rows: [Row], columns: [Column]):
        super().__init__()
        self.rowlen = len(rows)
        self.columnlen = len(columns)
        self.rows = rows
        self.columns = columns

        if self.rowlen == 0:
            self.rows = [Row.ByProportion(1)]
        if self.columnlen == 0:
            self.columns = [Column.ByProportion(1)]

        self._elemt_interval_w = auto
        self._elemt_interval_h = auto
        self.gen_unit()
        self._grid: GridMatrix = utils.fill_2d_array(self.rowlen, self.columnlen, None)
        self._r_width = 0
        self._r_height = 0
        self._r_elemt_interval_w = 0
        self._r_elemt_interval_h = 0
        self._cur_focused_index: Optional[FIndex] = (0, 0)

    def Arrange(self, width: int, height: int) -> Tuple[int, int]:
        return super().Arrange(width, height)

    def Measure(self):
        super().Measure()

    def PaintOn(self, canvas: Canvas):
        super().PaintOn(canvas)

    def gen_unit(self):
        self._units: Units = utils.gen_2d_arrayX(
            self.rowlen, self.columnlen, lambda i, j: _unit(self.rows[i], self.columns[j]))

    def paint_on(self, buf: buffer):
        for c in self.elements:
            c.cache_layout()

        if self.IsLayoutChanged:
            self.cache_layout()
        if self.top_margin > 0:
            buf.addtext(utils.repeat("\n", self.top_margin), end="")
        for i in range(self.rowlen):
            if self.left_margin > 0:
                buf.addtext(utils.repeat(" ", self.left_margin), end="")
            for j in range(self.columnlen):
                c = self._grid[i][j]
                if c:
                    c.paint_on(buf)
                    w = c.render_width
                    rest = self.columns[j].width - w
                    if rest > 0:
                        buf.addtext(utils.repeat(" ", rest), end="")
                else:
                    buf.addtext(utils.repeat(" ", self.columns[j].width), end="")
                buf.addtext(utils.repeat(" ", self._r_elemt_interval_w), end="")
            buf.addtext(utils.repeat("\n", self._r_elemt_interval_h))
        if not self.in_container:
            buf.addtext()

    def cache_layout(self):
        for c in self.elements:
            c.cache_layout()

        if not self.IsLayoutChanged:
            return
        self.IsLayoutChanged = False

        w = 0
        h = 0
        if self.width == auto:
            if self.elemt_interval_w == auto:
                self._r_elemt_interval_w = 1
            else:
                self._r_elemt_interval_w = self.elemt_interval_w

            for j, column in enumerate(self.columns):
                try:
                    max_width = max(c.render_width for c in self.column_items(j) if c)
                except Exception as e:
                    max_width = column.width
                column.width = max_width
                w += max_width
        else:
            occupied_width = 0
            for j, column in enumerate(self.columns):
                try:
                    max_width = max(c.render_width for c in self.column_items(j) if c)
                except:
                    max_width = column.width
                column.width = max_width
                w += max_width
                occupied_width += max_width

            if self.elemt_interval_w == auto:
                if columnlen == 1:
                    self._r_elemt_interval_w = 0
                else:
                    self._r_elemt_interval_w = (self.width - occupied_width) // (self.columnlen - 1)
            else:
                self._r_elemt_interval_w = self.elemt_interval_w

        w += self._r_elemt_interval_w * (self.columnlen - 1)

        if self.height == auto:
            if self.elemt_interval_h == auto:
                self._r_elemt_interval_h = 0
            else:
                self._r_elemt_interval_h = self.elemt_interval_h
        else:
            if self.elemt_interval_h == auto:
                if self.rowlen == 1:
                    self._r_elemt_interval_w = 0
                else:
                    self._r_elemt_interval_h = (self.height - self.rowlen) // (self.columnlen - 1)
            else:
                self._r_elemt_interval_h = self.elemt_interval_h

        h += self.rowlen + self._r_elemt_interval_h * (self.rowlen - 1)
        self._r_width = w + self.left_margin
        self._r_height = h + self.top_margin

        for i in range(self.rowlen):
            for j in range(self.columnlen):
                c = self._grid[i][j]
                if c:
                    c.width = self._units[i][j].width

        for e in self.column_items(0):
            if e and e.gprop(Panel.No_Left_Margin) is not True:
                e.left_margin = self.left_margin

    def switch_to(self, elemt: Control):
        if elemt.focusable:
            index = self.find(elemt)
            if index:
                self.cur_focused_index = index

    def row_items(self, row: int):
        for j in range(self.columnlen):
            yield self._grid[row][j]

    def column_items(self, column: int):
        for i in range(self.rowlen):
            yield self._grid[i][column]

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
        i, j = item
        return self._grid[i][j]

    def __setitem__(self, key: Tuple[int, int], value: Control):
        i, j = key
        self.set(i, j, value)

    def set(self, i: int, j: int, ctrl: Control) -> bool:
        former: Control = self._grid[i][j]
        if former:
            self.RemoveControl(former, (i, j))
        self._grid[i][j] = ctrl
        return super().AddControl(ctrl)

    @property
    def render_height(self) -> int:
        return self._r_height

    @property
    def render_width(self) -> int:
        return self._r_width

    def go_next_focusable(self) -> bool:
        index = self.cur_focused_index
        if index:
            i, j = index
            if i == self.rowlen - 1 and j == self.columnlen - 1:
                return False
        else:
            i, j = 0, -1
        for item, index in self.all_next((i, j)):
            if item and item.focusable:
                self.cur_focused_index = index
                return True
        return False

    def go_pre_focusable(self) -> bool:
        index = self.cur_focused_index
        if index:
            i, j = index
            if i == 0 and j == 0:
                return False
        else:
            return False
        for item, index in self.all_pre((i, j)):
            if item and item.focusable:
                self.cur_focused_index = index
                return True
        return False

    def switch_to_first_or_default_item(self):
        self.cur_focused_index = None
        self.go_next_focusable()

    def find(self, elemt: Optional[Control]) -> Optional[FIndex]:
        for i in range(self.rowlen):
            for j in range(self.columnlen):
                if self._grid[i][j] == elemt:
                    return i, j
        return None

    def all_next(self, start: FIndex) -> Iterator[Tuple[Optional[Control], FIndex]]:
        i, j = start
        i_end = self.rowlen - 1
        j_end = self.columnlen - 1
        while i != i_end or j != j_end:
            if j == j_end:
                i += 1
                j = 0
            else:
                j += 1
            yield self._grid[i][j], (i, j)

    def all_pre(self, start: FIndex) -> Iterator[Tuple[Optional[Control], FIndex]]:
        i, j = start
        j_end = self.columnlen - 1
        while i != 0 or j != 0:
            if j == 0:
                i -= 1
                j = j_end
            else:
                j -= 1
            yield self._grid[i][j], (i, j)

    def RemoveControl(self, control: Control, index: Optional[FIndex] = None) -> bool:
        if super().RemoveControl(control):
            if index is None:
                index = self.find(control)
            if index:
                i, j = index
                if j == 0:
                    control.left_margin = 0
                self._grid[i][j] = None
                return True
        return False

    def AddControl(self, control: Control, index: Optional[FIndex] = None) -> bool:
        if index is None:
            index = self.find(None)
        if index:
            i, j = index
            former = self._grid[i][j]
            if former is None:
                self._grid[i][j] = control
                return super().AddControl(control)
        return False

    @property
    def cur_focused_index(self) -> FIndex:
        return self._cur_focused_index

    @cur_focused_index.setter
    def cur_focused_index(self, value: FIndex):
        if value:
            i, j = value
            if 0 <= i < self.rowlen and 0 <= j < self.columnlen:
                c = self._grid[i][j]
                self._cur_focused_index = value
                self.cur_focused = c
        else:
            self._cur_focused_index = value
            self.cur_focused = None

    def on_focused(self):
        super().on_focused()
        self.switch_to_first_or_default_item()

    def on_lost_focus(self):
        super().on_lost_focus()
        self.cur_focused = None


def gen_grid(row_count: int, columns: [Column]):
    return Grid(rows=[Row.ByAbs(1) for i in range(row_count)], columns=columns)
