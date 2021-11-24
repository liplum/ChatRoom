from ui.cmd_modes import common_hotkey
from ui.control.checkboxes import checkbox
from ui.panels import *
from ui.tab.shared import *
from ui.tabs import *


class settings_tab(tab):

    def __init__(self, client: iclient, tablist: tablist):
        super().__init__(client, tablist)
        self.win = self.client.win
        settings = gen_grid(4, [column(30), column(10)])
        main = stack()
        main.on_content_changed.add(lambda _: self.on_content_changed(self))
        self.main = main
        settings[0, 0] = i18n_label("settings.RestoreTabWhenRestart")
        settings[0, 1] = checkbox(True, theme=turn_on_off_check_theme)
        settings.elemt_interval_w = 4
        main.add(settings)
        main.switch_to_first_or_default_item()

    @property
    def title(self) -> str:
        return i18n.trans("tabs.settings_tab.name")

    def paint_on(self, buf: buffer):
        self.main.paint_on(buf)

    def on_input(self, char: chars.char) -> Is_Consumed:
        consumed = self.main.on_input(char)
        if consumed:
            return Consumed
        if not consumed:
            if keys.k_down == char or keys.k_enter == char or chars.c_tab_key == char:
                self.main.switch_to_first_or_default_item()
                return Consumed
            else:
                consumed = not common_hotkey(char, self, self.client, self.tablist, self.win)
                return consumed
        return Not_Consumed
