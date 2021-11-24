from abc import abstractmethod

from ui.ctrl import control
from ui.panels import panel
from ui.shared import *


class base_popup(panel):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def on_input(self, char: chars.char) -> Is_Consumed:
        return Not_Consumed

    def add(self, elemt: control) -> bool:
        return False

    def remove(self, elemt: control) -> bool:
        return False

    def clear(self):
        return

    def _add(self, elemt: control) -> bool:
        return super().add(elemt)

    def _remove(self, elemt: control) -> bool:
        return super().remove(elemt)

    def _clear(self):
        super().clear()


class popup(base_popup):

    def __init__(self):
        super().__init__()

    def on_input(self, char: chars.char) -> Is_Consumed:
        pass

    def paint_on(self, buf: buffer):
        pass

    def go_next_focusable(self) -> bool:
        pass

    def go_pre_focusable(self) -> bool:
        pass

    def switch_to_first_or_default_item(self):
        pass
