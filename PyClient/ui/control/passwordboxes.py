from typing import Optional, Iterable, Set

import chars
import utils
from ui.control.textboxes import TextBox
from ui.control.xtbox import Xtextbox
from ui.themes import password_theme

spot = password_theme("⦁")
asterisk = password_theme("*")


def passwordbox(cursorIcon: str = '^', init: Optional[Iterable[str]] = None, theme: password_theme = asterisk,
                exceptedChars: Optional[Set[chars.char]] = None,
                onlyAllowedChars: Optional[Set[chars.char]] = None) -> TextBox:
    tbox = Xtextbox(cursorIcon, init, exceptedChars, onlyAllowedChars)

    def getRenderInputListDelegate() -> Iterable[str]:
        return utils.repeat(theme.hidden, tbox.InputLength)

    tbox.getRenderInputList = getRenderInputListDelegate
    return tbox
