from lazys import lazy
from ui.tabs import *

main_menu_type = lazy(lambda: utils.get(tab_name2type, "main_menu_tab"))


def close_cur_tab(tablist: tablist, win: IApp, tab: Optional[tab] = None):
    if tab is None and (tab := tablist.cur) is None:
        return
    if tablist.tabs_count == 1:
        menu_type = main_menu_type()
        if not isinstance(tab, menu_type):
            main_menu = win.newtab(menu_type)
            tablist.replace(tab, main_menu)
    else:
        tablist.remove(tab)
