import traceback
from collections import deque

import utils
from core.settings import entity as settings
from ui.tab.chat import chat_tab
from ui.tab.main_menu import main_menu_tab
from ui.tabs import *
from ui.tabs import Suspend
from utils import multiget, get

Focusable = Union[base_popup, tab]
CallStackItem = Tuple[Generator, Focusable]


class window(iwindow):

    def __init__(self, client: iclient):
        super().__init__(client)
        self.logger: "ilogger" = self.client.logger
        self._tablist: tablist = tablist()
        self.screen_buffer: Optional[buffer] = None
        self.tablist.on_content_changed.add(lambda _: self.client.mark_dirty())
        self.tablist.on_curtab_changed.add(lambda li, n, t: self.client.mark_dirty())
        self.tablist.on_tablist_changed.add(lambda li, mode, t: self.client.mark_dirty())
        self.network: "inetwork" = self.client.network
        self.popups: deque[base_popup] = deque()
        self.popup_return_values: Dict[base_popup, Any] = {}
        self.call_stack: deque[CallStackItem] = deque()

        def on_closed_last_tab(li: tablist, mode, t):
            if li.tabs_count == 0:
                self.client.stop()

        self.tablist.on_tablist_changed.add(on_closed_last_tab)

    def start(self):
        configs = settings()
        if configs.RestoreTabWhenRestart:
            self.restore_last_time_tabs()

    def stop(self):
        configs = settings()
        if configs.RestoreTabWhenRestart:
            self.store_unclosed_tabs()

    def restore_last_time_tabs(self):
        configs = settings()
        last_opened: Dict[str, List[dict]] = configs.LastOpenedTabs
        for tab_name, li in last_opened.items():
            if tab_name in tab_name2type:
                tabtype = tab_name2type[tab_name]
                if tabtype.serializable():
                    for entity in li:
                        try:
                            tab = tabtype.deserialize(entity, self.client, self.tablist)
                        except CannotRestoreTab:
                            continue
                        except Exception as e:
                            self.client.logger.warn(f"[Window]{e}\n{traceback.format_exc()}")
                            continue
                        if tab is not None:
                            self.tablist.add(tab)
        self.tablist.unite_like_tabs()

    def store_unclosed_tabs(self):
        self.tablist.unite_like_tabs()
        configs = settings()
        last_opened: Dict[str, List[dict]] = {}
        for tab in self.tablist.tabs:
            tabtype = type(tab)
            if tabtype in tab_type2name:
                if tabtype.serializable():
                    li = multiget(last_opened, tab_type2name[tabtype])
                    try:
                        dic = tabtype.serialize(tab)
                    except CannotStoreTab:
                        continue
                    except Exception as e:
                        self.client.logger.warn(f"[Window]{e}\n{traceback.format_exc()}")
                        continue
                    if dic is not None:
                        li.append(dic)
        configs["LastOpenedTabs"] = last_opened

    def gen_default_tab(self):
        if self.tablist.tabs_count == 0:
            t = self.newtab(main_menu_tab)
            self.tablist.add(t)

    def newtab(self, tabtype: Union[Type[T], str]) -> T:
        if isinstance(tabtype, str):
            ttype = get(tab_name2type, tabtype)
            if ttype:
                t = ttype(self.client, self.tablist)
            else:
                raise TabTypeNotFound(tab_name=tabtype)
        elif isinstance(tabtype, type):
            t = tabtype(self.client, self.tablist)
        else:
            raise TypeError(tabtype, type(tabtype))
        return t

    def new_chat_tab(self) -> chat_tab:
        return self.newtab(chat_tab)

    def prepare(self):
        self.screen_buffer = self.displayer.gen_buffer()

    def update_screen(self):
        utils.clear_screen()
        self.prepare()
        self.tablist.paint_on(self.screen_buffer)
        cur_painter = self.cur_painter
        if cur_painter:
            cur_painter.paint_on(self.screen_buffer)

        self.displayer.render(self.screen_buffer)

    def on_input(self, char):
        if len(self.popups) > 0:
            p = self.popups[0]
            p.on_focused()
            it = p.on_input(char)
            self.step(it, p)
            if not p.returned:
                return
        cur_item = self.cur_stack_item
        if cur_item:
            it, cur = cur_item
            self.call_stack.pop()
            self.step(it, cur)
        else:
            cur_focused = self.cur_focused
            if cur_focused:
                if not isinstance(cur_focused, base_popup):
                    it = cur_focused.on_input(char)
                    self.step(it, cur_focused)

    def _on_popup_returned(self, popup: base_popup):
        self.popup_return_values[popup] = popup.return_value
        self.popups.remove(popup)
        popup.on_lost_focus()
        popup.on_removed()
        if popup.need_refresh_instant:
            cur_item = self.cur_stack_item
            if cur_item:
                it, cur = cur_item
                self.call_stack.pop()
                self.step(it, cur)
        else:
            self.client.mark_dirty()

    @property
    def cur_painter(self):
        if len(self.popups) > 0:
            return self.popups[0]
        else:
            cur_item = self.cur_stack_item
            if cur_item:
                it, cur = cur_item
                return cur
            else:
                cur_tab = self.tablist.cur
                return cur_tab

    @property
    def cur_focused(self) -> Optional[Focusable]:
        if len(self.popups) > 0:
            return self.popups[0]
        else:
            cur_tab = self.tablist.cur
            return cur_tab

    @property
    def cur_stack_item(self) -> Optional[CallStackItem]:
        if len(self.call_stack) > 0:
            return self.call_stack[0]
        else:
            return None

    def add_string(self, string: str):
        curtab = self.tablist.cur
        if curtab:
            curtab.add_string(string)

    def reload(self):
        for t in self.tablist:
            t.reload()
        self.client.mark_dirty()

    def popup(self, popup: "base_popup") -> NoReturn:
        self.popups.append(popup)
        popup.on_content_changed.add(lambda _: self.client.mark_dirty())
        popup.on_returned.add(self._on_popup_returned)
        popup.on_added()
        self.client.mark_dirty()

    def retrieve_popup(self, popup: "base_popup") -> Optional[Any]:
        if popup in self.popup_return_values:
            value = self.popup_return_values[popup]
            del self.popup_return_values[popup]
            return value
        else:
            return None

    def step(self, it: Generator, focusable: Focusable):
        while True:
            try:
                rv = next(it)
            except StopIteration:
                break
            except Exception as e:
                raise e
            if rv == Suspend:
                self.call_stack.append((it, focusable))
                break
            elif isinstance(rv, Generator):
                self.step(rv, focusable)
                break

    @property
    def tablist(self) -> "tablist":
        return self._tablist

    def find_first_popup(self, predicate: Callable[["base_popup"], bool]) -> Optional["base_popup"]:
        for p in self.popups:
            try:
                if predicate(p):
                    return p
            except:
                pass
        return None
