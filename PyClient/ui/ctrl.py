from abc import ABC, abstractmethod

from ui.outputs import buffer


class control(ABC):
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
