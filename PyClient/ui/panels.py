from typing import Set

import keys
from ui.Controls import *
from ui.panel.AbstractContainers import AbstractContainer

CTRL = TypeVar('CTRL', covariant=True, bound=Control)


class Panel(AbstractContainer):
    No_Left_Margin: str = "Panel.no_left_margin"

    def __init__(self):
        super().__init__()
        self._elements: Set[CTRL] = set()
        self._focused = False
        self._cur_focused: Optional[CTRL] = None
        self._on_elements_changed = Event(Panel, bool, Control)
        self._on_focused_changed = Event(Panel, (Control, type(None)), (Control, type(None)))
        self._top_margin = 0

        self._on_elements_changed.Add(lambda _, _1, _2: self.on_content_changed(self))
        self._on_focused_changed.Add(lambda _, _1, _2: self.on_content_changed(self))

    def _on_elemt_exit_focus(self, elemt) -> bool:
        """

        :param elemt:
        :return: whether current focused Control exited
        """
        if elemt == self.cur_focused:
            self.cur_focused = None
            return True
        return False

    def AddControl(self, control: Control):
        if control and control not in self._elements:
            self.AddChild(control)
            self._elements.add(control)
            control.in_container = True
            control.on_content_changed.Add(self._on_elemt_content_changed)
            self.on_elements_changed(self, True, control)
            control.on_exit_focus.Add(self._on_elemt_exit_focus)
            return True
        return False

    def RemoveControl(self, control: Control) -> bool:
        if control and control in self._elements:
            self.RemoveChild(control)
            self._elements.remove(control)
            control.in_container = False
            control.on_content_changed.Remove(self._on_elemt_content_changed)
            self.on_elements_changed(self, False, control)
            control.on_exit_focus.Remove(self._on_elemt_exit_focus)
            return True
        return False

    def add(self, elemt: Control) -> bool:
        return self.AddControl(elemt)

    def remove(self, elemt: Control) -> bool:
        return self.RemoveChild(elemt)

    def clear(self):
        for elemt in list(self._elements):
            self.remove(elemt)

    def _on_elemt_content_changed(self, elemt):
        self.on_content_changed(self)

    @property
    def on_elements_changed(self) -> Event:
        """
        Para 1:Panel object

        Para 2:True->Add,False->Remove

        Para 3:operated Control

        :return: Event(Panel,bool,Control)
        """
        return self._on_elements_changed

    @property
    def on_focused_changed(self) -> Event:
        """
        Para 1:Panel object

        Para 2:former focused

        Para 3:current focused

        :return: Event(Panel,Optional[Control],Control)
        """
        return self._on_focused_changed

    @abstractmethod
    def paint_on(self, buf: buffer):
        """
        Draw all content on the buffer
        :param buf:screen buffer
        """
        pass

    @property
    def top_margin(self) -> int:
        return self._top_margin

    @top_margin.setter
    def top_margin(self, value: int):
        if value < 0:
            return
        if self._top_margin != value:
            self._top_margin = value
            self.on_prop_changed(self, "top_margin")

    @property
    def elements(self) -> Set[Control]:
        return self._elements

    @property
    def elemt_count(self) -> int:
        return len(self._elements)

    @property
    def focusable(self) -> bool:
        return True

    @property
    def cur_focused(self) -> Control:
        return self._cur_focused

    @cur_focused.setter
    def cur_focused(self, value: Control):
        if value is None or value in self.elements:
            former: Control = self._cur_focused
            if former != value:
                if former and former.focusable:
                    former.on_lost_focus()
                self._cur_focused = value
                if value and value.focusable:
                    value.on_focused()
                self.on_focused_changed(self, former, value)

    @property
    def elemts_total_width(self):
        return sum(elemt.RenderWidth for elemt in self.elements)

    @property
    def elemts_total_height(self):
        return sum(elemt.RenderHeight for elemt in self.elements)

    @abstractmethod
    def go_next_focusable(self) -> bool:
        return False

    @abstractmethod
    def go_pre_focusable(self) -> bool:
        return False

    def on_input(self, char: chars.char) -> IsConsumed:
        if self.cur_focused:
            consumed = self.cur_focused.on_input(char)
            if consumed:
                return Consumed
            else:
                if keys.k_up == char:
                    return self.go_pre_focusable()
                elif keys.k_down == char or keys.k_enter == char or chars.c_tab_key == char:
                    return self.go_next_focusable()
                elif chars.c_esc == char:
                    self.on_exit_focus(self)
                    return Consumed
                return NotConsumed
        else:
            return NotConsumed

    @abstractmethod
    def switch_to_first_or_default_item(self):
        pass

    def switch_to(self, elemt: Control):
        self.cur_focused = elemt

    def reload(self):
        self.IsLayoutChanged = True
        for c in self.elements:
            c.reload()
        self.cache_layout()
