import i18n
from ui.controls import *
from ui.ctrl import *

T = TypeVar('T')
CTRL = TypeVar('CTRL', bound=control)


def i18n_label(i18n_key: str, *args, **kwargs) -> label:
    return label(CGT(lambda: i18n.trans(i18n_key, *args, **kwargs)))


def i18n_button(i18n_key: str, on_press: Callable[[], NoReturn], *args, **kwargs) -> button:
    return button(CGT(lambda: i18n.trans(i18n_key, *args, **kwargs)), on_press)
