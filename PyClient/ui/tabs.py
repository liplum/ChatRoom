from abc import ABCMeta
from threading import RLock

import GLOBAL
import utils
from GLOBAL import StringIO
from ui.Controls import Control
from ui.Core import *
from ui.Renders import *
from ui.coroutines import Finished
from ui.outputs import buffer, CmdBkColor, CmdFgColor
from utils import is_in

tab_name2type: Dict[str, type] = {}
tab_type2name: Dict[type, str] = {}


def _add_tabtype(name: str, tabtype: "metatab"):
    tab_name2type[name] = tabtype
    tab_type2name[tabtype] = name


Need_Release_Resource = bool


class tablist(Control):
    def __init__(self):
        super().__init__()
        self._cur: Optional["tab"] = None
        self._tabs: List["tab"] = []
        self.cur_index: Optional[int] = None

        self.view_history = []
        self.max_view_history = 5

        self._on_curtab_changed = Event(tablist, (int, type(None)), (tab, type(None)))
        self._on_tablist_changed = Event(tablist, bool, tab)
        self._lock = RLock()

    @property
    def tabs(self) -> List["tab"]:
        return self._tabs

    @tabs.setter
    def tabs(self, value: List["tab"]):
        self._tabs = value

    def unite_like_tabs(self):
        with self._lock:
            no_duplicate = []
            for t in self.tabs:
                if not is_in(t, no_duplicate, lambda a, b: a.equals(b)):
                    no_duplicate.append(t)

            self.tabs = no_duplicate
            if self.cur:
                former = self.cur_index
                self.reset_index()
                if self.cur_index != former:
                    self.on_curtab_changed(self, self.cur_index, self.cur)

    def it_all_tabs_is(self, tabtype: Type[T]) -> Iterable[T]:
        with self._lock:
            return (t for t in self.tabs if isinstance(t, tabtype))

    def find_first(self, predicate: Callable[["tab"], bool]) -> Optional[Tuple["tab", int]]:
        with self._lock:
            i = 0
            for t in self.tabs:
                try:
                    if predicate(t):
                        return t, i
                except:
                    pass
                i += 1
            return None

    def reset_index(self):
        with self._lock:
            cur = self.cur
            if cur:
                self.cur_index = self.GetIndex(cur)

    @property
    def tabs_count(self) -> int:
        with self._lock:
            return len(self.tabs)

    @property
    def on_curtab_changed(self) -> Event:
        """
        Para 1:tablist object

        Para 2:index of current tab (nullable)

        Para 3:current tab (nullable)

        :return: Event(tablist,Optional[int],Optional[tab])
        """
        return self._on_curtab_changed

    @property
    def on_tablist_changed(self) -> Event:
        """
        Para 1:tablist object

        Para 2:change type: True->add ; False->remove

        Para 3:operated tab

        :return: Event(tablist,bool,tab)
        """
        return self._on_tablist_changed

    def __len__(self) -> int:
        return self.tabs_count

    @property
    def cur(self) -> Optional["tab"]:
        with self._lock:
            return self._cur

    @cur.setter
    def cur(self, value: Optional["tab"]):
        with self._lock:
            changed = self._cur is not value
            if changed:
                if self._cur:
                    self._cur.on_lost_focus()
                self._cur = value
                if self._cur:
                    self.reset_index()
                    self._cur.on_focused()
                self.on_curtab_changed(self, self.cur_index, value)

    def add(self, t: "tab"):
        with self._lock:
            self.tabs.append(t)
            self.reset_index()
            self.on_tablist_changed(self, True, t)
            if self.cur is None:
                self.cur = t
            t.on_added()
            t.on_content_changed.Add(self.on_subtab_content_changed)

    def replace(self, old_tab: Union[int, "tab"], new_tab: "tab"):
        if isinstance(old_tab, int):
            if 0 <= old_tab < self.tabs_count:
                removed: "tab" = self.GetTabByIndex(old_tab)
                self.DeleteTabByIndex(old_tab)
                pos: int = old_tab
            else:
                return
        elif isinstance(old_tab, tab):
            removed: "tab" = old_tab
            pos: Optional[int] = self.GetIndex(removed)
            if pos is None:
                return

        new_tab.on_added()
        need_release_resource = new_tab.on_replaced(removed)
        new_tab.on_content_changed.Add(self.on_subtab_content_changed)
        if need_release_resource:
            removed.on_removed()

        removed.on_content_changed.Remove(self.on_subtab_content_changed)
        self.SetTabByIndex(pos, new_tab)

        self.on_tablist_changed(self, False, removed)
        self.on_tablist_changed(self, True, new_tab)

        if self.cur is old_tab:
            self.cur = new_tab

    def on_subtab_content_changed(self, subtab):
        with self._lock:
            self.on_content_changed(self)

    def GetTabByIndex(self, index: Optional[int]) -> Optional["tab"]:
        try:
            return self.tabs[index]
        except:
            return None

    def GetIndex(self, t: Optional["tab"]) -> Optional[int]:
        if t is None:
            return None
        try:
            return self.tabs.index(t)
        except:
            return None

    def SetTabByIndex(self, index: int, new_tab: "tab"):
        if 0 <= index < self.tabs_count:
            self.tabs[index] = new_tab

    def DeleteTabByIndex(self, index: int):
        if 0 <= index < self.tabs_count:
            del self.tabs[index]

    def DeleteTab(self, t: "tab"):
        if t in self.tabs:
            self.tabs.remove(t)
            return True
        else:
            return False

    def remove(self, item: Union[int, "tab"]):
        if isinstance(item, int):
            if 0 <= item < self.tabs_count:
                removed: "tab" = self.GetTabByIndex(item)
                self.DeleteTabByIndex(item)
            else:
                return
        elif isinstance(item, tab):
            removed: "tab" = item
            try:
                self.DeleteTab(removed)
            except:
                return
        else:
            return

        self.on_tablist_changed(self, False, removed)
        removed.on_removed()
        removed.on_content_changed.Remove(self.on_subtab_content_changed)

        if self.tabs_count == 0:
            self.cur = None
        else:
            self.goto(self.cur_index)

    def remove_cur(self):
        cur = self.cur
        if cur:
            self.DeleteTab(cur)
        self.on_tablist_changed(self, False, cur)

        if self.tabs_count == 0:
            self.cur = None
        else:
            self.goto(self.cur_index)

    def switch(self):
        if len(self.view_history) >= 2:
            self.goto(self.view_history[-2])

    def goto(self, number: Optional[int]):
        if number is None:
            origin = self.cur
            if origin is target:
                return
            self.cur = None
        else:
            number = max(number, 0)
            number = min(number, self.tabs_count - 1)
            origin = self.cur
            target = self.GetTabByIndex(number)
            if origin is target:
                return
            self.cur = target
            self.add_view_history(number)

    def next(self):
        cur_index = self.cur_index
        if cur_index is None:
            self.goto(0)
        else:
            self.goto(cur_index + 1)

    def back(self):
        cur_index = self.cur_index
        if cur_index is None:
            self.goto(0)
        else:
            self.goto(self.cur_index - 1)

    def clear(self):
        for t in self.tabs:
            self.remove(t)

    def add_view_history(self, number: int):
        self.view_history.append(number)
        if len(self.view_history) > self.max_view_history:
            self.view_history = self.view_history[-self.max_view_history:]

    def paint_on(self, buf: buffer):
        tab_count = self.tabs_count
        cur = self.cur
        with StringIO() as separator:
            for i, t in enumerate(self.tabs):
                bk = CmdBkColor.Yellow if t is cur else CmdBkColor.Green
                fg = CmdFgColor.Black if t is cur else CmdFgColor.Violet
                title = t.title
                if GLOBAL.DEBUG:
                    displayed_title = f" {title} "
                else:
                    displayed_title = f" {title} "
                buf.addtext(displayed_title, fgcolor=fg, bkcolor=bk, end='')
                repeated = " " if t is cur else "─"
                second_line = utils.repeat(repeated, len(displayed_title))
                separator.write(second_line)
                if i + 1 < tab_count:
                    buf.addtext("│", end='')
                    if t is cur:
                        separator.write("└")
                    elif i + 1 < tab_count and self.tabs[i + 1] is cur:
                        separator.write("┘")
                    else:
                        separator.write("┴")
            buf.addtext()
            buf.addtext(separator.getvalue())

    def Arrange(self, width: Optional[int] = None, height: Optional[int] = None):
        pass

    def PaintOn(self, canvas: Canvas):
        tab_count = self.tabs_count
        cur = self.cur
        names = StrWriter(canvas, 0, 0, canvas.Width, 1)
        separator = StrWriter(canvas, 0, 1, canvas.Width, 1)
        for i, t in enumerate(self.tabs):
            bk = BK.Yellow if t is cur else BK.Green
            fg = FG.Black if t is cur else FG.Violet
            title = t.title
            if GLOBAL.DEBUG:
                displayed_title = f" {title} "
            else:
                displayed_title = f" {title} "
            names.Write(displayed_title, bk, fg)
            repeated = " " if t is cur else "─"
            second_line = utils.repeat(repeated, len(displayed_title))
            separator.Write(second_line)
            if i + 1 < tab_count:
                names.Write("│")
                if t is cur:
                    separator.Write("└")
                elif i + 1 < tab_count and self.tabs[i + 1] is cur:
                    separator.Write("┘")
                else:
                    separator.Write("┴")

    def __iter__(self):
        with self._lock:
            return iter(self.tabs)


