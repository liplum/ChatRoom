from abc import ABC, abstractmethod
from io import StringIO
from typing import List, Optional, Type, Iterable, Union, TypeVar, Dict

import chars
from events import event
from ui.notice import notified
from ui.outputs import buffer, CmdBkColor, CmdFgColor

T = TypeVar('T')
Is_Consumed = bool


class tab(notified, ABC):
    def __init__(self, client: "client", tablist: "tablist"):
        super().__init__()
        self.tablist = tablist
        self.client = client

    def on_input(self, char: chars.char) -> Is_Consumed:
        return False

    def draw_on(self, buf: buffer):
        pass

    @classmethod
    def deserialize(cls, data: dict, client: "client", tablist: "tablist") -> "tab":
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

    def on_focused(self):
        pass

    def on_lost_focus(self):
        pass

    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other):
        return id(self) == id(other)


class tablist(notified):
    def __init__(self):
        super().__init__()
        self.tabs: List[tab] = []
        self._cur: Optional[tab] = None
        self.cur_index = 0
        self.view_history = []
        self.max_view_history = 5
        self._on_curtab_changed = event()
        self._on_tablist_changed = event()

    def unite_like_tabs(self):
        no_duplicate = dict.fromkeys(self.tabs)
        self.tabs = list(no_duplicate)
        if self.cur:
            self.cur_index = self.tabs.index(self._cur)

    def it_all_tabs_is(self, tabtype: Type[T]) -> Iterable[T]:
        for t in self.tabs:
            if isinstance(t, tabtype):
                yield t

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
    def cur(self) -> Optional[tab]:
        return self._cur

    @cur.setter
    def cur(self, value: Optional[tab]):
        changed = self._cur is not value
        if changed:
            if self._cur:
                self._cur.on_lost_focus()
            self._cur = value
            if self._cur:
                self.cur_index = self.tabs.index(self._cur)
                self._cur.on_focused()
            self.on_curtab_changed(self, self.cur_index, tab)

    def add(self, tab: "tab"):
        self.tabs.append(tab)
        self.on_tablist_changed(self, True, tab)
        if self.cur is None:
            self.cur = tab
        tab.on_added()
        tab.on_content_changed.add(lambda _: self.on_content_changed(self))

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

        removed.on_removed()
        new_tab.on_added()
        self.tabs.insert(pos, new_tab)

        self.on_tablist_changed(self, False, removed)
        self.on_tablist_changed(self, True, new_tab)

        if self.cur is old_tab:
            self.cur = new_tab

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

        if len(self.tabs) == 0:
            self.cur = None
        else:
            self.goto(self.cur_index)

    def remove_cur(self):
        cur = self.cur
        if cur:
            self.tabs.remove(self.cur)
        self.on_tablist_changed(self, False, cur)
        cur.on_removed()

        if len(self.tabs) == 0:
            self.cur = None
        else:
            self.goto(self.cur_index)

    def switch(self):
        if len(self.view_history) >= 2:
            self.goto(self.view_history[-2])

    def goto(self, number: int):
        number = max(number, 0)
        number = min(number, len(self.tabs) - 1)
        origin = self.cur
        target = self.tabs[number]
        if origin == target:
            return
        self.cur = target
        self.add_view_history(number)

    def next(self):
        self.goto(self.cur_index + 1)

    def back(self):
        self.goto(self.cur_index - 1)

    def add_view_history(self, number: int):
        self.view_history.append(number)
        if len(self.view_history) > self.max_view_history:
            self.view_history = self.view_history[-self.max_view_history:]

    def draw_on(self, buf: buffer):
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


tab_name2type: Dict[str, Type[tab]] = {}
tab_type2name: Dict[Type[tab], str] = {}


def add_tabtype(name: str, tabtype: Type[tab]):
    tab_name2type[name] = tabtype
    tab_type2name[tabtype] = name


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
