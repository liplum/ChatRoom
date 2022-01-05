from typing import Dict, Union, Any

import utils
from GLOBAL import StringIO
from ui.Renders import *
from ui.shared import *

unlimited = "unlimited"
from ui.Elements import *


class Control(VisualElement, notifiable, painter, LogicalElement, inputable, reloadable, ABC):
    def __init__(self):
        super().__init__()
        self._in_container = False
        self._focused = False
        self._width = auto
        self._height = auto
        """Deprecated"""
        self._left_margin = 0
        self._onExitFocus = Event(Control)
        self._onLayoutChanged = Event(Control)

        def __onLayoutChangedHandler(self, prop_name):
            self.IsLayoutChanged = True
            self.on_content_changed(self)

        self.OnPropChanged.Add(__onLayoutChangedHandler)
        self.IsLayoutChanged = True
        self._attachProps: Dict[str, T] = {}

    @property
    def OnLayoutChanged(self) -> Event:
        """
        Para 1:Control object

        :return: Event(Control)
        """
        return self._onLayoutChanged

    @property
    def on_prop_changed(self) -> Event:
        """
        Para 1:Control object

        Para 2:property name

        :return: Event(Control,str)
        """
        return self._onPropChanged

    @property
    def on_exit_focus(self) -> Event:
        """
        Para 1:Control object

        :return: Event(Control)
        """
        return self._onExitFocus

    @property
    def OnExitFocus(self) -> Event:
        """
        Para 1:Control object

        :return: Event(Control)
        """
        return self._onExitFocus

    @property
    def width(self) -> PROP:
        """
        Gets the current tw of this Control
        :return:the column
        """
        return self._width

    @width.setter
    def width(self, value: PROP):
        """
        Sets the tw of this Control.
        How it works depends on the subclass's implementation
        :param value: PROP
        """
        if self.width != value:
            if value == auto:
                self._width = auto
            else:
                self._width = max(0, value)
                self._onLayoutPropChanged(self, "tw")

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
        Gets the current height of this Control
        :return:the row
        """
        return self._height

    @height.setter
    def height(self, value: PROP):
        """
        Sets the height of this Control.
        How it works depends on the subclass's implementation
        :param value: int(height)
        """
        if self.height != value:
            if value == auto:
                self._height = auto
            else:
                self._height = max(0, value)
                self._onLayoutPropChanged(self, "height")

    @property
    def focusable(self) -> bool:
        return False

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
        """Deprecated"""
        pass

    def reload(self):
        self.IsLayoutChanged = True
        self.cache_layout()

    @property
    def left_margin(self) -> int:
        """Deprecated"""
        return self._left_margin

    @left_margin.setter
    def left_margin(self, value: int):
        """Deprecated"""
        if value < 0:
            return
        if self._left_margin != value:
            self._left_margin = value
            self.on_prop_changed(self, "left_margin")

    def prop(self, key: str, value: T) -> "Control":
        if utils.get(self._attachProps, key) != value:
            self._attachProps[key] = value
            self.OnAttachPropChanged(self, key)
        return self

    def gprop(self, key: str) -> Optional[T]:
        if key in self._attachProps:
            return self._attachProps[key]
        return None

    def delprop(self, key: str) -> "Control":
        if key in self._attachProps:
            del self._attachProps[key]
        return self


class text_control(Control, ABC):

    def __init__(self):
        super().__init__()
        self._on_render_char: Optional[Callable[[str], str]] = None

    @property
    def on_render_char(self):
        return self._on_render_char

    @on_render_char.setter
    def on_render_char(self, value: Optional[Callable[[str], str]]):
        self._on_render_char = value

    def _render_chars(self, text: str) -> str:
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

    def notify_content_changed(self):
        self.on_content_changed(self)
        self.IsLayoutChanged = True


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


def AutoAdd(parent: Control, sub: Control):
    parent.AddVElem(sub)
    parent.AddLElem(sub)
    sub.VElemParent = parent
    sub.LElemParent = parent


def AutoRemove(parent: Control, sub: Control):
    parent.RemoveVElem(sub)
    parent.RemoveLElem(sub)
    if sub.VElemParent == parent:
        sub.VElemParent = None
    if sub.LElemParent == parent:
        sub.LElemParent = None
