from typing import TypeVar

import chars
from Events import Event
from ui.outputs import buffer

IsConsumed = bool
Consumed = True
NotConsumed = False
T = TypeVar('T')


class painter:
    def paint_on(self, buf: buffer):
        pass


class inputable:
    def on_input(self, char: chars.char) -> IsConsumed:
        """
        When user types a char
        :param char: which be typed
        :return:whether this object consumed the char
        """
        return NotConsumed


class reloadable:
    def reload(self):
        pass


class notifiable:
    def __init__(self):
        self._on_content_changed = Event(notifiable)

    @property
    def on_content_changed(self) -> Event:
        """
        Para 1:notifiable object

        :return: Event(notifiable)
        """
        return self._on_content_changed
