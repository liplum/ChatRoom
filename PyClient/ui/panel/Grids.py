import re
from enum import Enum
from typing import Tuple, List, Optional, Iterator

import utils
from ui.Controls import PROP, Control, Auto
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


class DefinitionType(Enum):
    Auto = 1
    Char = 2
    Star = 3


class DefinitionBase:

    def __init__(self, value: Optional[int] = None,
                 defType: DefinitionType = DefinitionType.Auto):
        self.Value = value
        self.DefType = defType

    @classmethod
    def ByStar(cls, star: int) -> "DefinitionBase":
        return cls(star, DefinitionType.Star)

    @classmethod
    def ByChar(cls, char: int) -> "DefinitionBase":
        return cls(char, DefinitionType.Char)

    @classmethod
    def ByStr(cls, arg: str) -> "DefinitionBase":
        stars = re.match(_MatchRowAndColumnProportion, arg)
        if stars is not None:
            p = stars.group()
            if len(p) == 0:
                return cls.ByStar(1)
            else:
                try:
                    p = int(p)
                except:
                    p = 1
                return cls.ByStar(p)
        else:
            try:
                p = int(arg)
            except:
                p = 1
            return cls.ByStar(p)


class Row(DefinitionBase):
    pass


class Column(DefinitionBase):
    pass


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


class DefinitionCollection:
    def __init__(self):
        pass


class RowCollection(DefinitionCollection):
    def GetHeightByIndex(self, fullHeight, index) -> int:
        pass


class ColumnCollection(DefinitionCollection):
    def GetWidthByIndex(self, fullWidth, index) -> int:
        pass


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


class Grid(Panel):

    def __init__(self):
        super().__init__()
        self._rows = None
        self._columns = None
        self.Built = False

        # ------------Legacy------------
        self._elemt_interval_w = Auto
        self._elemt_interval_h = Auto

        self._r_elemt_interval_w = 0
        self._r_elemt_interval_h = 0
        self._cur_focused_index: Optional[FIndex] = (0, 0)
        # ------------Legacy------------

    @property
    def RowDefinitions(self) -> [Row]:
        return self._rows

    @RowDefinitions.setter
    def RowDefinitions(self, value: [Row]):
        self._rows = value
        self.rowlen = len(value)

    @property
    def ColumnDefinitions(self) -> [Column]:
        return self._columns

    @ColumnDefinitions.setter
    def ColumnDefinitions(self, value: [Column]):
        self._columns = value
        self.columnlen = len(value)

    def Build(self):
        if self.RowDefinitions is None:
            raise GridHasNoDefinitionError(f"Row definition is None.", self)
        if self.ColumnDefinitions is None:
            raise GridHasNoDefinitionError(f"Column definition is None.", self)
        self.gen_unit()
        self._grid: GridMatrix = utils.fill_2d_array(self.rowlen, self.columnlen, None)
        self.Built = True

    def TryBuild(self):
        if not self.Built:
            self.Build()

    def GetWidthHeightByRC(self, row: Row, column: Column) -> Tuple[int, int]:
        pass

    def GetWidthHeightByRCIndex(self, rowI: int, columnI: int) -> Tuple[int, int]:
        pass

    def Arrange(self, width: int, height: int) -> Tuple[int, int]:
        if not self.IsVisible:
            self.RenderWidth = 0
            self.RenderHeight = 0
            return 0, 0

    def Measure(self):
        if not self.IsVisible:
            self.DWidth = 0
            self.DHeight = 0
            return
        dw = self.Width
        dh = self.Height
        if dw == Auto:
            for j in range(self.rowlen):
                for i in range(self.columnlen):
                    pass
        else:
            self.DWidth = dw

    def PaintOn(self, canvas: Canvas):
        pass

    def __getitem__(self, item: Tuple[int, int]) -> Optional[CTRL]:
        i, j = item
        return self._grid[i][j]

    def __setitem__(self, key: Tuple[int, int], value: Control):
        i, j = key
        self.set(i, j, value)

    def set(self, i: int, j: int, ctrl: Control) -> bool:
        self.TryBuild()
        former: Control = self._grid[i][j]
        if former:
            self.RemoveControl(former, (i, j))
        self._grid[i][j] = ctrl
        return super().AddControl(ctrl)

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

    def OnFocused(self):
        super().OnFocused()
        self.switch_to_first_or_default_item()

    def OnLostFocused(self):
        super().OnLostFocused()
        self.cur_focused = None

    # ------------Legacy------------
    def gen_unit(self):
        self._units: Units = utils.gen_2d_arrayX(
            self.rowlen, self.columnlen, lambda i, j: _unit(self._rows[i], self._columns[j]))

    def paint_on(self, buf: buffer):
        self.TryBuild()

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
                    w = c.RenderWidth
                    rest = self._columns[j].width - w
                    if rest > 0:
                        buf.addtext(utils.repeat(" ", rest), end="")
                else:
                    buf.addtext(utils.repeat(" ", self._columns[j].width), end="")
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
        if self.width == Auto:
            if self.elemt_interval_w == Auto:
                self._r_elemt_interval_w = 1
            else:
                self._r_elemt_interval_w = self.elemt_interval_w

            for j, column in enumerate(self._columns):
                try:
                    max_width = max(c.RenderWidth for c in self.column_items(j) if c)
                except Exception as e:
                    max_width = column.width
                column.width = max_width
                w += max_width
        else:
            occupied_width = 0
            for j, column in enumerate(self._columns):
                try:
                    max_width = max(c.RenderWidth for c in self.column_items(j) if c)
                except:
                    max_width = column.width
                column.width = max_width
                w += max_width
                occupied_width += max_width

            if self.elemt_interval_w == Auto:
                if columnlen == 1:
                    self._r_elemt_interval_w = 0
                else:
                    self._r_elemt_interval_w = (self.width - occupied_width) // (self.columnlen - 1)
            else:
                self._r_elemt_interval_w = self.elemt_interval_w

        w += self._r_elemt_interval_w * (self.columnlen - 1)

        if self.height == Auto:
            if self.elemt_interval_h == Auto:
                self._r_elemt_interval_h = 0
            else:
                self._r_elemt_interval_h = self.elemt_interval_h
        else:
            if self.elemt_interval_h == Auto:
                if self.rowlen == 1:
                    self._r_elemt_interval_w = 0
                else:
                    self._r_elemt_interval_h = (self.height - self.rowlen) // (self.columnlen - 1)
            else:
                self._r_elemt_interval_h = self.elemt_interval_h

        h += self.rowlen + self._r_elemt_interval_h * (self.rowlen - 1)
        self.RenderWidth = w + self.left_margin
        self.RenderHeight = h + self.top_margin

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
        if value != Auto and value < 0:
            value = 0
        if self._elemt_interval_w != value:
            self._elemt_interval_w = value
            self.on_prop_changed(self, "elemt_interval_w")

    @property
    def elemt_interval_h(self) -> PROP:
        return self._elemt_interval_h

    @elemt_interval_h.setter
    def elemt_interval_h(self, value: PROP):
        if value != Auto and value < 0:
            value = 0
        if self._elemt_interval_h != value:
            self._elemt_interval_h = value
            self.on_prop_changed(self, "elemt_interval_h")

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

    # ------------Legacy------------


def gen_grid(row_count: int, columns: [Column]):
    g = Grid()
    g.RowDefinitions = [Row.ByChar(1) for _ in range(row_count)]
    g.ColumnDefinitions = columns
    return g


class GridHasNoDefinitionError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
