from typing import Optional, Set, Iterable

import keys
from ui.control.TextAreas import TextArea
from ui.control.textboxes import textbox
from ui.k import kbinding
from ui.shared import *


def XtextWrapper(textArea: TextArea,
                 exceptedChars: Optional[Set[chars.char]] = None,
                 onlyAllowedChars: Optional[Set[chars.char]] = None) -> TextArea:
    def onExitFocusHandler(_):
        textArea.OnExitFocus(textArea)
        return True

    if exceptedChars and onlyAllowedChars:
        onlyAllowedChars = onlyAllowedChars - exceptedChars
    kbs = kbinding()
    kbs.bind(keys.k_backspace, lambda c: textArea.Delete())
    kbs.bind(keys.k_delete, lambda c: textArea.Delete(left=False))
    kbs.bind(keys.k_left, lambda c: textArea.Left())
    kbs.bind(keys.k_right, lambda c: textArea.Right())
    kbs.bind(keys.k_home, lambda c: textArea.Home())
    kbs.bind(keys.k_end, lambda c: textArea.End())
    kbs.bind(chars.c_esc, onExitFocusHandler)
    spapp = textArea.Append
    if onlyAllowedChars is not None:
        kbs.on_any = lambda c: spapp(
            chars.to_str(c)) if c.is_printable() and c in onlyAllowedChars else False
    elif exceptedChars is not None:
        kbs.on_any = lambda c: spapp(
            chars.to_str(c)) if c.is_printable() and c not in exceptedChars else False
    else:
        kbs.on_any = lambda c: spapp(chars.to_str(c)) if c.is_printable() else False

    def OnInputDelegate(ch: chars.char) -> IsConsumed:
        return kbs.trigger(ch)

    textArea.on_input = OnInputDelegate
    return textArea


def xtextbox(cursorIcon: str = "^", init: Optional[Iterable[str]] = None,
             exceptedChars: Optional[Set[chars.char]] = None,
             onlyAllowedChars: Optional[Set[chars.char]] = None):
    return XtextWrapper(textbox(cursorIcon, init), exceptedChars, onlyAllowedChars)


Xtextbox = xtextbox
