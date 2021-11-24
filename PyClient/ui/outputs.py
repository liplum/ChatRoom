import os
import sys
import traceback
from abc import ABC, abstractmethod
from datetime import datetime
from io import StringIO
from typing import Optional, NoReturn, List, Tuple

import GLOBAL
import i18n
from core.filer import ifiler


def get_winsize() -> Tuple[int, int]:
    return os.get_terminal_size()


def get_winsize_default() -> Tuple[int, int]:
    return 80, 20


try:
    os.get_terminal_size()
except:
    get_winsize = get_winsize_default


class ilogger:
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


CmdFgColorEnum = str


class CmdFgColor:
    Black = ';30'
    Red = ';31'
    Green = ';32'
    Yellow = ';33'
    Blue = ';34'
    Violet = ';35'
    Cyan = ';36'
    White = ';37'


CmdBkColorEnum = str


class CmdBkColor:
    Black = ';40'
    Red = ';41'
    Green = ';42'
    Yellow = ';43'
    Blue = ';44'
    Violet = ';45'
    Cyan = ';46'
    White = ';47'


CmdStyleEnum = str


class CmdStyle:
    Default = '0'
    Bold = '1'
    Underline = '4'
    ReverseColor = '7'


class AlertLevel:
    Msg = (CmdFgColor.White, "Message")
    Tip = (CmdFgColor.Blue, "Tip")
    Warn = (CmdFgColor.Yellow, "Warn")
    Error = (CmdFgColor.Red, "Error")


def tinted_print(text: str, style: CmdStyleEnum = CmdStyle.Default, fgcolor: Optional[CmdFgColorEnum] = None,
                 bkcolor: Optional[CmdBkColorEnum] = None,
                 end='\n') -> NoReturn:
    print(tintedtxt(text, style, fgcolor, bkcolor, end), end="")


def tintedtxt(text: str, style: CmdStyleEnum = CmdStyle.Default, fgcolor: Optional[CmdFgColorEnum] = None,
              bkcolor: Optional[CmdBkColorEnum] = None,
              end='\n') -> str:
    with StringIO() as s:
        s.write("\033[")
        s.write(style)
        if fgcolor:
            s.write(fgcolor)
        if bkcolor:
            s.write(bkcolor)
        s.write('m')
        s.write(text)
        s.write("\033[0m")
        s.write(end)
        return s.getvalue()


def tintedtxtIO(IO, text: str, style: Optional[CmdStyleEnum] = None, fgcolor: Optional[CmdFgColorEnum] = None,
                bkcolor: Optional[CmdBkColorEnum] = None,
                end='\n'):
    IO.write("\033[")
    if style:
        IO.write(style)
    if fgcolor:
        IO.write(fgcolor)
    if bkcolor:
        IO.write(bkcolor)
    IO.write('m')
    IO.write(text)
    IO.write("\033[0m")
    IO.write(end)


class cmd_logger(ilogger):

    def __init__(self, output_to_cmd: bool = True):
        super().__init__()
        self.output_to_cmd = output_to_cmd

    def init(self, container):
        self.filer = container.resolve(ifiler)

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

    def alert_print(self, text: str, level: Tuple[CmdFgColorEnum, str]) -> None:
        color, label = level
        time_stamp = datetime.now().strftime("%Y%m%d-%H:%M:%S")
        if GLOBAL.DEBUG:
            t = f"{time_stamp}[DEBUG][{label}]{text}"
        else:
            t = f"{time_stamp}[{label}]{text}"
        if self.output_to_cmd:
            tinted_print(t, fgcolor=color)
        with open(self.logfile, "a+", encoding='utf-8') as log:
            log.write(t + '\n')


class buffer:
    def addtext(self, text: str = "", style: CmdStyleEnum = CmdStyle.Default, fgcolor: Optional[CmdFgColorEnum] = None,
                bkcolor: Optional[CmdBkColorEnum] = None, end: str = '\n') -> NoReturn:
        pass

    @property
    @abstractmethod
    def width(self):
        pass

    @property
    @abstractmethod
    def height(self):
        pass


class idisplay(ABC):
    @abstractmethod
    def render(self, buf: buffer) -> bool:
        pass

    @abstractmethod
    def gen_buffer(self) -> buffer:
        pass


class cmd_display(idisplay):
    """
    It uses buffer to store all items used be rendered soon until call render(self)
    """

    def __init__(self):
        pass

    def init(self, container: "container"):
        self.logger: ilogger = container.resolve(ilogger)

    @staticmethod
    def text(buffer_list, text: str = "", style: CmdStyleEnum = CmdStyle.Default,
             fgcolor: Optional[CmdFgColorEnum] = None,
             bkcolor: Optional[CmdBkColorEnum] = None, end: str = '\n') -> NoReturn:
        if fgcolor is None and bkcolor is None:
            added_text = f"{text}{end}"
        else:
            added_text = tintedtxt(text, style, fgcolor, bkcolor, end)
        buffer_list.append(added_text)
        return None

    def render(self, buf: buffer) -> bool:
        if isinstance(buf, cmd_display.cmd_buffer):
            for text in buf.render_list:
                try:
                    print(text, end='')
                except:
                    print(i18n.trans("outputs.render.print_error"))
                    self.logger.error(f"[Output]Cannot print the text because \n{traceback.format_exc()}")
            return True
        return False

    class cmd_buffer(buffer):
        def __init__(self, displayer: "cmd_display", width: int, height: int):
            super().__init__()
            self.displayer: "cmd_display" = displayer
            self.render_list: List[str] = []
            self._width = width
            self._height = height

        def addtext(self, text: str = "", style: CmdStyleEnum = CmdStyle.Default,
                    fgcolor: Optional[CmdFgColorEnum] = None,
                    bkcolor: Optional[CmdBkColorEnum] = None, end: str = '\n') -> NoReturn:
            self.displayer.text(self.render_list, text, style, fgcolor, bkcolor, end)

        @property
        def width(self):
            return self, _width

        @property
        def height(self):
            return self._height

    def gen_buffer(self) -> buffer:
        size = get_winsize()
        return cmd_display.cmd_buffer(self, size[0], size[1])


class full_cmd_display(idisplay):
    class buf(buffer):
        def __init__(self, width: int, height: int):
            super().__init__()
            self.buffer = StringIO()
            self._width = width
            self._height = height

        def addtext(self, text: str = "", style: Optional[CmdStyleEnum] = None,
                    fgcolor: Optional[CmdFgColorEnum] = None,
                    bkcolor: Optional[CmdBkColorEnum] = None, end: str = '\n') -> NoReturn:
            buffer = self.buffer
            if bkcolor is None and fgcolor is None and style is None:
                buffer.write(text)
                buffer.write(end)
            else:
                tintedtxtIO(buffer, text, style, fgcolor, bkcolor, end)

        @property
        def width(self):
            return self, _width

        @property
        def height(self):
            return self._height

    def gen_buffer(self) -> buffer:
        size = get_winsize()
        return full_cmd_display.buf(size[0], size[1])

    def render(self, buf: buffer) -> bool:
        if isinstance(buf, full_cmd_display.buf):
            try:
                sys.stdout.write(buf.buffer.getvalue())
            except:
                print(i18n.trans("outputs.render.print_error"))
                self.logger.error(f"[Output]Cannot print the text because \n{traceback.format_exc()}")
            finally:
                buf.buffer.close()
            return True
        return False
