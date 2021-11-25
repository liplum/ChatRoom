from abc import ABCMeta
from typing import List, Optional, Iterable, Dict

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


class tablist(notifiable, painter):
    def __init__(self):
        super().__init__()
        self.tabs: List["tab"] = []
        self._cur: Optional["tab"] = None
        self.cur_index = 0
        self.view_history = []
        self.max_view_history = 5
        self._on_curtab_changed = event()
        self._on_tablist_changed = event()

    def unite_like_tabs(self):
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
        for t in self.tabs:
            if isinstance(t, tabtype):
                yield t

    def _reset_index(self):
        cur = self.cur
        if cur:
            try:
                self.cur_index = self.tabs.index(cur)
            except:
                pass

    @property
    def tabs_count(self) -> int:
        return len(self.tabs)

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
        return len(self.tabs)

    @property
    def cur(self) -> Optional["tab"]:
        return self._cur

    @cur.setter
    def cur(self, value: Optional["tab"]):
        changed = self._cur is not value
        if changed:
            if self._cur:
                self._cur.on_lost_focus()
            self._cur = value
            if self._cur:
                self._reset_index()
                self._cur.on_focused()
            self.on_curtab_changed(self, self.cur_index, tab)

    def add(self, tab: "tab"):
        self.tabs.append(tab)
        self.on_tablist_changed(self, True, tab)
        if self.cur is None:
            self.cur = tab
        tab.on_added()
        tab.on_content_changed.add(self.on_subtab_content_changed)

    def replace(self, old_tab: Union[int, "tab"], new_tab: "tab"):
        if isinstance(old_tab, int):
            if 0 <= old_tab < len(self.tabs):
                removed = self.tabs[old_tab]
                del self.tabs[old_tab]
                pos = old_tab
            else:
                return
        elif isinstance(old_tab, tab):
            removed = old_tab
            try:
                pos = self.tabs.index(removed)
            except:
                return
            del self.tabs[pos]

        new_tab.on_added()
        need_release_resource = new_tab.on_replaced(removed)
        new_tab.on_content_changed.add(self.on_subtab_content_changed)
        if need_release_resource:
            removed.on_removed()
        removed.on_content_changed.remove(self.on_subtab_content_changed)
        self.tabs.insert(pos, new_tab)

        self.on_tablist_changed(self, False, removed)
        self.on_tablist_changed(self, True, new_tab)

        if self.cur is old_tab:
            self.cur = new_tab

    def on_subtab_content_changed(self, subtab):
        self.on_content_changed(self)

    def insert(self, index: int, new_tab: "tab"):
        self.tabs.insert(index, new_tab)
        self.on_tablist_changed(self, True, new_tab)

    def remove(self, item: Union[int, "tab"]):
        if isinstance(item, int):
            if 0 <= item < len(self.tabs):
                removed = self.tabs[item]
                del self.tabs[item]
        elif isinstance(item, tab):
            removed = item
            try:
                self.tabs.remove(removed)
            except:
                return

        self.on_tablist_changed(self, False, removed)
        removed.on_removed()
        removed.on_content_changed.remove(self.on_subtab_content_changed)

        if len(self.tabs) == 0:
            self.cur = None
        else:
            self.goto(self.cur_index)

    def remove_cur(self):
        cur = self.cur
        if cur:
            self.tabs.remove(cur)
        self.on_tablist_changed(self, False, cur)

        if len(self.tabs) == 0:
            self.cur = None
        else:
            self.goto(self.cur_index)

    def switch(self):
        if len(self.view_history) >= 2:
            self.goto(self.view_history[-2])

    def goto(self, number: int):
        number = max(number, 0)
        number = min(number, self.tabs_count - 1)
        origin = self.cur
        target = self.tabs[number]
        if origin is target:
            return
        self.cur = target
        self.add_view_history(number)

    def next(self):
        self.goto(self.cur_index + 1)

    def back(self):
        self.goto(self.cur_index - 1)

    def clear(self):
        for t in list(self.tabs):
            self.remove(t)

    def add_view_history(self, number: int):
        self.view_history.append(number)
        if len(self.view_history) > self.max_view_history:
            self.view_history = self.view_history[-self.max_view_history:]

    def paint_on(self, buf: buffer):
        tab_count = len(self.tabs)
        cur = self.cur
        with StringIO() as separator:
            for i, t in enumerate(self.tabs):
                bk = CmdBkColor.Yellow if t is cur else CmdBkColor.Green
                fg = CmdFgColor.Black if t is cur else CmdFgColor.Violet
                title = t.title
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
        return iter(self.tabs)


class metatab(ABCMeta):

    def __init__(cls, name, bases, dic):
        super().__init__(name, bases, dic)
        _add_tabtype(cls.__qualname__, cls)


class tab(notifiable, inputable, reloadable, metaclass=metatab):
    def __init__(self, client: iclient, tablist: tablist):
        super().__init__()
        self.tablist: tablist = tablist
        self.client: iclient = client
        self._is_focused = False

    def on_input(self, char: chars.char) -> Is_Consumed:
        return Not_Consumed

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
