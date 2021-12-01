from states import *
from ui.control.textboxes import textbox
from ui.core import iclient
from ui.shared import *
from ui.tabs import tablist


class ui_smachine(smachine,painter, inputable):

    def paint_on(self, buf: buffer):
        if self.cur is not None:
            self.cur.paint_on(buf)

    def on_input(self, char: chars.char) -> Is_Consumed:
        if self.cur is not None:
            return self.cur.on_input(char)
        return Not_Consumed


class ui_state(state, painter, inputable):
    textbox: textbox
    client: iclient
    tablist: tablist
    sm: ui_smachine

    def __init__(self):
        super().__init__()

    def paint_on(self, buf: buffer):
        pass

    def on_input(self, char: chars.char) -> Is_Consumed:
        return Not_Consumed
