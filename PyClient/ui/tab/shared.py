import random

import ui.themes as themes
from ui.control.buttons import button
from ui.control.labels import label
from ui.ctrl import *
from ui.outputs import *

T = TypeVar('T')
CTRL = TypeVar('CTRL', bound=control)


def i18n_label(i18n_key: str, *i18n_args, **i18n_kwargs) -> label:
    return label(CGT(lambda: i18n.trans(i18n_key, *i18n_args, **i18n_kwargs)))


def i18n_button(i18n_key: str, on_press: Callable[[], NoReturn], *i18n_args, **i18n_kwargs) -> button:
    return button(CGT(lambda: i18n.trans(i18n_key, *i18n_args, **i18n_kwargs)), on_press)


number_keys = frozenset(
    {chars.c_0, chars.c_1, chars.c_2, chars.c_3, chars.c_4, chars.c_5, chars.c_6, chars.c_7, chars.c_8, chars.c_9})

alphabet_keys = frozenset({
    chars.c_a, chars.c_A, chars.c_b, chars.c_B, chars.c_c, chars.c_C, chars.c_d, chars.c_D, chars.c_e, chars.c_E,
    chars.c_f, chars.c_F, chars.c_g, chars.c_G, chars.c_h, chars.c_H, chars.c_i, chars.c_I, chars.c_j, chars.c_J,
    chars.c_k, chars.c_K, chars.c_l, chars.c_L, chars.c_m, chars.c_M, chars.c_n, chars.c_N, chars.c_o, chars.c_O,
    chars.c_p, chars.c_P, chars.c_q, chars.c_Q, chars.c_r, chars.c_R, chars.c_s, chars.c_S, chars.c_t, chars.c_T,
    chars.c_u, chars.c_U, chars.c_v, chars.c_V, chars.c_w, chars.c_W, chars.c_x, chars.c_X, chars.c_y, chars.c_Y,
    chars.c_z, chars.c_Z
})

number_alphabet_keys = number_keys | alphabet_keys


class i18n_theme(themes.check_theme):
    def __init__(self, checked_key: str, unchecked_key: str, null_key: str):
        super().__init__(checked_key, unchecked_key, null_key)

    @property
    def checked(self):
        return i18n.trans(self._checked)

    @property
    def unchecked(self):
        return i18n.trans(self._unchecked)

    @property
    def null(self):
        return i18n.trans(self._null)


turn_on_off_check_theme = i18n_theme(
    "controls.checkbox.turn_on", "controls.checkbox.turn_off", "controls.checkbox.null"
)

_word_separator_key = "controls.textblock.word_separator"


def split_textblock_words(key: str,*args,**kwargs) -> List[str]:
    word_separator = i18n.trans(_word_separator_key)
    if word_separator == _word_separator_key:
        word_separator = ""
    text = i18n.trans(key,*args,**kwargs)
    if word_separator == "":
        return [text]
    else:
        try:
            return text.split(word_separator)
        except:
            return [text]


def tinted_theme(theme: themes.theme) -> themes.theme:
    t = theme.copy()
    t.left_top = tintedtxt(t.left_top, fgcolor=CmdFgColor.Blue)
    t.right_top = tintedtxt(t.right_top, fgcolor=CmdFgColor.Blue)
    t.left_bottom = tintedtxt(t.left_bottom, fgcolor=CmdFgColor.Blue)
    t.right_bottom = tintedtxt(t.right_bottom, fgcolor=CmdFgColor.Blue)
    t.horizontal = tintedtxt(t.horizontal, fgcolor=CmdFgColor.Red)
    t.vertical = tintedtxt(t.vertical, fgcolor=CmdFgColor.Green)
    return t


colorful_rounded_rectangle = tinted_theme(themes.rounded_rectangle)
colorful_tube = tinted_theme(themes.tube)


def random_fgcolor() -> CmdFgColorEnum:
    return random.choice(CmdFgColorsWithoutBlack)


def random_bkcolor() -> CmdBkColorEnum:
    return random.choice(CmdBkColorsWithoutBlack)


def random_style() -> CmdStyleEnum:
    return random.choice(CmdStyles)


class chaos_theme(themes.packed_theme):

    @property
    def left_top(self) -> str:
        return tintedtxt(self._left_top, fgcolor=random_fgcolor())

    @property
    def right_top(self) -> str:
        return tintedtxt(self._right_top, fgcolor=random_fgcolor())

    @property
    def left_bottom(self) -> str:
        return tintedtxt(self._left_bottom, fgcolor=random_fgcolor())

    @property
    def right_bottom(self) -> str:
        return tintedtxt(self._right_bottom, fgcolor=random_fgcolor())

    @property
    def horizontal(self) -> str:
        return tintedtxt(self._horizontal, fgcolor=random_fgcolor())

    @property
    def vertical(self) -> str:
        return tintedtxt(self._vertical, fgcolor=random_fgcolor())


chaos_tube = themes.copy_packed_theme(themes.tube, chaos_theme)


def colorize(text: str) -> str:
    with StringIO() as s:
        for char in text:
            tintedtxtIO(s, char, fgcolor=random_fgcolor())
        return s.getvalue()


def colorize_char(text: str) -> str:
    return tintedtxt(text, fgcolor=random_fgcolor())
