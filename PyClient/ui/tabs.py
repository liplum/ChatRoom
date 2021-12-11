from abc import ABCMeta
from threading import RLock
from typing import List, Iterable, Dict, Generator, Tuple, Hashable, Set

import GLOBAL
from GLOBAL import StringIO
from ui.core import *
from ui.outputs import buffer, CmdBkColor, CmdFgColor
from utils import is_in

tab_name2type: Dict[str, type] = {}
tab_type2name: Dict[type, str] = {}


def _add_tabtype(name: str, tabtype: "metatab"):
    tab_name2type[name] = tabtype
    tab_type2name[tabtype] = name


Need_Release_Resource = bool

Suspend = -1
Finished = 0


class group:

    def __init__(self, identity: Any = None):
        super().__init__()
        self.identity = identity
        self.tabs: List["tab"] = []
        self.tabs_set: Set["tab"] = set()

    def sort(self):
        pass

    def add(self, t: "tab") -> bool:
        if t not in self.tabs_set:
            self.tabs.append(t)
            self.tabs_set.add(t)
            return True
        return False

    def remove(self, t: "tab") -> bool:
        if t in self.tabs_set:
            self.tabs.remove(t)
            self.tabs_set.remove(t)
            return True
        return False

    def __eq__(self, other):
        if isinstance(other, group):
            return self.identity == other.identity
        return False

    def __hash__(self):
        identity = self.identity
        if isinstance(identity, Hashable):
            return hash(identity)
        else:
            return super().__hash__()

    def __len__(self) -> int:
        return len(self.tabs)

    def __iter__(self):
        return iter(self.tabs)

    def __repr__(self):
        return f"group({self.identity})"


