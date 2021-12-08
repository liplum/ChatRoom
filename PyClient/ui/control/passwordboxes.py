from typing import Optional, Iterable, Set

import chars
import utils
from ui.control.xtbox import xtextbox
from ui.themes import password_theme

spot = password_theme("⦁")
asterisk = password_theme("*")


class passwordbox(xtextbox):
    def __init__(self, cursor_icon: str = '^', theme: password_theme = asterisk,
                 init: Optional[Iterable[str]] = None,
                 excepted_chars: Optional[Set[chars.char]] = None,
                 only_allowed_chars: Optional[Set[chars.char]] = None):
        super().__init__(cursor_icon, init, excepted_chars, only_allowed_chars)
        self.pwd_theme = theme

    @property
    def render_input_list(self) -> Iterable[str]:
        return utils.repeat(self.pwd_theme.hidden, self.input_count)
