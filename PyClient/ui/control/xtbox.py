from typing import Optional, Set, Iterable

import keys
from ui.control.textboxes import textbox
from ui.k import kbinding
from ui.shared import *


class xtextbox(textbox):
    def __init__(self, cursor_icon: str = '^', init: Optional[Iterable[str]] = None,
                 excepted_chars: Optional[Set[chars.char]] = None,
                 only_allowed_chars: Optional[Set[chars.char]] = None):
        super().__init__(cursor_icon, init)
        self._excepted_chars: Optional[Set[chars.char]] = excepted_chars
        if excepted_chars and only_allowed_chars:
            self._only_allowed_chars = only_allowed_chars - excepted_chars
        else:
            self._only_allowed_chars = only_allowed_chars
        kbs = kbinding()
        self.kbs = kbs
        kbs.bind(keys.k_backspace, lambda c: self.delete())
        kbs.bind(keys.k_delete, lambda c: self.delete(left=False))
        kbs.bind(keys.k_left, lambda c: self.left())
        kbs.bind(keys.k_right, lambda c: self.right())
        kbs.bind(keys.k_home, lambda c: self.home())
        kbs.bind(keys.k_end, lambda c: self.end())

        def on_exit_focus(_):
            self.on_exit_focus(self)
            return True

        kbs.bind(chars.c_esc, on_exit_focus)
        spapp = super().append
        if only_allowed_chars:
            kbs.on_any = lambda c: spapp(
                chars.to_str(c)) if c.is_printable() and c in self._only_allowed_chars else False
        elif excepted_chars:
            kbs.on_any = lambda c: spapp(
                chars.to_str(c)) if c.is_printable() and c not in self._excepted_chars else False
        else:
            kbs.on_any = lambda c: spapp(chars.to_str(c)) if c.is_printable() else False

    def on_input(self, ch: chars.char) -> IsConsumed:
        return self.kbs.trigger(ch)