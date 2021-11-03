from typing import Dict, List

from autofill import prompt


class command:
    def __init__(self, name: str, tip: str, handler):
        self.name = name
        self.tip = tip
        self.handler = handler

    def match(self, text) -> bool:
        return text == self.name

    def execute(self, args: List[str]):
        self.handler(args)


class cmdmanager:
    def __init__(self):
        self.autofill = prompt()
        # self.autofill.max_candidate = 10
        self.map: Dict[str, command] = {}

    def add(self, cmd: command):
        name = cmd.name
        self.autofill.add(name)
        self.map[name] = cmd

    def prompts(self, inputs: str) -> List[str]:
        return self.autofill.autofill(inputs)

    def execute(self, cmd_name: str, args: List[str]):
        """

        :param cmd_name:
        :param args:
        :exception CmdError:the base exception
        :exception WrongUsageError: raise when the para user inputted is wrong
        :exception CmdNotFound: raise when the given cmd name is not in command list
        :return:
        """
        if cmd_name in self.map:
            cmd = self.map[cmd_name]
            if cmd.match(cmd_name):
                cmd.execute(args)
            else:
                raise CmdNotFound(cmd_name)
        else:
            raise CmdNotFound(cmd_name)

    def apply_name(self, cmd_name: str):
        if cmd_name in self.map:
            self.autofill.apply(cmd_name)


class CmdError(BaseException):

    def __init__(self, msg: str) -> None:
        super().__init__()
        self.msg = msg


class WrongUsageError(CmdError):

    def __init__(self, msg: str, pos: int) -> None:
        super().__init__(msg)
        self.position = pos


class CmdNotFound(CmdError):
    def __init__(self, cmd_name: str) -> None:
        super().__init__(f'Not found "{cmd_name}" command.')
