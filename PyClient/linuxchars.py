from chars import char
from typing import Union, Optional,Tuple

linux_esc = 0x1b
linux_csi = ord('[')
linux_o = 79
linux_126 = 126


class linux_control(char):

    def __init__(self, keycode_2: int, keycode_3: int, keycode_4: Optional[int], keycode_5: Optional[int]):
        super().__init__(linux_esc, keycode_2)
        self.keycode_3 = keycode_3
        self.keycode_4 = keycode_4
        self.keycode_5 = keycode_5

    def __eq__(self, other: Union[char, "linux_control", bytes, int, Tuple[int, int], Tuple[int, int, int, int]]):
        if super().__eq__(other):
            if isinstance(other, linux_control):
                return self.keycode_3 == other.keycode_3 and self.keycode_4 == other.keycode_4 and \
                       self.keycode_5 == other.keycode_5
            elif isinstance(other, tuple):
                if len(other) >= 4:
                    return self.keycode_3 == other[2] and self.keycode_4 == other[3] and \
                           self.keycode_5 == other[4]
        return False

    def __repr__(self):
        return f'({self.keycode_1},{self.keycode_2},{self.keycode_3},{self.keycode_4})'

    def __hash__(self):
        return hash((self.keycode_1, self.keycode_2, self.keycode_3, self.keycode_4))


def csi_1(keycode_3: int) -> linux_control:
    return linux_control(linux_csi, keycode_3, None, None)


def csi_2(keycode_3: int, keycode_4: int) -> linux_control:
    return linux_control(linux_csi, keycode_3, keycode_4, None)


def csi_2_end126(keycode_3: int) -> linux_control:
    return linux_control(linux_csi, keycode_3, linux_126, None)


def csi_3_end126(keycode_3: int, keycode_4: int):
    return linux_control(linux_csi, keycode_3, keycode_4, linux_126)


def o_1(keycode_3: int) -> linux_control:
    return linux_control(linux_o, keycode_3, None, None)


def from_tuple(li: Union[list, tuple]) -> linux_control:
    l = len(li)
    k2 = li[1]
    k3 = li[2]
    k4 = li[3] if l > 3 else None
    k5 = li[4] if l > 4 else None
    return linux_control(k2, k3, k4, k5)


lc_up = csi_1(65)
lc_down = csi_1(66)
lc_right = csi_1(67)
lc_left = csi_1(68)

lc_pgdown = csi_2_end126(54)
lc_pgup = csi_2_end126(53)

lc_end = csi_1(70)
lc_home = csi_1(72)

lc_insert = csi_2_end126(50)
lc_delete = csi_2_end126(51)

lc_f1 = o_1(80)
lc_f2 = o_1(81)
lc_f3 = o_1(82)
lc_f4 = o_1(83)

lc_f5 = csi_3_end126(49, 53)
lc_f6 = csi_3_end126(49, 55)
lc_f7 = csi_3_end126(49, 56)
lc_f8 = csi_3_end126(49, 57)

lc_f9 = csi_3_end126(50, 48)
lc_f10 = csi_3_end126(50, 49)

lc_f12 = csi_3_end126(50, 52)
