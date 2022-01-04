from states import *
from ui.control.textboxes import textbox
from ui.Core import IClient
from ui.shared import *
from ui.tabs import tablist


class ui_smachine(smachine, painter, inputable):

    def paint_on(self, buf: buffer):
        if self.cur is not None:
            self.cur.paint_on(buf)

    def on_input(self, char: chars.char) -> IsConsumed:
        if self.cur is not None:
            return self.cur.on_input(char)
        return NotConsumed


class ui_state(state, painter, inputable):
    textbox: textbox
    client: IClient
    tablist: tablist
    sm: ui_smachine

    def __init__(self):
        super().__init__()

    def paint_on(self, buf: buffer):
        pass

    def on_input(self, char: chars.char) -> IsConsumed:
        return NotConsumed
