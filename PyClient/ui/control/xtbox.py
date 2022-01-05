from typing import Set

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
    lastOperatedStr = ""
    lastOperatedIndex = 0
    lastOperatedType = 0  # 0 is empty,1 for append,2 for delete

    def OnAppend(tb, i, c):
        nonlocal lastOperatedStr, lastOperatedType, lastOperatedIndex
        lastOperatedStr = c
        lastOperatedIndex = i
        lastOperatedType = 1

    def OnDelete(tb, i, c):
        nonlocal lastOperatedStr, lastOperatedType, lastOperatedIndex
        lastOperatedStr = c
        lastOperatedIndex = i
        lastOperatedType = 2

    def Undo():
        nonlocal lastOperatedType
        if lastOperatedType == 2:
            textArea.InputListRaw.insert(lastOperatedIndex, lastOperatedStr)
        elif lastOperatedType == 1:
            del textArea.InputListRaw[lastOperatedIndex]

        lastOperatedType = 0

    textArea.OnAppend.Add(OnAppend)
    textArea.OnDelete.Add(OnDelete)
    kbs = kbinding()
    kbs.bind(keys.k_backspace, lambda c: textArea.Delete())
    kbs.bind(keys.k_delete, lambda c: textArea.Delete(left=False))
    kbs.bind(keys.k_left, lambda c: textArea.Left())
    kbs.bind(keys.k_right, lambda c: textArea.Right())
    kbs.bind(keys.k_home, lambda c: textArea.Home())
    kbs.bind(keys.k_end, lambda c: textArea.End())
    # kbs.bind(keys.ctrl_x, lambda c: Undo())
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
