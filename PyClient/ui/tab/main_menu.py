from ui.control.display_boards import display_board
from ui.panels import *
from ui.tab.login import login_tab
from ui.tab.shared import *
from ui.tabs import *
from ui.themes import *


class main_menu_tab(tab):

    def __init__(self, client: iclient, tablist: tablist):
        super().__init__(client, tablist)
        self._title_texts = []
        self.gen_title_texts()
        main = stack()
        db = display_board(MCGT(lambda: self._title_texts), theme=tube)
        main.add(db)
        self.main = main
        self.main.on_content_changed.add(lambda _: self.on_content_changed(self))
        db.width = 40
        db.height = auto
        self.win = self.client.win

        def login():
            tab = self.win.newtab(login_tab)
            tablist.replace(self, tab)

        b_login = i18n_button("controls.login", login)
        main.add(b_login)
        b_login.width = 8

        def quit_app():
            client.stop()

        b_quit = i18n_button("controls.quit", quit_app)
        main.add(b_quit)
        b_quit.width = 8

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
            i18n.trans('info.copyright.author')
        ]
        self._title_texts = l

    def reload(self):
        self.gen_title_texts()

    def on_input(self, char: chars.char) -> Is_Consumed:
        consumed = self.main.on_input(char)
        if not consumed:
            if keys.k_down == char or keys.k_enter == char or chars.c_tab_key == char:
                self.main.switch_to_first_or_default_item()
                return Consumed
        return Not_Consumed
