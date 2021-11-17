import os
from abc import ABC, abstractmethod
from datetime import datetime
from enum import IntEnum, unique
from typing import Optional, NoReturn, List, Tuple

from core.filer import i_filer


def get_winsize() -> Tuple[int, int]:
    return os.get_terminal_size()


def get_winsize_default() -> Tuple[int, int]:
    return 80, 20


try:
    os.get_terminal_size()
except:
    get_winsize = get_winsize_default


class i_logger:
    def __init__(self):
        self._logfile: Optional[str] = None

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


class AlertLevel:
    Msg = (CmdFgColor.White, "Message")
    Tip = (CmdFgColor.Blue, "Tip")
    Warn = (CmdFgColor.Yellow, "Warn")
    Error = (CmdFgColor.Red, "Error")


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

    def __init__(self, output_to_cmd: bool = True):
        super().__init__()
        self.output_to_cmd = output_to_cmd

    def init(self, container):
        self.filer = container.resolve(i_filer)

    @property
    def logfile(self):
        return self.filer.get_file(f"/log/{datetime.today().strftime('%Y%m%d')}.log")

    def msg(self, text: str) -> NoReturn:
        self.alert_print(text, AlertLevel.Msg)

    def tip(self, text: str) -> NoReturn:
        self.alert_print(text, AlertLevel.Tip)

    def warn(self, text: str) -> NoReturn:
        self.alert_print(text, AlertLevel.Warn)

    def error(self, text: str) -> NoReturn:
        self.alert_print(text, AlertLevel.Error)

    def alert_print(self, text: str, level: Tuple[CmdFgColor, str]) -> None:
        color, label = level
        time_stamp = datetime.now().strftime("%Y%m%d-%H:%M:%S")
        t = f"{time_stamp}[{label}]{text}"
        if self.output_to_cmd:
            tinted_print(t, fgcolor=color)
        with open(self.logfile, "a+", encoding='utf-8') as log:
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
        def __init__(self, displayer: "cmd_display", width: int, height: int):
            super().__init__()
            self.displayer: "cmd_display" = displayer
            self.render_list: List[str] = []
            self._width = width
            self._height = height

        def addtext(self, text: str = "", end: str = '\n', fgcolor: Optional[CmdFgColor] = None,
                    bkcolor: Optional[CmdBkColor] = None) -> NoReturn:
            self.displayer.text(self.render_list, text, end, fgcolor, bkcolor)

        @property
        def width(self):
            return self, _width

        @property
        def height(self):
            return self._height

    def gen_buffer(self) -> buffer:
        size = get_winsize()
        return cmd_display.cmd_buffer(self, size[0], size[1])
