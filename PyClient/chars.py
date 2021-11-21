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

    def is_printable(self) -> bool:
        if self.keycode_2 is None and self.keycode_1 != control_keycode_1 and self.keycode_1 != f_keycode_1:
            return True
        return False


class printable(char):
    def __init__(self, char_: Union[str, bytes]):
        if isinstance(char_, bytes):
            self.char = char_.decode()
        else:
            self.char = char_
        super().__init__(ord(self.char))

    def is_printable(self) -> bool:
        return True


class control(char):
    def __init__(self, keycode_2: int):
        super().__init__(control_keycode_1, keycode_2)

    def is_printable(self) -> bool:
        return False


class f(char):
    def __init__(self, keycode_2: int):
        super().__init__(f_keycode_1, keycode_2)

    def is_printable(self) -> bool:
        return False


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


def to_str(ch: char) -> str:
    """
    Transfer a char object to a character
    :param ch:
    :return:
    """
    return chr(ch.keycode_1)


c_a = printable('a')
c_A = printable('A')

c_b = printable('b')
c_B = printable('B')

c_c = printable('c')
c_C = printable('C')

c_d = printable('d')
c_D = printable('D')

c_e = printable('e')
c_E = printable('E')

c_f = printable('f')
c_F = printable('F')

c_g = printable('g')
c_G = printable('G')

c_h = printable('h')
c_H = printable('H')

c_i = printable('i')
c_I = printable('I')

c_j = printable('j')
c_J = printable('J')

c_k = printable('k')
c_K = printable('K')

c_l = printable('l')
c_L = printable('L')

c_m = printable('m')
c_M = printable('M')

c_n = printable('n')
c_N = printable('N')

c_o = printable('o')
c_O = printable('O')

c_p = printable('p')
c_P = printable('P')

c_q = printable('q')
c_Q = printable('Q')

c_r = printable('r')
c_R = printable('R')

c_s = printable('s')
c_S = printable('S')

c_t = printable('t')
c_T = printable('T')

c_u = printable('u')
c_U = printable('U')

c_v = printable('v')
c_V = printable('V')

c_w = printable('w')
c_W = printable('W')

c_x = printable('x')
c_X = printable('X')

c_y = printable('y')
c_Y = printable('Y')

c_z = printable('z')
c_Z = printable('Z')

c_0 = printable('0')
c_1 = printable('1')
c_2 = printable('2')
c_3 = printable('3')
c_4 = printable('4')
c_5 = printable('5')
c_6 = printable('6')
c_7 = printable('7')
c_8 = printable('8')
c_9 = printable('9')

c_space = printable(' ')
c_exclamation_mark = printable('!')
c_quotation_mark = printable('"')
c_number_sign = printable('#')
c_colon = printable(':')
c_semicolon = printable(';')
c_less_than = printable('<')
c_grave_accent = printable('`')
c_tilde = printable('~')

c_null = char(0)
c_table = char(7)  # carriage_return \r

c_backspace = char(8)
c_tab_key = char(9)  # \t
c_line_end = char(10)
c_vtable = char(11)
c_carriage_return = char(13)  # aka Vertical Tab \r\n
c_esc = char(27)
c_delete127 = char(127)

c_home = control(71)
c_up = control(72)
c_pgup = control(73)
c_left = control(75)
c_right = control(77)
c_end = control(79)
c_down = control(80)
c_pgdown = control(81)
c_insert = control(82)
c_delete = control(83)

c_f1 = f(59)
c_f2 = f(60)
c_f3 = f(61)
c_f4 = f(62)
c_f5 = f(63)
c_f6 = f(64)
c_f7 = f(65)
c_f8 = f(66)
c_f9 = f(67)
c_f10 = f(68)
c_f11 = control(133)
c_f12 = control(134)
