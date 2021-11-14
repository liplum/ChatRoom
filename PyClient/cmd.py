from io import StringIO
from typing import Dict, List, Callable, Tuple

from autofill import prompt


class cmdbase:
    def match(self, text: str) -> bool:
        pass

    def execute(self, context, args: [str]):
        pass


class command(cmdbase):
    def __init__(self, name: str, handler: Callable = None):
        self.name = name
        self.handler = handler

    def match(self, text: str) -> bool:
        return text == self.name

    def execute(self, context, args: [str]):
        if self.handler:
            self.handler(context, args)


class cmdmanager:
    def __init__(self):
        self.autofill = prompt()
        # self.autofill.max_candidate = 10
        self.map: Dict[str, cmdbase] = {}

    def add(self, cmd: cmdbase):
        name = cmd.name
        self.autofill.add(name)
        self.map[name] = cmd

    def has(self, cmd_name: str) -> bool:
        return cmd_name in self.map

    def __iter__(self):
        return iter(self.map.items())

    def prompts(self, inputs: str) -> List[Tuple[str, str]]:
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


class CmdError(Exception):

    def __init__(self, msg: str):
        super().__init__()
        self.msg = msg


class WrongUsageError(CmdError):

    def __init__(self, msg: str, pos: int):
        super().__init__(msg)
        self.position = pos


class CmdNotFound(Exception):
    def __init__(self, cmd_name: str):
        super().__init__()
        self.cmd_name = cmd_name


def is_quoted(index: int, quoted_indexes: List[Tuple[int, str]]):
    for i, qtype in quoted_indexes:
        if index == i:
            return True
        elif index > i:
            return False
    return False


def compose_full_cmd(cmd_args: List[str], quoted_indexes: List[Tuple[int, str]]) -> str:
    argslen = len(cmd_args)
    if len(quoted_indexes) == 0:  # no quotation
        with StringIO() as s:
            for i, arg in enumerate(cmd_args):
                s.write(arg)
                if i < argslen - 1:
                    s.write(' ')
            return s.getvalue()
    else:  # has quotation
        cur_quoted_metaindexes = 0
        quoted_indexeslen = len(quoted_indexes)
        with StringIO() as s:
            for i, arg in enumerate(cmd_args):
                if cur_quoted_metaindexes < quoted_indexeslen:
                    index, qtype = quoted_indexes[cur_quoted_metaindexes]
                    if index == i:
                        s.write(qtype)
                        s.write(arg)
                        s.write(qtype)
                    else:
                        s.write(arg)
                if i < argslen - 1:
                    s.write(' ')
            return s.getvalue()


def analyze_cmd_args(full: str) -> Tuple[List[str], List[Tuple[int, str]]]:
    if len(full) == 0:
        return [], []

    res = []
    quoted_indexes = []
    quotation_mode = False
    quotation_type = None
    temp = StringIO()
    hasText = False

    def is_quotation(ch: str):
        return ch == "\'" or ch == "\""

    def save_and_refresh():
        nonlocal res, temp, hasText
        res.append(temp.getvalue())
        temp.close()
        temp = StringIO()
        hasText = False

    for ch in full:
        if ch == ' ':  # is space
            if quotation_mode:  # the space is quoted
                temp.write(ch)
            else:  # the space is not quoted
                if hasText:  # has any text ahead
                    save_and_refresh()
                else:  # no text ahead
                    continue
        else:  # not space
            if is_quotation(ch):  # is " or '
                if quotation_mode:  # already had a quotation ahead
                    if ch == quotation_type:  # match the same quotation
                        save_and_refresh()
                        quoted_indexes.append((len(res) - 1, ch))
                    else:  # not the same quotation ,dismiss it
                        hasText = True
                        temp.write(ch)
                else:  # not enter quotation mode
                    # then enter
                    quotation_mode = True
                    quotation_type = ch
            else:  # not a space and not a ' and not a "
                hasText = True
                temp.write(ch)

    final = temp.getvalue()
    temp.close()
    if final:
        res.append(final)
    return res, quoted_indexes
