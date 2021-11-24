from ui.ctrl import *


class checkbox(control):

    def __init__(self):
        super().__init__()

    def paint_on(self, buf: buffer):
        pass

    @property
    def focusable(self) -> bool:
        return True

    def on_input(self, char: chars.char) -> Is_Consumed:
        return Not_Consumed
