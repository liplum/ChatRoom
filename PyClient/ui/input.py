class i_input:
    def get_input(self, tip: str = None) -> str:
        pass


class cmd_input(i_input):

    def get_input(self, tip: str = None) -> str:
        if tip is None:
            res = input()
        else:
            res = input(str)
        return res
