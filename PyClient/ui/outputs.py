from abc import ABC, abstractmethod
from datetime import datetime
from enum import IntEnum, unique
from typing import Union, Optional, NoReturn, List
import os

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
class CmdFgColor(IntEnum):
    Black = 30
    Red = 31
    Green = 32
    Yellow = 33
    Blue = 34
    Violet = 35
    Cyan = 36
    White = 37


class CmdBkColor(IntEnum):
    Black = 40
    Red = 41
    Green = 42
    Yellow = 43
    Blue = 44
    Violet = 45
    Cyan = 46
    White = 47


class AlertColor(IntEnum):
    Msg = CmdFgColor.White
    Tip = CmdFgColor.Blue
    Warn = CmdFgColor.Yellow
    Error = CmdFgColor.Red


def tinted_print(text: str, fgcolor: Optional[CmdFgColor] = None, bkcolor: Optional[CmdBkColor] = None,
                 end='\n') -> NoReturn:
    fg = 0 if fgcolor is None else int(fgcolor)
    bk = 0 if bkcolor is None else int(bkcolor)
    print(f"\033[0;{fg};{bk}m{text}\033[0m", end=end)


def gen_tinted_text(text: str, fgcolor: Optional[CmdFgColor], bkcolor: Optional[CmdBkColor] = None, end='\n') -> str:
    fg = 0 if fgcolor is None else int(fgcolor)
    bk = 0 if bkcolor is None else int(bkcolor)
    return f"\033[0;{fg};{bk}m{text}\033[0m{end}"


class cmd_logger(i_logger):

    def __init__(self, output_to_cmd: bool = True, logfile: Optional[str] = None):
        super().__init__()
        self.logfile: Optional[str] = logfile
        self.output_to_cmd = output_to_cmd

    def msg(self, text: str) -> NoReturn:
        self.alert_print(text, AlertColor.Msg, "Message")

    def tip(self, text: str) -> NoReturn:
        self.alert_print(text, AlertColor.Tip, "Tip")

    def warn(self, text: str) -> NoReturn:
        self.alert_print(text, AlertColor.Warn, "Warn")

    def error(self, text: str) -> NoReturn:
        self.alert_print(text, AlertColor.Error, "Error")

    def alert_print(self, text: str, color: Union[CmdFgColor, AlertColor], alertLevel: str) -> None:
        time_stamp = datetime.now().strftime("%Y%m%d-%H:%M:%S")
        t = f"{time_stamp}[{alertLevel}]{text}"
        tinted_print(t, color)
        if self.logfile is not None:
            with open(self.logfile, "a") as log:
                log.write(t + '\n')


class buffer:
    def addtext(self, text: str = "", end: str = '\n', fgcolor: Optional[CmdFgColor] = None,
                bkcolor: Optional[CmdBkColor] = None) -> NoReturn:
        pass
    
    @property
    @abstractmethod
    def width(self):
        pass

    @property
    @abstractmethod
    def height(self):
        pass

class i_display(ABC):
    @abstractmethod
    def render(self, buf: buffer) -> bool:
        pass

    @abstractmethod
    def gen_buffer(self) -> buffer:
        pass


class cmd_display(i_display):
    """
    It uses buffer to store all items used be rendered soon until call render(self)
    """

    def __init__(self):
        pass

    def text(self, buffer_list, text: str = "", end: str = '\n', fgcolor: Optional[CmdFgColor] = None,
             bkcolor: Optional[CmdBkColor] = None) -> NoReturn:
        if fgcolor is None and bkcolor is None:
            added_text = f"{text}{end}"
        else:
            added_text = gen_tinted_text(text, fgcolor, bkcolor, end)
        buffer_list.append(added_text)

    def render(self, buf: buffer) -> bool:
        if isinstance(buf, cmd_display.cmd_buffer):
            for text in buf.render_list:
                print(text, end='')
            return True
        return False

    class cmd_buffer(buffer):
        def __init__(self, displayer: "cmd_display",width:int,height:int):
            super().__init__()
            self.displayer: "cmd_display" = displayer
            self.render_list: List[str] = []
            self._width=width
            self._height=height

        def addtext(self, text: str = "", end: str = '\n', fgcolor: Optional[CmdFgColor] = None,
                    bkcolor: Optional[CmdBkColor] = None) -> NoReturn:
            self.displayer.text(self.render_list, text, end, fgcolor, bkcolor)

        @property
        def width(self):
            return self,_width

        @property
        def height(self):
            return self._height

    def gen_buffer(self) -> buffer:
        size = terminal.get_terminal_size()
        return cmd_display.cmd_buffer(self,size.columns,size.lines)
