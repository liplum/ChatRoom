from typing import Dict, List, Callable

from autofill import prompt


class command:
    def __init__(self, name: str, handler: Callable = None):
        self.name = name
        self.handler = handler

    def match(self, text) -> bool:
        return text == self.name

    def execute(self, context, args: [str]):
        if self.handler:
            self.handler(context, args)


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

    def execute(self, context, cmd_name: str, args: [str]):
        """

        :param cmd_name:
        :param context: some background info
        :param args:
        :exception CmdError:the base exception
        :exception WrongUsageError: raise when the para user inputted is wrong
        :exception CmdNotFound: raise when the given cmd name is not in command list
        :return:
        """
        if cmd_name in self.map:
            cmd = self.map[cmd_name]
            if cmd.match(cmd_name):
                cmd.execute(context, args)
            else:
                raise CmdNotFound(cmd_name)
        else:
            raise CmdNotFound(cmd_name)

    def apply_name(self, cmd_name: str):
        if cmd_name in self.map:
            self.autofill.apply(cmd_name)


class CmdError(BaseException):

    def __init__(self, msg_key: str, args=None):
        super().__init__()
        if args is None:
            args = []
        self.msg_key = msg_key
        self.args = args


class WrongUsageError(CmdError):

    def __init__(self, msg_key: str, pos: int, args=None):
        super().__init__(msg_key, args)
        self.position = pos


class CmdNotFound(Exception):
    def __init__(self, cmd_name: str):
        super().__init__()
        self.cmd_name = cmd_name
