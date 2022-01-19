import platform
import traceback
from threading import Thread

import GLOBAL
import ioc as ioc
import tasks
import ui.inputs as _input
import ui.outputs as output
from Test.Apps import TestApp
from core.chats import *
from core.filer import ifiler, filer
from core.operations import *
from timers import timer
from ui.Consoles import *
from ui.Core import *
from ui.Renders import IRender


class TestClient(IClient):
    def __init__(self):
        super().__init__()
        self._container: ioc.container = ioc.container()
        self._running: bool = False
        self._dirty = True
        self.root_path = None
        self.rps = timer.byFps(30)  # Render
        self.tps = timer.byFps(30)  # update
        self.task_runner = tasks.task_runner(step_mode=tasks.byPercent(0.2), safe_mode=False)
        self.render_ticks = 0
        self.input_ticks = 0
        self.main_loop_ticks = 0

    def check_file_permission(self) -> bool:
        return os.access(self.root_path, os.F_OK & os.R_OK & os.W_OK)

    def init(self) -> None:
        ct = self.container
        ct.register_instance(IClient, self)
        ct.register_singleton(output.ilogger, output.cmd_logger)
        ct.register_singleton(output.idisplay, output.full_cmd_display)
        ct.register_singleton(ifiler, filer)

        # services register event
        self.on_service_register(self, ct)

        self.filer: ifiler = ct.resolve(ifiler)
        if self.root_path is None:
            dirpath, filepath = utils.get_executed_path()
            self.root_path = dirpath
        if not self.check_file_permission():
            self.root_path = ""

        self.filer.root_path = self.root_path
        self.inpt: _input.iinput = ct.resolve(_input.iinput)
        self._logger: output.ilogger = ct.resolve(output.ilogger)
        self.logger.output_to_cmd = False
        self.logger.startup_screen = GLOBAL.LOGO
        self.logger.initialize()
        systemType = platform.system()
        systemVersion = platform.version()
        pythonImplementation = platform.python_implementation()
        pythonVersion = platform.python_version()
        pythonCompiler = platform.python_compiler()
        self.logger.tip(
            f"[Client]Client starts on {systemType} {systemVersion} by {pythonImplementation} {pythonVersion} compiled by {pythonCompiler}")
        self._render = ct.resolve(IRender)
        self._render.InitRender()
        self._displayer: output.idisplay = ct.resolve(output.idisplay)
        self.logger.msg("[Client]Service component initialized.")

        self._win = TestApp(self)

        if CanGetTerminalScreenSize():
            self.winsize = GetTerminalScreenSize()
            self.winsize_monitor = Thread(target=self.monitor_winsize, name="SizeMonitor")
            self.winsize_monitor.daemon = True

    def monitor_winsize(self):
        get_winsize = GetTerminalScreenSize
        while True:
            cur = get_winsize()
            if self.winsize != cur:
                self.winsize = cur
                self._render.OnResized()
                self.mark_dirty()

    @property
    def need_update(self):
        return self._dirty

    def mark_dirty(self):
        self._dirty = True

    def __clear_dirty(self):
        self._dirty = False

    def connect(self, ip: str, port: int):
        self.network.connect(server_token(ip, port))

    def add_task(self, task: Callable):
        self.task_runner.add(task)

    def start(self):
        self._running = True
        try:
            inpt = self.inpt
            inpt.InitInput()
            self.App.start()
            self.App.gen_default_tab()
            first_rendered = False
            rps = self.rps
            rps.reset()
            tps = self.tps
            tps.reset()
            while self._running:
                self.main_loop_ticks += 1
                if tps.is_end:
                    self.Tick()
                    tps.reset()
                if (self.need_update and rps.is_end) or (not first_rendered):
                    self.render()
                    rps.reset()
                    first_rendered = True
                self.handle_input()
                self.task_runner.run_step()
        except Exception as e:
            self.logger.error(f"[Client]{e}\n{traceback.format_exc()}", Async=False)
            self.stop()
        try:
            self.App.stop()
        except Exception as e:
            self.logger.error(f"[Client]{e}\n{traceback.format_exc()}", Async=False)
        self.logger.close()
        self.logger.tip("[Client]Programme quited.", Async=False)
        return

    def Tick(self):
        self.App.OnTick()

    def stop(self):
        self._running = False

    def handle_input(self):
        inpt = self.inpt
        if inpt.is_blocked_input:
            self.__handle_input_blocked(inpt)
        else:
            self.__handle_nonblocking_input(inpt)

    def __handle_nonblocking_input(self, inpt):
        inpt.get_input()
        ch = inpt.consume_char()
        if ch and self.App.accept_input:
            self.input_ticks += 1
            self.App.on_input(ch)
        self.run_coroutine()

    def __handle_input_blocked(self, inpt):
        inpt.get_input()
        while True:
            ch = inpt.consume_char()
            if ch and self.App.accept_input:
                self.input_ticks += 1
                self.App.on_input(ch)
                self.run_coroutine()
            if inpt.is_end:
                break

    def run_coroutine(self):
        self.App.run_coroutine()

    def render(self):
        self.render_ticks += 1
        self.__clear_dirty()
        self.App.update_screen()
        if GLOBAL.DEBUG and False:
            print(f"MTick={self.main_loop_ticks},RTick={self.render_ticks},ITick={self.input_ticks}")

    @property
    def App(self) -> IApp:
        return self._win

    @property
    def container(self) -> "container":
        return self._container

    @property
    def network(self) -> "inetwork":
        raise NotImplementedError()

    @property
    def logger(self) -> "ilogger":
        return self._logger

    @property
    def msg_manager(self) -> "imsgmager":
        raise NotImplementedError()

    @property
    def displayer(self) -> "idisplay":
        return self._displayer

    @property
    def Render(self) -> IRender:
        return self._render
