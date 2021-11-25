from core.settings import entity
from ui.cmd_modes import common_hotkey
from ui.control.display_boards import display_board, DCenter, DRight
from ui.panels import *
from ui.tab.copyright import copyright_tab
from ui.tab.language import language_tab
from ui.tab.login import login_tab
from ui.tab.register import register_tab
from ui.tab.settings import settings_tab
from ui.tab.shared import *
from ui.tabs import *
from ui.themes import *


class main_menu_tab(tab):

    def __init__(self, client: iclient, tablist: tablist):
        super().__init__(client, tablist)
        self._title_texts = []
        main = stack()

        class _db_alignments:
            def __getitem__(self, item: int):
                if item == 3:
                    return DRight
                else:
                    return DCenter

        db_alignments = _db_alignments()

        def db_color():
            if entity().ColorfulMainMenu:
                return chaos_tube
            else:
                return tube

        db = display_board(MCGT(lambda: self._title_texts), lambda: db_alignments, theme=db_color)
        main.add(db)
        self.main = main
        self.main.on_content_changed.add(lambda _: self.on_content_changed(self))
        db.width = 40
        db.height = auto
        self.win = self.client.win

        def start():
            tab = self.win.new_chat_tab()
            tablist.replace(self, tab)

        b_start = i18n_button("controls.start", start)
        main.add(b_start)
        b_start.width = 10

        def login():
            tab = self.win.newtab(login_tab)
            tablist.replace(self, tab)

        b_login = i18n_button("controls.login", login)
        main.add(b_login)
        b_login.width = 10

        def register():
            tab = self.win.newtab(register_tab)
            tablist.replace(self, tab)

        b_register = i18n_button("controls.register", register)
        main.add(b_register)
        b_register.width = 10

        def quit_app():
            client.stop()

        b_quit = i18n_button("controls.quit", quit_app)
        main.add(b_quit)
        b_quit.width = 10

        def show_info():
            tab = self.win.newtab(copyright_tab)
            tablist.replace(self, tab)

        b_info = i18n_button("controls.info", show_info)
        b_info.prop(panel.No_Left_Margin, True).prop(stack.Horizontal_Alignment, align_left)
        b_info.width = 10
        main.add(b_info)

        def language():
            tab = self.win.newtab(language_tab)
            tablist.replace(self, tab)

        b_language = i18n_button("controls.language", language)
        b_language.prop(panel.No_Left_Margin, True).prop(stack.Horizontal_Alignment, align_left)
        b_language.width = 10
        main.add(b_language)

        def settings():
            tab = self.win.newtab(settings_tab)
            tablist.replace(self, tab)

        b_settings = i18n_button("controls.settings", settings)
        b_settings.prop(panel.No_Left_Margin, True).prop(stack.Horizontal_Alignment, align_left)
        b_settings.width = 10
        main.add(b_settings)

        main.left_margin = 10
        main.switch_to_first_or_default_item()

    def paint_on(self, buf: buffer):
        self.main.paint_on(buf)

    @property
    def title(self) -> str:
        return i18n.trans("tabs.main_menu_tab.name")

    def gen_title_texts(self):
        powered_by = i18n.trans("info.software.powered_by", "Python")
        try:
            powered_by_a, powered_by_b = powered_by.split('|')
        except:
            powered_by_a, powered_by_b = "", ""
        l: List[str] = [
            i18n.trans("info.software.name"),
            powered_by_a,
            powered_by_b,
            i18n.trans('info.software.author')
        ]
        self._title_texts = l

    def on_added(self):
        self.gen_title_texts()
        self.main.reload()

    def reload(self):
        self.gen_title_texts()
        self.main.reload()

    def on_input(self, char: chars.char) -> Is_Consumed:
        consumed = self.main.on_input(char)
        if not consumed:
            if keys.k_down == char or keys.k_enter == char or chars.c_tab_key == char:
                self.main.switch_to_first_or_default_item()
                return Consumed
            else:
                consumed = not common_hotkey(char, self, self.client, self.tablist, self.win)
                return consumed
        return Not_Consumed

    def on_replaced(self, last_tab: "tab") -> Need_Release_Resource:
        self.main.switch_to_first_or_default_item()
        return True
