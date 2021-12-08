from core.settings import entity
from ui.cmd_modes import common_hotkey
from ui.control.display_boards import display_board, DCenter, DRight
from ui.panel.stacks import align_left, stack
from ui.panels import *
from ui.tab.copyright import copyright_tab
from ui.tab.language import language_tab
from ui.tab.login import login_tab
from ui.tab.popups import ok_cancel_popup
from ui.tab.register import register_tab
from ui.tab.settings import settings_tab
from ui.tab.shared import *
from ui.tabs import *
from ui.themes import *

LOGO = (
    "  ______ _                    _             ",
    " / _____) |          _   _   (_)            ",
    "| /     | | _   ____| |_| |_  _ ____   ____ ",
    "| |     | || \ / _  |  _)  _)| |  _ \ / _  |",
    "| \_____| | | ( ( | | |_| |__| | | | ( ( | |",
    " \______)_| |_|\_||_|\___)___)_|_| |_|\_|| |",
    "                                     (_____|",
)


def _get_theme_tube(): return tube


def _get_theme_chaos_tube(): return chaos_tube


class main_menu_tab(tab):

    def __init__(self, client: iclient, tablist: tablist):
        super().__init__(client, tablist)
        self._title_texts = []
        main = stack()

        class _db_alignments:
            def __getitem__(self, item: int):
                if item == 7:
                    return DRight
                else:
                    return DCenter

        db_alignments = _db_alignments()
        main_button_width = 14
        secondary_button_width = 14

        db = display_board(MCGT(lambda: self._title_texts), lambda: db_alignments, theme=_get_theme_tube)
        self.db = db
        main.add(db)
        self.main = main
        self.main.on_content_changed.add(lambda _: self.on_content_changed(self))
        db.width = 60
        db.height = auto

        def start():
            tab = self.win.new_chat_tab()
            tablist.replace(self, tab)

        b_start = i18n_button("controls.start", start)
        main.add(b_start)
        b_start.width = main_button_width

        def login():
            tab = self.win.newtab(login_tab)
            tablist.replace(self, tab)

        b_login = i18n_button("controls.login", login)
        main.add(b_login)
        b_login.width = main_button_width

        def register():
            tab = self.win.newtab(register_tab)
            tablist.replace(self, tab)

        b_register = i18n_button("controls.register", register)
        main.add(b_register)
        b_register.width = main_button_width
        self._on_quited = False

        def quit_app():
            self._on_quited = True

        b_quit = i18n_button("controls.quit", quit_app)
        main.add(b_quit)
        b_quit.width = main_button_width

        def show_info():
            tab = self.win.newtab(copyright_tab)
            tablist.replace(self, tab)

        b_info = i18n_button("controls.info", show_info)
        b_info.prop(panel.No_Left_Margin, True).prop(stack.Horizontal_Alignment, align_left)
        b_info.width = secondary_button_width
        main.add(b_info)

        def language():
            tab = self.win.newtab(language_tab)
            tablist.replace(self, tab)

        b_language = i18n_button("controls.language", language)
        b_language.prop(panel.No_Left_Margin, True).prop(stack.Horizontal_Alignment, align_left)
        b_language.width = secondary_button_width
        main.add(b_language)

        def settings():
            tab = self.win.newtab(settings_tab)
            tablist.replace(self, tab)

        b_settings = i18n_button("controls.settings", settings)
        b_settings.prop(panel.No_Left_Margin, True).prop(stack.Horizontal_Alignment, align_left)
        b_settings.width = secondary_button_width
        main.add(b_settings)

        main.left_margin = 10
        main.switch_to_first_or_default_item()

    def paint_on(self, buf: buffer):
        self.main.paint_on(buf)

    @property
    def title(self) -> str:
        return i18n.trans("tabs.main_menu_tab.name")

    def gen_title_texts(self):
        l: List[str] = list(LOGO)
        l.append(i18n.trans('info.software.author'))
        self._title_texts = l

    def on_added(self):
        self.gen_title_texts()
        self.main.reload()

    def reload(self):
        self.gen_title_texts()
        self.main.reload()

    def on_input(self, char: chars.char) -> Generator:
        consumed = self.main.on_input(char)
        if not consumed:
            if keys.k_down == char or keys.k_enter == char or chars.c_tab_key == char:
                self.main.switch_to_first_or_default_item()
            else:
                consumed = not common_hotkey(char, self, self.client, self.tablist, self.win)
        if self._on_quited:
            p = self.new_popup(ok_cancel_popup)
            p.words = split_textblock_words("tabs.main_menu_tab.quit_tip")
            p.title_getter = lambda: i18n.trans("controls.warning")
            self.win.popup(p)
            yield Suspend
            v = self.win.retrieve_popup(p)
            if v is True:
                self.client.stop()
            self._on_quited = False

    def on_replaced(self, last_tab: "tab") -> Need_Release_Resource:
        self.main.switch_to_first_or_default_item()
        return True

    def on_focused(self):
        configs = entity()

        if configs.ColorfulMainMenu:
            self.db.theme = _get_theme_chaos_tube
            self.db.on_render_char = colorize_char
        else:
            self.db.theme = _get_theme_tube
            self.db.on_render_char = None
