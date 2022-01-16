import json
import platform
import traceback
from threading import Thread

import GLOBAL
import ioc as ioc
import net.networks as net
import tasks
import ui.inputs as _input
import ui.outputs as output
from core.chats import *
from core.filer import ifiler, filer
from core.operations import *
from core.rooms import iroom_manager, room_manager
from core.settings import entity as settings
from timers import timer
from ui.Apps import App
from ui.Consoles import *
from ui.Core import *
from ui.k import cmdkey
from utils import get

system_type = platform.system()


class Client(IClient):
    def __init__(self):
        super().__init__()
        self._container: ioc.container = ioc.container()
        self._running: bool = False
        self._dirty = True
        self.cmdkeys = []
        self.key_quit_text_mode = self.key(cmdkey())
        self.key_enter_text = self.key(cmdkey())
        self.root_path = None
        self.tps = timer.byFps(24)
        self.task_runner = tasks.task_runner(step_mode=tasks.byPercent(0.2), safe_mode=False)
        self.render_ticks = 0
        self.input_ticks = 0
        self.main_loop_ticks = 0

    def key(self, ck: cmdkey) -> cmdkey:
        self.cmdkeys.append(ck)
        return ck

    def check_file_permission(self) -> bool:
        return os.access(self.root_path, os.F_OK & os.R_OK & os.W_OK)

    def init(self) -> None:
        ct = self.container
        ct.register_instance(IClient, self)
        ct.register_singleton(output.ilogger, output.cmd_logger)
        ct.register_singleton(output.idisplay, output.full_cmd_display)
        ct.register_instance(inetwork, net.network(self))
        ct.register_singleton(cmdmanager, cmdmanager)
        ct.register_singleton(imsgmager, msgmager)
        ct.register_singleton(imsgfiler, msgfiler)
        ct.register_singleton(ifiler, filer)
        ct.register_singleton(iroom_manager, room_manager)

        # services register event
        self.on_service_register(self, ct)

        self.filer: ifiler = ct.resolve(ifiler)
        if self.root_path is None:
            dirpath, filepath = utils.get_executed_path()
            self.root_path = dirpath
        if not self.check_file_permission():
            self.root_path = ""

        self.filer.root_path = self.root_path
        self._network: net.inetwork = ct.resolve(net.inetwork)
        self.inpt: _input.iinput = ct.resolve(_input.iinput)
        self._logger: output.ilogger = ct.resolve(output.ilogger)
        self.logger.output_to_cmd = False
        self.logger.startup_screen = GLOBAL.LOGO
        self.logger.initialize()

        self._displayer: output.idisplay = ct.resolve(output.idisplay)
        self.cmd_manger: cmdmanager = ct.resolve(cmdmanager)
        self.logger.msg("[Client]Service component initialized.")
        self.logger.msg(f"[Client]Client starts up on {system_type}.")
        self._msg_manager: imsgmager = ct.resolve(imsgmager)

        if GLOBAL.DEBUG:
            def on_msg_pre_analyzed(network, server_token, source, jobj):
                self.logger.msg(json.dumps(jobj, indent=2, ensure_ascii=False))

            self.network.on_msg_pre_analyzed.Add(on_msg_pre_analyzed)

        self._win = App(self)
        self._init_channels()
        self.on_cmd_register(self, self.cmd_manger)

        for k in self.cmdkeys:
            self.on_keymapping(self, k)

        if CanGetTerminalScreenSize():
            self.winsize = GetTerminalScreenSize()
            self.winsize_monitor = Thread(target=self.monitor_winsize, name="SizeMonitor")
            self.winsize_monitor.daemon = True

    def _init_channels(self):
        self.channel_user = self.network.new_channel("User")
        self.channel_chatting = self.network.new_channel("Chatting")
        self.network.auto_register()

    @property
    def need_update(self):
        return self._dirty

    def mark_dirty(self):
        self._dirty = True

    def __clear_dirty(self):
        self._dirty = False

    def monitor_winsize(self):
        get_winsize = GetTerminalScreenSize
        while True:
            cur = get_winsize()
            if self.winsize != cur:
                self.winsize = cur
                self.mark_dirty()

    def connect(self, ip: str, port: int):
        self.network.connect(server_token(ip, port))

    def add_task(self, task: Callable):
        self.task_runner.add(task)

    def auto_login(self):
        configs = settings()
        if configs.AutoLoginSwitch:
            network = self.network
            entries: List = configs.AutoLogin
            for info in entries:
                info: dict
                server = get(info, "server")
                token = server_token.by(server)
                account = get(info, "account")
                password = get(info, "password")
                if utils.not_none(token, account, password):
                    connect(network, token)
                    login(network, token, account, password)

    def auto_connection(self):
        configs = settings()
        connections = configs.AutoConnection
        for server_full_str in connections:
            token = server_token.by(server_full_str)
            if token:
                self.network.connect(token)

    def start(self):
        self._running = True
        try:
            inpt = self.inpt
            inpt.initialize()
            self.auto_connection()
            # self.winsize_monitor.start()
            self.App.start()
            self.auto_login()
            self.App.gen_default_tab()
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
            self.msg_manager.save_all()
            self.App.stop()
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
        if GLOBAL.DEBUG:
            print(f"MTick={self.main_loop_ticks},RTick={self.render_ticks},ITick={self.input_ticks}")

    @property
    def App(self) -> IApp:
        return self._win

    @property
    def container(self) -> "container":
        return self._container

    @property
    def network(self) -> "inetwork":
        return self._network

    @property
    def logger(self) -> "ilogger":
        return self._logger

    @property
    def msg_manager(self) -> "imsgmager":
        return self._msg_manager

    @property
    def displayer(self) -> "idisplay":
        return self._displayer
