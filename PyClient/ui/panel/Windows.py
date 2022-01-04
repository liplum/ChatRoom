from ui.Controls import *


class Window(Control):
    @property
    def focusable(self) -> bool:
        return True
