import json
import traceback

import GLOBAL
import ioc as ioc
import ui.inputs as _input
import ui.outputs as output
from cmd import cmdmanager
from core.chats import *
from core.filer import ifiler, filer
from core.operations import *
from core.settings import entity as settings
from net import networks
from ui.core import iclient
from ui.k import cmdkey
from ui.windows import window
from utils import get


class client(iclient):
    def __init__(self):
        super().__init__()
        self._container: ioc.container = ioc.container()
        self._running: bool = False
        self._display_lock: RLock = RLock()
        self._dirty = True
        self.cmdkeys = []
        self.key_quit_text_mode = self.key(cmdkey())
        self.key_enter_text = self.key(cmdkey())
        self.root_path = None

    def key(self, ck: cmdkey) -> cmdkey:
        self.cmdkeys.append(ck)
        return ck

    def check_file_permission(self) -> bool:
        return os.access(self.root_path, os.F_OK & os.R_OK & os.W_OK)

    def init(self) -> None:
        ct = self.container
        ct.register_instance(iclient, self)
        ct.register_singleton(output.ilogger, output.cmd_logger)
        ct.register_singleton(output.idisplay, output.full_cmd_display)
        ct.register_instance(inetwork, networks.network(self))
        ct.register_singleton(cmdmanager, cmdmanager)
        ct.register_singleton(imsgmager, msgmager)
        ct.register_singleton(imsgfiler, msgfiler)
        ct.register_singleton(ifiler, filer)

        # services register event
        self.on_service_register(self, ct)

        self._network: networks.network = ct.resolve(networks.inetwork)
        self.inpt: _input.iinput = ct.resolve(_input.iinput)
        self._logger: output.ilogger = ct.resolve(output.ilogger)
        self.logger.output_to_cmd = False
        if self.root_path is None:
            dirpath, filepath = utils.get_executed_path()
            self.root_path = dirpath
        if not self.check_file_permission():
            self.root_path = ""

        self.filer: ifiler = ct.resolve(ifiler)
        self.filer.root_path = self.root_path
        self._displayer: output.idisplay = ct.resolve(output.idisplay)
        self.cmd_manger: cmdmanager = ct.resolve(cmdmanager)
        self.logger.msg("[Client]Service component initialized.")
        self._msg_manager: imsgmager = ct.resolve(imsgmager)

        if GLOBAL.DEBUG:
            def on_msg_pre_analyzed(network, server_token, source, jobj):
                self.logger.msg(json.dumps(jobj, indent=2))

            self.network.on_msg_pre_analyzed.add(on_msg_pre_analyzed)

        self._win = window(self)
        self._init_channels()
        self.on_cmd_register(self, self.cmd_manger)

        def on_input(inpt, char):
            ch = inpt.consume_char()
            if ch is char:
                self.win.on_input(ch)
            else:
                self.logger.error(f"[Client]Input event provides a wrong char '{ch} -> {char}'.")

        self.inpt.on_input.add(on_input)

        for k in self.cmdkeys:
            self.on_keymapping(self, k)

        """
        self.winsize = output.get_winsize()
        self.winsize_monitor = Thread(target=self.monitor_winsize)
        self.winsize_monitor.daemon = True
        """

    def _init_channels(self):
        self.channel_user = self.network.new_channel("User")
        self.channel_chatting = self.network.new_channel("Chatting")

        self.channel_chatting.register(msgs.chatting)
        self.channel_user.register(msgs.register_request)
        self.channel_user.register(msgs.register_result)
        self.channel_user.register(msgs.authentication_req)
        self.channel_user.register(msgs.authentication_result)

    @property
    def need_update(self):
        return self._dirty

    def mark_dirty(self):
        self._dirty = True

    def _clear_dirty(self):
        self._dirty = False

    def monitor_winsize(self):
        while True:
            cur = output.get_winsize()
            if self.winsize != cur:
                self.winsize = cur
                self.mark_dirty()

    def connect(self, ip: str, port: int):
        self.network.connect(server_token(ip, port))

    def send_text(self, user_info: uentity, room_id: roomid, text: str):
        msg = msgs.chatting()
        msg.room_id = room_id
        msg.send_time = datetime.utcnow()
        msg.text = text
        msg.vcode = user_info.vcode
        msg.user_id = user_info.uid
        self.channel_chatting.send(user_info.server, msg)

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
            i = self.inpt
            i.initialize()
            self.auto_connection()
            # self.winsize_monitor.start()
            self.win.start()
            self.auto_login()
            self.win.gen_default_tab()
            while self._running:
                # self.tps.delay()
                if self.need_update:
                    if not self._running:
                        break
                    self.render()
                self.inpt.get_input()
        except Exception as e:
            self.logger.error(f"[Client]{e}\n{traceback.format_exc()}")
            self.stop()
        try:
            self.msg_manager.save_all()
            self.win.stop()
        except Exception as e:
            self.logger.error(f"[Client]{e}\n{traceback.format_exc()}")
        self.logger.tip("[Client]Programme quited.")
        return

    def stop(self):
        self._running = False

    def render(self):
        with self._display_lock:
            self._clear_dirty()
            self.win.update_screen()

    @property
    def display_lock(self) -> RLock:
        return self._display_lock

    @property
    def win(self) -> "window":
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
