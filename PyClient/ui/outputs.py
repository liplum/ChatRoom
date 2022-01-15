import sys
import traceback
from abc import ABC, abstractmethod
from collections import deque
from datetime import datetime
from threading import Thread, currentThread
from typing import NoReturn, List, Deque, Collection, Optional

import GLOBAL
import i18n
from GLOBAL import StringIO
from core.filer import ifiler, Directory, File
from files import EndsWith
from ui.Consoles import *


class ilogger:
    def __init__(self):
        self._logfile: Optional[str] = None
        self._startup_screen: Optional[Collection[str]] = None
        self._close = False

    def msg(self, text, Async=True) -> NoReturn:
        pass

    def tip(self, text, Async=True) -> NoReturn:
        pass

    def warn(self, text, Async=True) -> NoReturn:
        pass

    def error(self, text, Async=True) -> NoReturn:
        pass

    def initialize(self):
        pass

    @property
    def output_to_cmd(self) -> bool:
        raise NotImplementedError()

    @output_to_cmd.setter
    def output_to_cmd(self, value: bool):
        raise NotImplementedError()

    @property
    def startup_screen(self) -> Optional[Collection[str]]:
        return self._startup_screen

    @startup_screen.setter
    def startup_screen(self, value: Optional[Collection[str]]):
        self._startup_screen = value

    def close(self):
        self._close = True

    @property
    def closed(self):
        return self._close


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


CmdFgColors = (CmdFgColor.Black, CmdFgColor.Red, CmdFgColor.Green, CmdFgColor.Yellow, CmdFgColor.Blue,
               CmdFgColor.Violet, CmdFgColor.Cyan, CmdFgColor.White)

CmdFgColorsWithoutBlack = (CmdFgColor.Red, CmdFgColor.Green, CmdFgColor.Yellow, CmdFgColor.Blue,
                           CmdFgColor.Violet, CmdFgColor.Cyan, CmdFgColor.White)

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


CmdBkColors = (CmdBkColor.Black, CmdBkColor.Red, CmdBkColor.Green, CmdBkColor.Yellow, CmdBkColor.Blue,
               CmdBkColor.Violet, CmdBkColor.Cyan, CmdBkColor.White)

CmdBkColorsWithoutBlack = (CmdBkColor.Red, CmdBkColor.Green, CmdBkColor.Yellow, CmdBkColor.Blue,
                           CmdBkColor.Violet, CmdBkColor.Cyan, CmdBkColor.White)

CmdStyleEnum = str


class CmdStyle:
    Default = '0'
    Bold = '1'
    Underline = '4'
    ReverseColor = '7'


CmdStyles = (CmdStyle.Default, CmdStyle.Bold, CmdStyle.Underline, CmdStyle.ReverseColor)


class AlertLevel:
    Msg = (CmdFgColor.White, "Message")
    Tip = (CmdFgColor.Blue, "Tip")
    Warn = (CmdFgColor.Yellow, "Warn")
    Error = (CmdFgColor.Red, "Error")


def tinted_print(text: str, style: CmdStyleEnum = CmdStyle.Default, fgcolor: Optional[CmdFgColorEnum] = None,
                 bkcolor: Optional[CmdBkColorEnum] = None,
                 end=None) -> NoReturn:
    print(tintedtxt(text, style, fgcolor, bkcolor, end), end="")


def tintedtxt(text: str, style: CmdStyleEnum = CmdStyle.Default, fgcolor: Optional[CmdFgColorEnum] = None,
              bkcolor: Optional[CmdBkColorEnum] = None,
              end=None) -> str:
    with StringIO() as s:
        tintedtxtIO(s, text, style, fgcolor, bkcolor, end)
        return s.getvalue()


def tintedtxtIO(IO, text: str, style: Optional[CmdStyleEnum] = None, fgcolor: Optional[CmdFgColorEnum] = None,
                bkcolor: Optional[CmdBkColorEnum] = None,
                end=None):
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
    if end:
        IO.write(end)


Content = str
Color = str
Item = Tuple[Content, Color]


