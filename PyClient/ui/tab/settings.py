from ui.tabs import *


class settings_tab(tab):
    @property
    def title(self) -> str:
        return "settings_tab"


add_tabtype("settings_tab", settings_tab)
