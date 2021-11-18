from abc import ABC, abstractmethod
from typing import Callable

import chars
from events import event
from ui.outputs import buffer


class control(ABC):
    def __init__(self):
        self._on_content_changed = event()

    @property
    def on_content_changed(self) -> event:
        """
        Para 1:textbox object

        :return: event(control)
        """
        return self._on_content_changed

    @property
    @abstractmethod
    def width(self) -> int:
        """
        Gets the current width of this control
        :return:the column
        """
        pass

    @width.setter
    def width(self, value: int):
        """
        Sets the width of this control.
        Whether it works depends on the subclass's implementation
        :param value: int(width)
        """
        pass

    @property
    @abstractmethod
    def height(self) -> int:
        """
        Gets the current height of this control
        :return:the row
        """
        pass

    @height.setter
    def height(self, value: int):
        """
        Sets the height of this control.
        Whether it works depends on the subclass's implementation
        :param value: int(height)
        """
        pass

    def draw_on(self, buf: buffer):
        """
        Draw all content on the buffer
        :param buf:screen buffer
        """
        pass

    def on_focused(self):
        pass

    def on_lost_focus(self):
        pass

    @property
    @abstractmethod
    def focusable(self) -> bool:
        pass

    @property
    def focused(self) -> bool:
        return False

    def on_input(self, char: chars.char):
        pass


class content_getter:
    def __init__(self, getter: Callable[[], str]):
        self.getter = getter

    def get(self) -> str:
        return self.getter()

    def __call__(self, *args, **kwargs):
        return self.getter()
