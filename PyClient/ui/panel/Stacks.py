import utils
from ui.Controls import Control
from ui.Elements import *
from ui.Renders import Canvas
from ui.Renders import Viewer
from ui.outputs import buffer
from ui.panels import Panel

expend = "expend"
Orientation = str
OverRange = str
discard = "discard"


class FitMode(Enum):
    Fit = 1
    Stretch = 2


class OrientationType(Enum):
    Horizontal = 1
    Vertical = 2


class AlignmentType(Enum):
    Left = 1
    Right = 2
    Top = 3
    Bottom = 4
    Center = 5


horizontal = OrientationType.Horizontal
vertical = OrientationType.Vertical
center = AlignmentType.Center
align_left = AlignmentType.Left
align_right = AlignmentType.Right


class Stack(Panel):
    OrientationProp: DpProp
    FitModeProp: DpProp
    GetHorizontalAlignment: Callable[[DpObj], AlignmentType]
    SetHorizontalAlignment: Callable[[DpObj, AlignmentType], NoReturn]
    GetVerticalAlignment: Callable[[DpObj], AlignmentType]
    SetVerticalAlignment: Callable[[DpObj, AlignmentType], NoReturn]

    def __init__(self):
        super().__init__()
        self._elements_stack: List[Control] = []
        # ------------Legacy------------
        self._elemt_interval = Auto
        self._r_elemt_interval = 0
        self._over_range = discard
        self._cur_focused_index = None
        self._horizontal_alignment = center
        # ------------Legacy------------

    def PaintOn(self, canvas: Canvas):
        elements = self._elements_stack
        dx = 0
        dy = 0
        width = self.RenderWidth
        height = self.RenderHeight
        if self.Orientation == OrientationType.Horizontal:
            for e in elements:
                if not e.IsVisible:
                    continue
                rew = e.RenderWidth
                reh = e.RenderHeight
                alignment = Stack.GetHorizontalAlignment(e)
                if alignment == AlignmentType.Top:
                    edy = 0
                elif alignment == AlignmentType.Bottom:
                    edy = height - reh
                else:  # Default is "Center"
                    edy = (height - reh) // 2
                e.PaintOn(Viewer(dx, edy, rew, reh, canvas))
                dx += rew
        else:
            for e in elements:
                if not e.IsVisible:
                    continue
                rew = e.RenderWidth
                reh = e.RenderHeight
                alignment = Stack.GetVerticalAlignment(e)
                if alignment == AlignmentType.Left:
                    edx = 0
                elif alignment == AlignmentType.Right:
                    edx = width - rew
                else:  # Default is "Center"
                    edx = (width - rew) // 2

                e.PaintOn(Viewer(edx, dy, rew, reh, canvas))
                dy += reh

    def Measure(self):
        if not self.IsVisible:
            self.DWidth = 0
            self.DHeight = 0
            return
        elements = self._elements_stack
        if self.Orientation == OrientationType.Horizontal:
            self.DWidth = sum(elem.DWidth for elem in elements if elem.IsVisible)
            self.DHeight = max(elem.DHeight for elem in elements if elem.IsVisible)
        else:
            self.DWidth = max(elem.DWidth for elem in elements if elem.IsVisible)
            self.DHeight = sum(elem.DHeight for elem in elements if elem.IsVisible)

    def Arrange(self, width: int, height: int) -> Tuple[int, int]:
        if not self.IsVisible:
            self.RenderWidth = 0
            self.RenderHeight = 0
            return 0, 0
        restw = width
        resth = height
        elements = self._elements_stack
        elen = len(elements)
        formerElemtCount = 0
        if self.Orientation == OrientationType.Horizontal:
            maxHeight = 0
            for e in elements:
                if not e.IsVisible:
                    continue
                dew = restw // (elen - formerElemtCount)
                rew, reh = e.Arrange(dew, resth)
                restw -= rew
                if reh > maxHeight:
                    maxHeight = reh
                formerElemtCount += 1
            self.RenderWidth = width - restw
            if self.Height == Auto:
                self.RenderHeight = maxHeight
            else:
                self.RenderHeight = height
        else:
            maxWidth = 0
            for e in elements:
                if not e.IsVisible:
                    continue
                deh = resth // (elen - formerElemtCount)
                rew, reh = e.Arrange(restw, deh)
                resth -= reh
                if rew > maxWidth:
                    maxWidth = rew
                formerElemtCount += 1
            if self.Width == Auto:
                self.RenderWidth = maxWidth
            else:
                self.RenderWidth = width
            self.RenderHeight = height - resth
        return self.RenderWidth, self.RenderHeight

    @property
    def Orientation(self):
        return self.GetValue(self.OrientationProp)

    @Orientation.setter
    def Orientation(self, value):
        self.SetValue(self.OrientationProp, value)

    # ------------Legacy------------
    def cache_layout(self):
        for c in self.elements:
            c.cache_layout()

        if not self.IsLayoutChanged:
            return
        self.IsLayoutChanged = False
        if self.Orientation == OrientationType.Vertical:
            if self.elemt_interval == Auto:
                if self.height == Auto:
                    self._r_elemt_interval = 0
                else:
                    self._r_elemt_interval = self.height // self.elemts_total_height
            else:
                self._r_elemt_interval = self.elemt_interval
        else:  # Horizontal
            if self.elemt_interval == Auto:
                if self.width == Auto:
                    self._r_elemt_interval = 1
                else:
                    self._r_elemt_interval = self.width // self.elemts_total_width
            else:
                self._r_elemt_interval = self.elemt_interval
        h = 0
        w = 0
        for i, elemt in enumerate(self._elements_stack):
            if self.width != Auto and w >= self.width and self.over_range == discard:
                continue
            if self.height != Auto and h >= self.height and self.over_range == discard:
                continue
            h += elemt.RenderHeight
            w = max(elemt.RenderWidth, w)
            if 0 < i < self.elemt_count - 1:
                if self.Orientation == OrientationType.Horizontal:
                    h += self._r_elemt_interval
                else:
                    w += self._r_elemt_interval

        self.RenderWidth = w
        self.RenderHeight = h

        if self.Orientation == OrientationType.Vertical:
            for item in self._elements_stack:
                if item.gprop(Panel.No_Left_Margin) is not True:
                    item.left_margin = self.left_margin
        else:
            for i, e in enumerate(self._elements_stack):
                if i == 0 and e.gprop(Panel.No_Left_Margin) is not True:
                    e.left_margin = self.left_margin
                else:
                    e.left_margin = 0

    def _get_final_horizontal_alignment(self, elemt: Control) -> AlignmentType:
        return Stack.GetHorizontalAlignment(elemt)

    def paint_on(self, buf: buffer):
        for c in self.elements:
            c.cache_layout()

        if self.IsLayoutChanged:
            self.cache_layout()

        if self.Orientation == OrientationType.Vertical:
            h = 0
            if self.top_margin > 0:
                buf.addtext(utils.repeat("\n", self.top_margin), end="")
            for i, elemt in enumerate(self._elements_stack):
                h += elemt.RenderHeight
                if i > 0:
                    h += self._r_elemt_interval
                if self.height != Auto and h >= self.height and self.over_range == discard:
                    break
                elemt: Control
                if elemt.RenderHeight == 1:
                    halign = self._get_final_horizontal_alignment(elemt)
                    if halign == AlignmentType.Left:
                        cur_left_margin = 0
                    elif halign == AlignmentType.Center:
                        cur_left_margin = (self.RenderWidth - elemt.RenderWidth) // 2
                    else:  # align right
                        cur_left_margin = self.RenderWidth - elemt.RenderWidth
                    buf.addtext(utils.repeat(' ', cur_left_margin), end='')
                elemt.paint_on(buf)
                buf.addtext(utils.repeat("\n", self._r_elemt_interval))
        else:
            w = 0
            if self.top_margin > 0:
                buf.addtext(utils.repeat("\n", self.top_margin), end="")
            for i, elemt in enumerate(self._elements_stack):
                w += elemt.RenderWidth
                if i > 0:
                    w += self._r_elemt_interval
                if self.width != Auto and w >= self.width and self.over_range == discard:
                    break
                if self.left_margin > 0:
                    buf.addtext(utils.repeat(" ", self.left_margin), end="")
                elemt: Control
                elemt.paint_on(buf)
                interval = utils.repeat(" ", self._r_elemt_interval)
                buf.addtext(text=interval, end="")
        if not self.in_container:
            buf.addtext()

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

    def Insert(self, index, control: Control):
        self._elements_stack.insert(index, control)
        return super().add(control)

    def AddControl(self, control: Control):
        self._elements_stack.append(control)
        return super().AddControl(control)

    def RemoveControl(self, control: Control) -> bool:
        try:
            self._elements_stack.remove(control)
        except:
            pass
        return super().RemoveControl(control)

    def _on_elemt_exit_focus(self, elemt) -> bool:
        if super()._on_elemt_exit_focus(elemt):
            if self.cur_focused is None:
                self.on_exit_focus(self)
                self._is_selected = False
            return True
        return False

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
    # ------------Legacy------------


Stack.OrientationProp = DpProp.Register(
    "Orientation", OrientationType, Stack,
    DpPropMeta(OrientationType.Vertical, propChangedCallback=OnRenderPropChangedCallback))
Stack.FitModeProp = DpProp.Register(
    "FitMode", FitMode, Stack,
    DpPropMeta(FitMode.Fit, propChangedCallback=OnRenderPropChangedCallback))
Stack.HorizontalAlignmentProp = DpProp.RegisterAttach(
    "HorizontalAlignment", AlignmentType, Stack,
    DpPropMeta(AlignmentType.Center, propChangedCallback=OnRenderPropChangedCallback)
)
Stack.VerticalAlignmentProp = DpProp.RegisterAttach(
    "VerticalAlignment", AlignmentType, Stack,
    DpPropMeta(AlignmentType.Center, propChangedCallback=OnRenderPropChangedCallback)
)
