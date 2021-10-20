from typing import Union, Optional


class char:
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
            elif name_b is not None:
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


char_a = char(name='!', )


class i_input:
    def __init__(self):
        self._input_list = []

    def get_input(self, tip: str = None):
        pass

    def get_input_list(self) -> list:
        return self._input_list[:]

    def flush(self):
        self._input_list = []


class i_nbinput(i_input):
    pass


class cmd_input(i_input):
    def __init__(self):
        super().__init__()

    def get_input(self, tip: str = None):
        if tip is None:
            res = input()
        else:
            res = input(str)
        self._input_list.append(res)
