from Events import Event
from ui.Elements import *
from ui.outputs import buffer


class painter:
    def paint_on(self, buf: buffer):
        """
        Deprecated
        Paint all content on the buffer
        :param buf:screen buffer
        """
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
        super().__init__()
        self._onContentChanged = Event(notifiable)

    @property
    def on_content_changed(self) -> Event:
        """
        Para 1:notifiable object

        :return: Event(notifiable)
        """
        return self._onContentChanged

    @property
    def OnContentChanged(self) -> Event:
        """
        Para 1:notifiable object

        :return: Event(notifiable)
        """
        return self._onContentChanged
