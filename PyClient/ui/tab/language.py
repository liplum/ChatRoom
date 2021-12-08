from core.settings import entity
from ui.cmd_modes import common_hotkey
from ui.panel.stacks import stack
from ui.panels import *
from ui.tab.shared import *
from ui.tabs import *


class language_tab(tab):

    def __init__(self, client: iclient, tablist: tablist):
        super().__init__(client, tablist)
        self.main: Optional[control] = None
        self.last_tab = None

        def on_quit():
            if self.last_tab:
                tablist.replace(self, self.last_tab)
            else:
                tablist.remove(self)

        b_quit = i18n_button("controls.quit", on_quit)
        self.b_quit = b_quit

    def on_added(self):
        self.gen_language_list()
        main = stack()
        self.main = main
        main.on_content_changed.add(lambda _: self.on_content_changed(self))
        lang_tabs = stack()
        main.add(lang_tabs)
        main.add(self.b_quit)
        main.left_margin = 10
        configs = entity()
        self.cur_lang_button: Optional[button] = None

        def gen(lang):
            def on_change():
                try:
                    i18n.load(lang, strict=True)
                    succeed = True
                except:
                    succeed = False
                if succeed:
                    self.win.reload()
                    configs.set("Language", lang)

            return on_change

        for lang in self.all_languages:
            b = i18n_button(f"langs.{lang}", gen(lang))
            if lang == i18n.cur_lang:
                self.cur_lang_button = b
            b.width = 20
            lang_tabs.add(b)
        main.switch_to_first_or_default_item()
        if self.cur_lang_button:
            lang_tabs.switch_to(self.cur_lang_button)

    @property
    def title(self) -> str:
        return i18n.trans("tabs.language_tab.name")

    def gen_language_list(self):
        self.all_languages = i18n.all_languages()

    def on_replaced(self, last_tab: "tab") -> Need_Release_Resource:
        self.last_tab = last_tab
        return False

    def paint_on(self, buf: buffer):
        if self.main:
            self.main.paint_on(buf)

    def on_input(self, char: chars.char) -> Generator:
        if self.main:
            consumed = self.main.on_input(char)
            if not consumed:
                if keys.k_down == char or keys.k_enter == char or chars.c_tab_key == char:
                    self.main.switch_to_first_or_default_item()
                else:
                    consumed = not common_hotkey(char, self, self.client, self.tablist, self.win)
        yield Finished

    def reload(self):
        if self.main:
            self.main.reload()

    @classmethod
    def deserialize(cls, data: dict, client: iclient, tablist: tablist) -> "tab":
        return language_tab(client, tablist)

    @classmethod
    def serialize(cls, self: "tab") -> dict:
        return {}

    @classmethod
    def serializable(cls) -> bool:
        return True
