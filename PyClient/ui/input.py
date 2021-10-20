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
