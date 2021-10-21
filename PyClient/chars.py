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
            if other_len == 1:
                return self.keycode_1 == other[0]
            elif other_len > 1:
                return self.keycode_1 == other[0] and self.keycode_2 == other[1]
        return False


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


class _char:
    def __init__(self, name: Optional[str] = None, name_b: Optional[bytes] = None, id_1: Optional[int] = None,
                 id_2: Optional[int] = None,
                 is_control: bool = False,
                 is_F: bool = False):
        if name is None and name_b is None and id_1 is None:
            raise Exception("Completely None Char")
        self.name: Optional[str] = name
        if name is not None and name_b is None:
            self.name_b: Optional[bytes] = name.encode()
        else:
            self.name_b = name_b
        if id_1 is None:
            if name is not None:
                self.id_1: Optional[int] = ord(name)
        else:
            self.id_1 = id_1
        self.id_2: Optional[int] = id_2
        self.is_control: bool = is_control
        self.is_F: bool = is_F

    def __eq__(self, other):
        if not isinstance(other, char):
            return False
        if self.name is not None and other.name is not None:
            return self.name == other.name
        elif self.name_b is not None and other.name_b is not None:
            return self.name_b == other.name_b
        elif self.id_1 is not None and other.id_1 is not None:
            if self.id_2 is not None and other.id_2 is not None:
                return self.id_1 == other.id_1 and self.id_2 == other.id_2
            else:
                return self.id_1 == other.id_1
        return False


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

char_esc = char(27)
char_delete = char(127)
char_line_end = char(10)

char_up = control(0x48)
char_down = control(0x50)
char_left = control(0x4B)
char_right = control(0x4D)
