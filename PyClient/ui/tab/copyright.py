import keys
from ui.cmd_modes import common_hotkey
from ui.control.display_boards import display_board
from ui.panel.Stacks import Stack
from ui.tab.shared import *
from ui.tabs import *
from ui.themes import *

"""
Copyright 2021 Liplum
Software: ChattingRoom PyClient
Author: Liplum
Email: Li_plum@outlook.com

Permission is hereby granted, free of charge, to any person obtaining a copy of this software (ChattingRoom PyClient) 
and associated documentation files (only in "PyClient" folder), to deal in the Software without restriction, 
including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and to permit 
persons to whom the Software is furnished to do so, subject to the following conditions: 

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


def _key(key: str) -> str:
    return i18n.trans(f"tabs.copyright_tab.keys.{key}")


def _value(key: str) -> str:
    return i18n.trans(f"info.copyright.{key}")


class copyright_tab(Tab):

    def __init__(self, client: IClient, tablist: Tablist):
        super().__init__(client, tablist)
        self._copyright_texts: List[str] = []
        self.gen_copyright_texts()
        self.last_tab = None
        main = Stack()
        self.main = main
        db = display_board(MCGT(lambda: self._copyright_texts), theme=rounded_rectangle)
        db.width = 40
        main.add(db)

        def quit_tab():
            if self.last_tab:
                tablist.replace(self, self.last_tab)
            else:
                tablist.remove(self)

        b = i18n_button("controls.ok", quit_tab)
        b.margin = 3
        main.add(b)

        main.left_margin = 12

        main.switch_to_first_or_default_item()

    def paint_on(self, buf: buffer):
        self.main.paint_on(buf)

    @property
    def title(self) -> str:
        return i18n.trans("tabs.copyright_tab.name")

    def gen_copyright_texts(self):
        l: List[str] = [
            f"{_key('software_name')}: {_value('software')}",
            f"{_key('author')}: {_value('author')}",
            f"{_key('year')}: {_value('year')}",
            f"{_key('email')}: {_value('email')}"
        ]
        self._copyright_texts = l

    def reload(self):
        self.gen_copyright_texts()

    def on_input(self, char: chars.char) -> Generator:
        consumed = self.main.on_input(char)
        if not consumed:
            if keys.k_down == char or keys.k_enter == char or chars.c_tab_key == char:
                self.main.switch_to_first_or_default_item()
                yield Finished
            else:
                consumed = not common_hotkey(char, self, self.client, self.tablist, self.App)
                yield Finished
        else:
            yield Finished

    def on_replaced(self, last_tab: "Tab") -> Need_Release_Resource:
        self.last_tab = last_tab
        return False

    @classmethod
    def deserialize(cls, data: dict, client: IClient, tablist: Tablist) -> "Tab":
        return copyright_tab(client, tablist)

    @classmethod
    def serialize(cls, self: "Tab") -> dict:
        return {}

    @classmethod
    def serializable(cls) -> bool:
        return True
