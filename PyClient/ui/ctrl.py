from abc import ABC, abstractmethod
from typing import Callable, Collection, Dict, Optional, Union, Any, Tuple

from GLOBAL import StringIO
from ui.shared import *

auto = "auto"
PROP = TypeVar('PROP', str, int)
unlimited = "unlimited"


class control(notifiable, painter, inputable, reloadable, ABC):
    def __init__(self):
        super().__init__()
        self._in_container = False
        self._focused = False
        self._width = auto
        self._height = auto
        self._left_margin = 0
        self._on_prop_changed = event()
        self._on_exit_focus = event()
        self._layout_changed = True
        self.on_prop_changed.add(self._on_layout_changed)
        self._attach_prop: Dict[str, T] = {}

    def _on_layout_changed(self, self2, prop_name):
        self.on_content_changed(self)
        self._layout_changed = True

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
        if self.width != value:
            if value == auto:
                self._width = auto
            else:
                self._width = max(0, value)
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
        if self.height != value:
            if value == auto:
                self._height = auto
            else:
                self._height = max(0, value)
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

    def cache_layout(self):
        pass

    def reload(self):
        self._layout_changed = True
        self.cache_layout()

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

    def prop(self, key: str, value: T) -> "control":
        self._attach_prop[key] = value
        return self

    def gprop(self, key: str) -> Optional[T]:
        if key in self._attach_prop:
            return self._attach_prop[key]
        return None

    def delprop(self, key: str) -> "control":
        if key in self._attach_prop:
            del self._attach_prop[key]
        return self


class text_control(control, ABC):

    def __init__(self):
        super().__init__()
        self._on_render_char: Optional[Callable[[str], str]] = None

    @property
    def on_render_char(self):
        return self._on_render_char

    @on_render_char.setter
    def on_render_char(self, value: Optional[Callable[[str], str]]):
        self._on_render_char = value

    def _render_chars(self, text: str):
        func = self.on_render_char
        if func:
            with StringIO as s:
                for char in text:
                    s.write(func(char))
                return s.getvalue()
        else:
            return text

    def _render_charsIO(self, IO, text: str):
        func = self.on_render_char
        if func:
            for char in text:
                IO.write(func(char))
        else:
            IO.write(text)


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


class multi_content_getter:
    def __init__(self, getter: Callable[[], Collection[str]]):
        self.getter = getter

    def get(self) -> Collection[str]:
        return self.getter()

    def __call__(self, *args, **kwargs):
        return self.getter()


MCGT = multi_content_getter


def MCGT_fix_text(texts: Collection[str]) -> multi_content_getter:
    return multi_content_getter(lambda: texts)


ContentGetter = Union[Callable[[], str], content_getter, str]

ContentsGetter = Union[Callable[[], Collection[str]], multi_content_getter, Collection[str]]


class multi_contentX_getter:
    def __init__(self, getter: Callable[[], Collection[Tuple[str, Any]]]):
        self.getter = getter

    def get(self) -> Collection[Tuple[str, Any]]:
        return self.getter()

    def __call__(self, *args, **kwargs):
        return self.getter()


ContentsXGetter = Union[multi_contentX_getter, Collection[Tuple[str, Any]]]
MCGXT = multi_contentX_getter
