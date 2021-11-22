from abc import ABC, abstractmethod
from typing import Callable

from ui.shared import *

auto = "auto"
PROP = TypeVar('PROP', str, int)


class control(notifiable, painter, inputable, reloadable, ABC):
    def __init__(self):
        super().__init__()
        self._in_container = False
        self._focused = False
        self._width = auto
        self._height = auto
        self._on_prop_changed = event()
        self._on_exit_focus = event()

    @property
    def on_exit_focus(self) -> event:
        """
        Para 1:control object

        :return: event(control)
        """
        return self._on_exit_focus

    @property
    def on_prop_changed(self) -> event:
        """
        Para 1:control object

        Para 2:property name

        :return: event(control,str)
        """
        return self._on_prop_changed

    @property
    def width(self) -> PROP:
        """
        Gets the current width of this control
        :return:the column
        """
        return self._width

    @width.setter
    def width(self, value: PROP):
        """
        Sets the width of this control.
        How it works depends on the subclass's implementation
        :param value: PROP
        """
        if value != auto and value < 0:
            value = 0
        if self._width != value:
            self._width = value
            self.on_prop_changed(self, "width")

    @property
    def render_height(self) -> int:
        height = self.height
        if height != auto:
            return height
        else:
            raise NotImplementedError()

    @property
    def render_width(self) -> int:
        width = self.width
        if width != auto:
            return width
        else:
            raise NotImplementedError()

    @property
    def height(self) -> PROP:
        """
        Gets the current height of this control
        :return:the row
        """
        return self._height

    @height.setter
    def height(self, value: PROP):
        """
        Sets the height of this control.
        How it works depends on the subclass's implementation
        :param value: int(height)
        """
        if value != auto and value < 0:
            value = 0
        if self._height != value:
            self._height = value
            self.on_prop_changed(self, "height")

    @abstractmethod
    def paint_on(self, buf: buffer):
        """
        Paint all content on the buffer
        :param buf:screen buffer
        """
        pass

    @property
    @abstractmethod
    def focusable(self) -> bool:
        pass

    @property
    def in_container(self) -> bool:
        return self._in_container

    @in_container.setter
    def in_container(self, value: bool):
        self._in_container = value

    def __hash__(self):
        return id(self)

    @property
    def is_focused(self) -> bool:
        return self._focused

    def on_focused(self):
        self._focused = True

    def on_lost_focus(self):
        self._focused = False


class content_getter:
    def __init__(self, getter: Callable[[], str]):
        self.getter = getter

    def get(self) -> str:
        return self.getter()

    def __call__(self, *args, **kwargs):
        return self.getter()


CGT = content_getter


def CGT_fix_text(text: str) -> content_getter:
    return content_getter(lambda: text)