class metatab(ABCMeta):

    def __init__(cls, name, bases, dic):
        super().__init__(name, bases, dic)
        _add_tabtype(name, cls)


class tab(Control, metaclass=metatab):
    def __init__(self, client: IClient, tablist: tablist):
        super().__init__()
        self.tablist: tablist = tablist
        self.client: IClient = client
        self._is_focused = False
        self._tab_priority = 1
        self._group_id = None
        self._group = None
        self._on_group_id_changed = Event(tab, object, object)

    @property
    def on_group_id_changed(self) -> Event:
        """
        Para 1:tab object

        Para 2:old group id

        Para 3:new group id

        :return: Event(tab,object,object)
        """
        return self._on_group_id_changed

    def on_input(self, char: chars.char) -> Generator:
        yield Finished

    @classmethod
    def deserialize(cls, data: dict, client: IClient, tablist: tablist) -> "tab":
        pass

    @classmethod
    def serialize(cls, self: "tab") -> dict:
        pass

    @classmethod
    def serializable(cls) -> bool:
        return False

    @property
    @abstractmethod
    def title(self) -> str:
        pass

    def add_string(self, string: str):
        pass

    def on_added(self):
        pass

    def on_removed(self):
        pass

    def on_replaced(self, last_tab: "tab") -> Need_Release_Resource:
        return True

    def on_focused(self):
        self._is_focused = True

    def on_lost_focus(self):
        self._is_focused = False

    @property
    def is_focused(self) -> bool:
        return self._is_focused

    def equals(self, tab: "tab"):
        return id(self) == id(tab)

    def new_popup(self, popup_type: Type[T], *args, **kwargs) -> T:
        return popup_type(self.client, self.tablist, *args, **kwargs)

    @property
    def win(self) -> IApp:
        return self.client.App

    @property
    def tab_priority(self) -> int:
        return self._tab_priority

    @tab_priority.setter
    def tab_priority(self, value: int):
        self._tab_priority = value


