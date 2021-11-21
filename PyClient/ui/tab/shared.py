from typing import TypeVar

import i18n
from ui.controls import label
from ui.ctrl import control, CGT

T = TypeVar('T')
CTRL = TypeVar('CTRL', bound=control)


def i18n_label(i18n_key: str, *args, **kwargs):
    return label(CGT(lambda: i18n.trans(i18n_key, *args, **kwargs)))