class cmd_logger(ilogger):

    def __init__(self, output_to_cmd: bool = True):
        super().__init__()
        self._output_to_cmd = output_to_cmd
        self.removed = False
        self.initialized = False
        self.log_queue: Deque[Item] = deque()
        self.log_folder: Directory = Directory("log")

    def init(self, container):
        self.filer = container.resolve(ifiler)
        self.log_folder: Directory = self.filer.get_dir("log")

    def delete_outdated(self):
        self.removed = True
        now = datetime.now()
        all_log_files = self.log_folder.GetSubFiles(EndsWith(".log"))
        need_removed = []
        for log_file in all_log_files:
            logf = log_file.FullPath
            timestamp = os.path.getctime(logf)
            create_time = datetime.fromtimestamp(timestamp)
            delta = now - create_time
            if delta.days > 7:
                need_removed.append(logf)
        for file in need_removed:
            try:
                os.remove(file)
            except Exception as e:
                self.error(f"[Log]Can't delete out-dated log file {file}")

    @property
    def logfile(self) -> File:
        return self.log_folder.SubFile(f"{datetime.today().strftime('%Y%m%d')}.log")

    def msg(self, text: str, Async=True) -> NoReturn:
        self.alert(text, AlertLevel.Msg, Async)

    def tip(self, text: str, Async=True) -> NoReturn:
        self.alert(text, AlertLevel.Tip, Async)

    def warn(self, text: str, Async=True) -> NoReturn:
        self.alert(text, AlertLevel.Warn, Async)

    def error(self, text: str, Async=True) -> NoReturn:
        self.alert(text, AlertLevel.Error, Async)

    def alert(self, text: str, level: Tuple[CmdFgColorEnum, str], Async=True) -> None:
        if Async:
            self.add_alert(text, level)
        else:
            self.alert_print(text, level)

    def initialize(self):
        self.initialized = True
        if not self.removed:
            self.delete_outdated()
        self.render_startup_screen()
        self.log_thread = Thread(target=self.__logging, name="Log")
        self.log_thread.daemon = True
        self.log_thread.start()

    def render_startup_screen(self):
        if self.startup_screen:
            with open(self.logfile.FullPath, "a+", encoding='utf-8') as log:
                for s in self.startup_screen:
                    if self.output_to_cmd:
                        tinted_print(s)
                    log.write(s)
                    log.write('\n')

    def __logging(self):
        queue = self.log_queue
        content = ""
        while True:
            try:
                if len(queue) > 0:
                    content, color = queue.popleft()
                    if self.output_to_cmd:
                        tinted_print(content, fgcolor=color)
                    with open(self.logfile.FullPath, "a+", encoding='utf-8') as log:
                        log.write(content)
                        log.write('\n')
            except Exception as e:
                self.error(f"[Log]Can't Log text \"{content}\" because of {e}")

    def add_alert(self, text: str, level: Tuple[CmdFgColorEnum, str]) -> None:
        if self.closed:
            return
        color, label = level
        time_stamp = datetime.now().strftime("%Y%m%d-%H:%M:%S")
        cur_thread = currentThread()
        thread_name = cur_thread.getName()
        if GLOBAL.DEBUG:
            t = f"{time_stamp}[{thread_name}][DEBUG][{label}]{text}"
        else:
            t = f"{time_stamp}[{thread_name}][{label}]{text}"
        self.log_queue.append((t, color))

    def wait_for_logging(self):
        while len(self.log_queue) > 0:
            pass

    def alert_print(self, text: str, level: Tuple[CmdFgColorEnum, str]) -> None:
        self.wait_for_logging()
        color, label = level
        time_stamp = datetime.now().strftime("%Y%m%d-%H:%M:%S")
        if GLOBAL.DEBUG:
            t = f"{time_stamp}[DEBUG][{label}]{text}"
        else:
            t = f"{time_stamp}[{label}]{text}"
        if self.output_to_cmd:
            tinted_print(t, fgcolor=color)
        with open(self.logfile.FullPath, "a+", encoding='utf-8') as log:
            log.write(t)
            log.write('\n')

    @property
    def output_to_cmd(self) -> bool:
        return self._output_to_cmd

    @output_to_cmd.setter
    def output_to_cmd(self, value: bool):
        self._output_to_cmd = value


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
        size = GetTerminalScreenSize()
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
        size = GetTerminalScreenSize()
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
