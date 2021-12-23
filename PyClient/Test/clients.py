import os
import platform
import traceback

import GLOBAL
import ioc as ioc
import tasks
import ui.inputs as _input
import ui.outputs as output
from Test.windows import TestWindow
from core.chats import *
from core.filer import ifiler, filer
from core.operations import *
from timers import timer
from ui.Renders import IRender
from ui.core import *

system_type = platform.system()


class TestClient(iclient):
    def __init__(self):
        super().__init__()
        self._container: ioc.container = ioc.container()
        self._running: bool = False
        self._dirty = True
        self.root_path = None
        self.tps = timer.byFps(24)
        self.task_runner = tasks.task_runner(step_mode=tasks.byPercent(0.2), safe_mode=False)
        self.render_ticks = 0
        self.input_ticks = 0
        self.main_loop_ticks = 0

    def check_file_permission(self) -> bool:
        return os.access(self.root_path, os.F_OK & os.R_OK & os.W_OK)

    def init(self) -> None:
        ct = self.container
        ct.register_instance(iclient, self)
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
        self._render = ct.resolve(IRender)
        self._render.Initialize()
        self._displayer: output.idisplay = ct.resolve(output.idisplay)
        self.logger.msg("[Client]Service component initialized.")
        self.logger.msg(f"[Client]Client starts up on {system_type}.")

        self._win = TestWindow(self)

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
            inpt.initialize()
            self.win.start()
            self.win.gen_default_tab()
            first_rendered = False
            tps = self.tps
            tps.reset()
            while self._running:
                self.main_loop_ticks += 1
                if (self.need_update and tps.is_end) or (not first_rendered):
                    self.render()
                    tps.reset()
                    first_rendered = True
                self.handle_input()
                self.task_runner.run_step()
        except Exception as e:
            self.logger.error(f"[Client]{e}\n{traceback.format_exc()}", Async=False)
            self.stop()
        try:
            self.win.stop()
        except Exception as e:
            self.logger.error(f"[Client]{e}\n{traceback.format_exc()}", Async=False)
        self.logger.close()
        self.logger.tip("[Client]Programme quited.", Async=False)
        return

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
        if ch and self.win.accept_input:
            self.input_ticks += 1
            self.win.on_input(ch)
        self.run_coroutine()

    def __handle_input_blocked(self, inpt):
        inpt.get_input()
        while True:
            ch = inpt.consume_char()
            if ch and self.win.accept_input:
                self.input_ticks += 1
                self.win.on_input(ch)
                self.run_coroutine()
            if inpt.is_end:
                break

    def run_coroutine(self):
        self.win.run_coroutine()

    def render(self):
        self.render_ticks += 1
        self.__clear_dirty()
        self.win.update_screen()
        if GLOBAL.DEBUG:
            print(f"MTick={self.main_loop_ticks},RTick={self.render_ticks},ITick={self.input_ticks}")

    @property
    def win(self) -> iwindow:
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
