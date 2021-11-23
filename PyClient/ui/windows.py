import utils
from core.settings import entity as settings
from ui.tab.chat import chat_tab
from ui.tab.main_menu import main_menu_tab
from ui.tabs import *
from utils import multiget, get


class window(iwindow):
    def __init__(self, client: iclient):
        super().__init__(client)
        self.tablist: tablist = tablist()
        self.screen_buffer: Optional[buffer] = None
        self.tablist.on_content_changed.add(lambda _: self.client.mark_dirty())
        self.tablist.on_curtab_changed.add(lambda li, n, t: self.client.mark_dirty())
        self.tablist.on_tablist_changed.add(lambda li, mode, t: self.client.mark_dirty())
        self.network: "inetwork" = self.client.network

        def on_closed_last_tab(li: tablist, mode, t):
            if li.tabs_count == 0:
                self.client.stop()

        self.tablist.on_tablist_changed.add(on_closed_last_tab)

    def start(self):
        configs = settings()
        """
        from ui.tab.grid_tab import grid_tab
        t = self.newtab(grid_tab)
        from ui.tab.test_tab import test_tab
        t = self.newtab(test_tab)
        from ui.tab.main_menu import main_menu_tab
        t = self.newtab(main_menu_tab)
        from ui.tab.copyright import copyright_tab
        t = self.newtab(copyright_tab)
        self.tablist.cur = t
        """
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
                        except:
                            continue
                        if tab:
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
                    except:
                        continue
                    if dic:
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
        curtab = self.tablist.cur
        if curtab:
            curtab.paint_on(self.screen_buffer)

        self.displayer.render(self.screen_buffer)

    def on_input(self, char) -> Is_Consumed:
        curtab = self.tablist.cur
        if curtab:
            return curtab.on_input(char)
        return Not_Consumed

    def add_string(self, string: str):
        curtab = self.tablist.cur
        if curtab:
            curtab.add_string(string)

    def reload(self):
        for t in self.tablist:
            t.reload()
        self.client.mark_dirty()
