from abc import ABC, abstractmethod
from enum import Enum, IntEnum, auto, unique
from datetime import datetime


class logger:
    @staticmethod
    def msg(text):
        pass

    @staticmethod
    def tip(text):
        pass

    @staticmethod
    def warn(text):
        pass

    @staticmethod
    def error(text):
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


class cmd_logger:
    @staticmethod
    def msg(text: str) -> None:
        cmd_logger.print(text, AlertColor.Msg, "Message")

    @staticmethod
    def tip(text: str) -> None:
        cmd_logger.print(text, AlertColor.Tip, "Tip")

    @staticmethod
    def warn(text: str) -> None:
        cmd_logger.print(text, AlertColor.Warn, "Warn")

    @staticmethod
    def error(text: str) -> None:
        cmd_logger.print(text, AlertColor.Error, "Error")

    @staticmethod
    def print(text: str, color: AlertColor, alertLevel: str) -> None:
        time_stamp = datetime.now().strftime("%Y%m%d-%H:%M:%S")
        print(f"\033[0;{int(color)}m{time_stamp}[{alertLevel}]{text}\033[0m")