class CannotRestoreTab(Exception):
    def __init__(self, tabtype: Type[tab]):
        super().__init__()
        self.tabtype = tabtype


class CannotStoreTab(Exception):
    def __init__(self, tab: tab):
        super().__init__()
        self.tab = tab


class TabTypeNotFound(Exception):
    def __init__(self, tab_name: str):
        super().__init__()
        self.tab_name = tab_name


TitleGetter = Optional[Callable[[], str]]


class base_popup(tab, ABC):
    def __init__(self, client: IClient, tablist: tablist):
        super().__init__(client, tablist)
        self._return_value: Optional[Any] = None
        self._returned = False
        self._on_returned = Event(base_popup)
        self._title_getter: Optional[Callable[[], str]] = None
        self._need_refresh_instant = False

    @property
    def on_returned(self) -> Event:
        """
        Para 1:base_popup object

        :return: Event(base_popup)
        """
        return self._on_returned

    def _Return(self, value: Optional[Any]):
        self._return_value = value
        self._returned = True
        self._on_returned(self)

    @property
    def return_value(self) -> Optional[Any]:
        return self._return_value

    @property
    def returned(self) -> bool:
        return self._returned

    @property
    def title(self) -> str:
        return self.get_title()

    @property
    def title_getter(self) -> TitleGetter:
        return self._title_getter

    @title_getter.setter
    def title_getter(self, value: TitleGetter):
        self._title_getter = value

    def get_title(self) -> str:
        getter = self.title_getter
        if getter:
            return getter()
        else:
            return ""

    @property
    def need_refresh_instant(self) -> bool:
        return self._need_refresh_instant

    @need_refresh_instant.setter
    def need_refresh_instant(self, value: bool):
        self._need_refresh_instant = value
