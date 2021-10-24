from abc import ABC, abstractmethod
from enum import Enum, IntEnum, auto, unique
from datetime import datetime
from typing import Union, Optional, NoReturn, Tuple, List


class i_logger:
    def __init__(self):
        self.logfile: Optional[str] = None

    def msg(self, text) -> NoReturn:
        pass

    def tip(self, text) -> NoReturn:
        pass

    def warn(self, text) -> NoReturn:
        pass

    def error(self, text) -> NoReturn:
        pass


@unique
class CmdColor(IntEnum):
    Black = 30
    Red = 31
    Green = 32
    Yellow = 33
    Blue = 34
    Violet = 35
    Cyan = 36
    White = 37


class AlertColor(IntEnum):
    Msg = CmdColor.White
    Tip = CmdColor.Blue
    Warn = CmdColor.Yellow
    Error = CmdColor.Red


def tinted_print(text: str, color: CmdColor, end=None) -> NoReturn:
    if end is None:
        print(f"\033[0;{int(color)}m{text}\033[0m")
    else:
        print(f"\033[0;{int(color)}m{text}\033[0m", end=end)


def gen_tinted_text(text: str, color: CmdColor) -> str:
    return f"\033[0;{int(color)}m{text}\033[0m"


class cmd_logger(i_logger):

    def __init__(self, output_to_cmd: bool = True, logfile: Optional[str] = None):
        super().__init__()
        self.logfile: Optional[str] = logfile
        self.output_to_cmd = output_to_cmd

    def msg(self, text: str) -> NoReturn:
        cmd_logger.alert_print(text, AlertColor.Msg, "Message")

    def tip(self, text: str) -> NoReturn:
        cmd_logger.alert_print(text, AlertColor.Tip, "Tip")

    def warn(self, text: str) -> NoReturn:
        cmd_logger.alert_print(text, AlertColor.Warn, "Warn")

    def error(self, text: str) -> NoReturn:
        cmd_logger.alert_print(text, AlertColor.Error, "Error")

    @staticmethod
    def alert_print(text: str, color: Union[CmdColor, AlertColor], alertLevel: str) -> None:
        time_stamp = datetime.now().strftime("%Y%m%d-%H:%M:%S")
        t = f"{time_stamp}[{alertLevel}]{text}"
        tinted_print(t, color)
        if self.logfile is not None:
            with open(self.logfile, "w+") as log:
                log.writelines(t)


class i_display:
    def display_text(self, text: str = "", end: str = "", color: Optional[CmdColor] = None) -> NoReturn:
        pass

    def display_image(self, file_path: str):
        pass

    def render(self):
        pass


class cmd_display(i_display):
    """
    It uses buffer to store all items used be rendered soon until call render(self)
    """

    def __init__(self):
        self.render_list: List[Tuple[str, str]] = []

    def display_text(self, text: str = "", end: str = "", color: Optional[CmdColor] = None) -> NoReturn:
        if color is not None:
            self.render_list.append((gen_tinted_text(text, color), end))
        else:
            self.render_list.append((text, end))

    def clear_render_list(self):
        self.render_list = []

    def render(self):
        for item in self.render_list:
            print(item[0], end=item[1])
        self.clear_render_list()
