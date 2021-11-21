from ui.tabs import *


class main_menu_tab(tab):

    def __init__(self, client: "client", tablist: tablist):
        super().__init__(client, tablist)

    @property
    def title(self) -> str:
        return "main_menu_tab"


add_tabtype("main_menu_tab", main_menu_tab)
