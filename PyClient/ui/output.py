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


class cmd_logger(i_logger):
    def msg(self, text: str) -> None:
        cmd_logger.print(text, AlertColor.Msg, "Message")

    def tip(self, text: str) -> None:
        cmd_logger.print(text, AlertColor.Tip, "Tip")

    def warn(self, text: str) -> None:
        cmd_logger.print(text, AlertColor.Warn, "Warn")

    def error(self, text: str) -> None:
        cmd_logger.print(text, AlertColor.Error, "Error")

    def print(self, text: str, color: AlertColor, alertLevel: str) -> None:
        time_stamp = datetime.now().strftime("%Y%m%d-%H:%M:%S")
        print(f"\033[0;{int(color)}m{time_stamp}[{alertLevel}]{text}\033[0m")


class i_display:
    def display_text(self, text: str):
        pass

    def display_image(self, file_path: str):
        pass


class cmd_display(i_display):

    def display_text(self, text: str):
        print(text, end="")

    def display_image(self, file_path: str):
        pass
