from typing import NoReturn

import i18n
from ui.control.buttons import button
from ui.control.labels import label
from ui.ctrl import *

T = TypeVar('T')
CTRL = TypeVar('CTRL', bound=control)


def i18n_label(i18n_key: str, *args, **kwargs) -> label:
    return label(CGT(lambda: i18n.trans(i18n_key, *args, **kwargs)))


def i18n_button(i18n_key: str, on_press: Callable[[], NoReturn], *args, **kwargs) -> button:
    return button(CGT(lambda: i18n.trans(i18n_key, *args, **kwargs)), on_press)


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
