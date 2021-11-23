from chars import printable
from keys import *
from ui.inputs import iinput

cmd_input_map = {
    "#n": k_enter,
    "#q": k_quit,
    "#l": k_left,
    "#r": k_right,
    "#u": k_up,
    "#d": k_down,
    "#b": k_backspace,
    "#h": k_home,
    "#e": k_end,
}


class cmd_input(iinput):
    """
    If the on_input event is canceled, it'll abandon all remaining chars in input list
    """

    def __init__(self):
        super().__init__()

    def get_input(self, tip: str = None):
        if tip is None:
            res = input()
        else:
            res = input(str)
        if res.lower() in cmd_input_map:
            ch = cmd_input_map[res]
            self._input_list.append(ch)
            self.on_input(self, ch)
            return

        for ch in res:
            ch = printable(ch)
            self._input_list.append(ch)
            canceled = self.on_input(self, ch)
            if canceled:
                return
