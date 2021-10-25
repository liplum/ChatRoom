from typing import Union, Optional, Tuple

control_keycode_1 = 0xe0
f_keycode_1 = 0


class char:
    def __init__(self, keycode_1: int, keycode_2: Optional[int] = None):
        self.keycode_1: int = keycode_1
        self.keycode_2: Optional[int] = keycode_2

    def __eq__(self, other: Union["char", str, bytes, int, Tuple[int, int]]):
        if isinstance(other, char):
            if self.keycode_1 == other.keycode_1:
                if self.keycode_2 is not None and other.keycode_2 is not None:
                    return self.keycode_2 == other.keycode_2
                return True
        elif isinstance(other, str):
            keycode = ord(other)
            return self.keycode_1 == keycode
        elif isinstance(other, bytes):
            real_char = other.decode()
            return self.keycode_1 == ord(real_char)
        elif isinstance(other, int):
            return self.keycode_1 == other
        elif isinstance(other, tuple):
            other_len = len(other)
            if other_len == 1 and self.keycode_2 is None:
                return self.keycode_1 == other[0]
            elif other_len > 1 and self.keycode_2 is not None:
                return self.keycode_1 == other[0] and self.keycode_2 == other[1]
        return False

    def __repr__(self):
        return f'({self.keycode_1},{self.keycode_2})->"{to_str(self)}"'

    def __str__(self):
        return to_str(self)

    def __hash__(self):
        return hash((self.keycode_1, self.keycode_2))


class printable(char):
    def __init__(self, char_: Union[str, bytes]):
        if isinstance(char_, bytes):
            self.char = char_.decode()
        else:
            self.char = char_
        super().__init__(ord(self.char))


class control(char):
    def __init__(self, keycode_2: int):
        super().__init__(control_keycode_1, keycode_2)


class f(char):
    def __init__(self, keycode_2: int):
        super().__init__(f_keycode_1, keycode_2)


def is_key(char: Union[str, bytes, bytearray], key: Union[str, bytes]):
    if isinstance(char, str):
        b = char.encode()
    elif isinstance(char, bytes):
        b = char
    elif isinstance(char, bytearray):
        b = bytes(bytearray)
    else:
        return False

    if isinstance(key, bytes):
        k = key
    elif isinstance(key, str):
        k = key.encode()
    else:
        return False
    return b == k


def is_printable(ch: char) -> bool:
    if isinstance(ch, printable):
        return True
    if isinstance(ch, control) or isinstance(ch, f):
        return False
    if ch.keycode_2 is None and ch.keycode_1 != control_keycode_1 and ch.keycode_1 != f_keycode_1:
        return True
    return False


def to_str(ch: char) -> str:
    """
    Transfer a char object to a character
    :param ch:
    :return:
    """
    return chr(ch.keycode_1)


char_a = printable('a')
char_A = printable('A')

char_b = printable('b')
char_B = printable('B')

char_c = printable('c')
char_C = printable('C')

char_d = printable('d')
char_D = printable('D')

char_e = printable('e')
char_E = printable('E')

char_f = printable('f')
char_F = printable('F')

char_g = printable('g')
char_G = printable('G')

char_h = printable('h')
char_H = printable('H')

char_i = printable('i')
char_I = printable('I')

char_j = printable('j')
char_J = printable('J')

char_k = printable('k')
char_K = printable('K')

char_l = printable('l')
char_L = printable('L')

char_m = printable('m')
char_M = printable('M')

char_n = printable('n')
char_N = printable('N')

char_o = printable('o')
char_O = printable('O')

char_p = printable('p')
char_P = printable('P')

char_q = printable('q')
char_Q = printable('Q')

char_r = printable('r')
char_R = printable('R')

char_s = printable('s')
char_S = printable('S')

char_t = printable('t')
char_T = printable('T')

char_u = printable('u')
char_U = printable('U')

char_v = printable('v')
char_V = printable('V')

char_w = printable('w')
char_W = printable('W')

char_x = printable('x')
char_X = printable('X')

char_y = printable('y')
char_Y = printable('Y')

char_z = printable('z')
char_Z = printable('Z')

char_0 = printable('0')
char_1 = printable('1')
char_2 = printable('2')
char_3 = printable('3')
char_4 = printable('4')
char_5 = printable('5')
char_6 = printable('6')
char_7 = printable('7')
char_8 = printable('8')
char_9 = printable('9')

char_space = printable(' ')
char_exclamation_mark = printable('!')
char_quotation_mark = printable('"')
char_number_sign = printable('#')
char_colon = printable(':')
char_semicolon = printable(';')
char_less_than = printable('<')
char_grave_accent = printable('`')
char_tilde = printable('~')

char_null = char(0)
char_table = char(7)
char_backspace = char(8)
char_line_end = char(10)
char_vtable = char(11)
char_carriage_return = char(13)
char_esc = char(27)

char_home = control(71)
char_up = control(72)
char_pgup = control(73)
char_left = control(75)
char_right = control(77)
char_down = control(80)
char_pgdown = control(81)
char_insert = control(82)
char_delete = control(83)

char_f1 = f(59)
char_f2 = f(60)
char_f3 = f(61)
char_f4 = f(62)
char_f5 = f(63)
char_f6 = f(64)
char_f7 = f(65)
char_f8 = f(66)
char_f9 = f(67)
char_f10 = f(68)
char_f11 = control(133)
char_f12 = control(134)
