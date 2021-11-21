from typing import Optional, Set, Union

import chars
import keys
from ui.controls import textbox
from ui.k import kbinding


class xtextbox(textbox):
    def __init__(self, cursor_icon: str = '^', excepted_chars: Optional[Set[chars.char]] = None):
        super().__init__(cursor_icon)
        if excepted_chars is None:
            excepted_chars = set()
        self._excepted_chars = excepted_chars
        kbs = kbinding()
        self.kbs = kbs
        kbs.bind(keys.k_backspace, lambda c: self.delete())
        kbs.bind(keys.k_delete, lambda c: self.delete(left=False))
        kbs.bind(keys.k_left, lambda c: self.left())
        kbs.bind(keys.k_right, lambda c: self.right())
        kbs.bind(keys.k_home, lambda c: self.home())
        kbs.bind(keys.k_end, lambda c: self.end())

        def on_exit_focus(c):
            self.on_exit_focus(self)
            return True

        kbs.bind(chars.c_esc, on_exit_focus)
        spapp = super().append
        kbs.on_any = lambda c: spapp(chars.to_str(c)) if c.is_printable() and c not in self.excepted_chars else False

    def append(self, ch: Union[str, chars.char]) -> bool:
        if isinstance(ch, str):
            return super().append(ch)
        elif isinstance(ch, chars.char):
            consumed = self.kbs.trigger(ch)
            return consumed
        return False

    @property
    def excepted_chars(self) -> Set[chars.char]:
        return self._excepted_chars


def _return_false(_):
    return False
