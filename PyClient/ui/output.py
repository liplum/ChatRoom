from abc import ABC, abstractmethod
from enum import Enum, IntEnum, auto, unique
from datetime import datetime


class i_logger:
    def msg(self, text):
        pass

    def tip(self, text):
        pass

    def warn(self, text):
        pass

    def error(self, text):
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


def tinted_print(text: str, color: CmdColor, end=None):
    if end is None:
        print(f"\033[0;{int(color)}m{text}\033[0m")
    else:
        print(f"\033[0;{int(color)}m{text}\033[0m", end=end)


class cmd_logger(i_logger):
    def msg(self, text: str) -> None:
        cmd_logger.alert_print(text, AlertColor.Msg, "Message")

    def tip(self, text: str) -> None:
        cmd_logger.alert_print(text, AlertColor.Tip, "Tip")

    def warn(self, text: str) -> None:
        cmd_logger.alert_print(text, AlertColor.Warn, "Warn")

    def error(self, text: str) -> None:
        cmd_logger.alert_print(text, AlertColor.Error, "Error")

    @staticmethod
    def alert_print(text: str, color, alertLevel: str) -> None:
        time_stamp = datetime.now().strftime("%Y%m%d-%H:%M:%S")
        t = f"{time_stamp}[{alertLevel}]{text}"
        tinted_print(t, color)


class i_display:
    def display_text(self, text: str, end: str = "", color: CmdColor = None):
        pass

    def display_image(self, file_path: str):
        pass


class cmd_display(i_display):

    def display_text(self, text: str, end: str = "", color: CmdColor = None):
        if color is not None:
            tinted_print(text, color, end)
        else:
            print(text, end=end)

    def display_image(self, file_path: str):
        pass
