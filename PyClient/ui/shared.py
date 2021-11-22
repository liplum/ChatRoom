from typing import TypeVar

import chars
from events import event
from ui.outputs import buffer

Is_Consumed = bool
Consumed = True
Not_Consumed = False
T = TypeVar('T')


class painter:
    def paint_on(self, buf: buffer):
        pass


class inputable:
    def on_input(self, char: chars.char) -> Is_Consumed:
        """
        When user types a char
        :param char: which be typed
        :return:whether this object consumed the char
        """
        return Not_Consumed


class reloadable:
    def reload(self):
        pass


class notifiable:
    def __init__(self):
        self._on_content_changed = event()

    @property
    def on_content_changed(self) -> event:
        """
        Para 1:current object

        :return: event(noticed)
        """
        return self._on_content_changed