class tablist(notifiable, painter):
    def __init__(self):
        super().__init__()
        self._cur: Optional["tab"] = None
        self.cur_group: Optional[group] = None
        self.groups: List[group] = []
        self.cur_group_index: int = 0
        self.cur_index: int = 0

        self.view_history = []
        self.max_view_history = 5

        self._on_curtab_changed = event()
        self._on_tablist_changed = event()
        self._lock = RLock()

    def match_or_create_group(self, t: "tab") -> group:
        for g in self.groups:
            if t.group_id == g.identity:
                return g
        g = group(t.group_id)
        self.groups.append(g)
        return g

    def match_group(self, t: "tab") -> Optional[group]:
        for g in self.groups:
            if t.group_id == g.identity:
                return g
        return None

    @property
    def tabs(self) -> List["tab"]:
        return [t for g in self.groups for t in g]

    @tabs.setter
    def tabs(self, value: List["tab"]):
        self.groups = [group()]
        for t in value:
            self.add(t)

    def unite_like_tabs(self):
        with self._lock:
            no_duplicate = []
            for t in self.tabs:
                if not is_in(t, no_duplicate, lambda a, b: a.equals(b)):
                    no_duplicate.append(t)

            self.tabs = no_duplicate
            if self.cur:
                former = self.cur_index
                self._reset_index()
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

    def _reset_index(self):
        with self._lock:
            cur = self.cur
            if cur:
                try:
                    self.cur_index = self.get_index(cur)
                except:
                    pass

    @property
    def tabs_count(self) -> int:
        with self._lock:
            return sum(len(g) for g in self.groups)

    @property
    def on_curtab_changed(self) -> event:
        """
        Para 1:tablist object

        Para 2:index of current tab

        Para 3:current tab

        :return: event(tablist,int,tab)
        """
        return self._on_curtab_changed

    @property
    def on_tablist_changed(self) -> event:
        """
        Para 1:tablist object

        Para 2:change type: True->add ; False->remove

        Para 3:operated tab

        :return: event(tablist,bool,tab)
        """
        return self._on_tablist_changed

    def __len__(self) -> int:
        with self._lock:
            return len(self.tabs)

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
                    self._reset_index()
                    self._cur.on_focused()
                self.on_curtab_changed(self, self.cur_index, tab)

    def add(self, t: "tab"):
        with self._lock:
            g = self.match_or_create_group(t)
            t.group = g
            g.add(t)
            self.on_tablist_changed(self, True, t)
            if self.cur is None:
                self.cur = t
            t.on_added()
            t.on_content_changed.add(self.on_subtab_content_changed)

    def replace(self, old_tab: Union[int, "tab"], new_tab: "tab"):
        with self._lock:
            if isinstance(old_tab, int):
                if 0 <= old_tab < self.tabs_count:
                    removed = self.get_by_index(item)
                    if removed is None:
                        return
                    pos = old_tab
                else:
                    return
            elif isinstance(old_tab, tab):
                removed = old_tab
                try:
                    pos = self.get_index(removed)
                    if pos is None:
                        return
                except:
                    return

            g = self.match_group(old_tab)
            new_tab.group = g

            new_tab.on_added()
            need_release_resource = new_tab.on_replaced(removed)
            new_tab.on_content_changed.add(self.on_subtab_content_changed)
            if need_release_resource:
                removed.on_removed()
            removed.on_content_changed.remove(self.on_subtab_content_changed)
            self.set_by_index(pos, new_tab)

            self.on_tablist_changed(self, False, removed)
            self.on_tablist_changed(self, True, new_tab)

            if self.cur is old_tab:
                self.cur = new_tab

    def on_subtab_content_changed(self, subtab):
        with self._lock:
            self.on_content_changed(self)

    def get_by_index(self, index: int) -> Optional["tab"]:
        total = 0
        for g in self.groups:
            glen = len(g)
            if total <= index < total + glen:
                rindex = index - total
                return g.tabs[rindex]
        return None

    def get_index(self, t: "tab") -> Optional[int]:
        total = 0
        for g in self.groups:
            try:
                rindex = g.tabs.index(t)
                return rindex + total
            except:
                pass
            total += len(g)
        return None

    def set_by_index(self, index: int, new_tab: "tab"):
        total = 0
        for g in self.groups:
            glen = len(g)
            if total <= index < total + glen:
                rindex = index - total
                g.tabs[rindex] = new_tab

    def remove(self, item: Union[int, "tab"]):
        with self._lock:
            if isinstance(item, int):
                if 0 <= item < self.tabs_count:
                    removed = self.get_by_index(item)
                    if removed:
                        g = t.group
                        g.remove(t)
                    else:
                        return
                else:
                    return
            elif isinstance(item, tab):
                removed = item
                try:
                    g = item.group
                    g.remove(item)
                except:
                    return
            else:
                return

            self.on_tablist_changed(self, False, removed)
            removed.on_removed()
            removed.on_content_changed.remove(self.on_subtab_content_changed)

            if self.tabs_count == 0:
                self.cur = None
            else:
                self.goto(self.cur_index)

    def remove_cur(self):
        with self._lock:
            cur = self.cur
            if cur:
                g = cur.group
                g.remove(cur)
            self.on_tablist_changed(self, False, cur)

            if self.tabs_count == 0:
                self.cur = None
            else:
                self.goto(self.cur_index)

    def switch(self):
        with self._lock:
            if len(self.view_history) >= 2:
                self.goto(self.view_history[-2])

    def goto(self, number: int):
        with self._lock:
            number = max(number, 0)
            number = min(number, self.tabs_count - 1)
            origin = self.cur
            target = self.get_by_index(number)
            if origin is target:
                return
            self.cur = target
            self.add_view_history(number)

    def next(self):
        with self._lock:
            self.goto(self.cur_index + 1)

    def back(self):
        with self._lock:
            self.goto(self.cur_index - 1)

    def clear(self):
        with self._lock:
            for t in list(self.tabs):
                self.remove(t)

    def add_view_history(self, number: int):
        with self._lock:
            self.view_history.append(number)
            if len(self.view_history) > self.max_view_history:
                self.view_history = self.view_history[-self.max_view_history:]

    def paint_on(self, buf: buffer):
        with self._lock:
            tab_count = len(self.tabs)
            cur = self.cur
            with StringIO() as separator:
                for i, t in enumerate(self.tabs):
                    bk = CmdBkColor.Yellow if t is cur else CmdBkColor.Green
                    fg = CmdFgColor.Black if t is cur else CmdFgColor.Violet
                    title = t.title
                    if GLOBAL.DEBUG:
                        displayed_title = f" [{t.group.identity}]{title} "
                    else:
                        displayed_title = f" {title} "
                    buf.addtext(displayed_title, fgcolor=fg, bkcolor=bk, end='')
                    repeated = " " if t is cur else "─"
                    second_line = repeated * len(displayed_title)
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

    def __iter__(self):
        with self._lock:
            return iter(self.tabs)


class metatab(ABCMeta):

    def __init__(cls, name, bases, dic):
        super().__init__(name, bases, dic)
        _add_tabtype(name, cls)


class tab(notifiable, reloadable, metaclass=metatab):
    def __init__(self, client: iclient, tablist: tablist):
        super().__init__()
        self.tablist: tablist = tablist
        self.client: iclient = client
        self._is_focused = False
        self._tab_priority = 1
        self._group_id = None
        self._group = None

    def on_input(self, char: chars.char) -> Generator:
        yield Finished

    def paint_on(self, buf: buffer):
        pass

    @classmethod
    def deserialize(cls, data: dict, client: iclient, tablist: tablist) -> "tab":
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
    def win(self) -> iwindow:
        return self.client.win

    @property
    def group_id(self) -> Any:
        return self._group_id

    @group_id.setter
    def group_id(self, value: Any):
        self._group_id = value

    @property
    def tab_priority(self) -> int:
        return self._tab_priority

    @tab_priority.setter
    def tab_priority(self, value: int):
        self._tab_priority = value

    @property
    def group(self) -> group:
        return self._group

    @group.setter
    def group(self, value: group):
        self._group = value


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
    def __init__(self, client: iclient, tablist: tablist):
        super().__init__(client, tablist)
        self._return_value: Optional[Any] = None
        self._returned = False
        self._on_returned = event()
        self._title_getter: Optional[Callable[[], str]] = None
        self._need_refresh_instant = False

    @property
    def on_returned(self) -> event:
        """
        Para 1:base_popup object

        :return: event(base_popup)
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
