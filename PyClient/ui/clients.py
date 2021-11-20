import traceback
from functools import wraps
from threading import Thread

import GLOBAL
import ioc as ioc
import ui.inputs as _input
import ui.outputs as output
from cmd import cmdmanager
from core.chats import *
from core.filer import i_filer, filer
from core.operations import *
from core.settings import entity as settings
from events import event
from net import networks
from ui.k import cmdkey
from ui.windows import window
from utils import lock


class client:
    def __init__(self):
        self.container: ioc.container = ioc.container()
        self._on_service_register = event()
        self._on_cmd_register = event()
        self._on_keymapping = event()
        self._running: bool = False
        self._display_lock: RLock = RLock()
        self._dirty = False
        self.cmdkeys = []
        self.key_quit_text_mode = self.key(cmdkey())
        self.key_enter_text = self.key(cmdkey())
        self.root_path = None

    def key(self, ck: cmdkey) -> cmdkey:
        self.cmdkeys.append(ck)
        return ck

    def check_file_permission(self) -> bool:
        return os.access(self.root_path, os.F_OK & os.R_OK & os.W_OK)

    @property
    def on_service_register(self) -> event:
        """
        Para 1:client object


        Para 2:container

        :return: event(client,container)
        """
        return self._on_service_register

    @property
    def on_cmd_register(self) -> event:
        """
        Para 1:the manager of cmd

        :return: event(client,cmdmanager)
        """
        return self._on_cmd_register

    @property
    def on_keymapping(self) -> event:
        """
        Para 1: client object


        Para 1: key map

        :return: event(client,cmdkey)
        """
        return self._on_keymapping

    def init(self) -> None:
        ct = self.container
        ct.register_instance(client, self)
        ct.register_singleton(output.i_logger, output.cmd_logger)
        ct.register_singleton(output.i_display, output.cmd_display)
        ct.register_instance(i_network, networks.network(self))
        ct.register_singleton(cmdmanager, cmdmanager)
        ct.register_singleton(i_msgmager, msgmager)
        ct.register_singleton(i_msgfiler, msgfiler)
        ct.register_singleton(i_filer, filer)

        # services register event
        self.on_service_register(self, ct)

        self.network: networks.network = ct.resolve(networks.i_network)
        self.inpt: _input.i_input = ct.resolve(_input.i_input)
        self.logger: output.i_logger = ct.resolve(output.i_logger)
        self.logger.output_to_cmd = False

        if not self.check_file_permission():
            self.root_path = ""

        self.filer: i_filer = ct.resolve(i_filer)
        self.filer.root_path = self.root_path
        self.display: output.i_display = ct.resolve(output.i_display)
        self.cmd_manger: cmdmanager = ct.resolve(cmdmanager)
        self.logger.msg("[Client]Service component initialized.")
        self.msg_manager: i_msgmager = ct.resolve(i_msgmager)

        if GLOBAL.DEBUG:
            def on_msg_pre_analyzed(network, server_token, source, json):
                self.logger.msg(json)

            self.network.on_msg_pre_analyzed.add(on_msg_pre_analyzed)

        self.win = window(self, self.display)
        self._init_channels()
        self.on_cmd_register(self, self.cmd_manger)

        def on_input(inpt, char):
            ch = inpt.consume_char()
            if ch is char:
                return self.win.on_input(ch)
            else:
                self.logger.error(f"[Client]Input event provides a wrong char '{ch} -> {char}'.")

        self.inpt.on_input.add(on_input)

        for k in self.cmdkeys:
            self.on_keymapping(self, k)

        self.winsize = output.get_winsize()
        self.winsize_monitor = Thread(target=self.monitor_winsize)
        self.winsize_monitor.daemon = True

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
        cur = output.get_winsize()
        if self.winsize != cur:
            self.winsize = cur
            self.mark_dirty()

    def connect(self, ip: str, port: int):
        self.network.connect(server_token(ip, port))

    def receive_text(self, server: server_token, room_id: roomid, user_id: userid, text: str, time: datetime):
        self.msg_manager.receive(server, room_id, (time, user_id, text))
        self.mark_dirty()

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
            info: Dict[str, str] = configs.AutoLogin
            for server_full, ap in info.items():
                token = to_server_token(server_full)
                if token:
                    ap = ap.split()
                    if len(ap) == 2:
                        connect(self.network, token)
                        login(self.network, token, ap[0], ap[1])

    def auto_connection(self):
        configs = settings()
        connections = configs.AutoConnection
        for server_full_str in connections:
            token = to_server_token(server_full_str)
            if token:
                self.network.connect(token)

    def start(self):
        self._running = True
        try:
            i = self.inpt
            i.initialize()
            self.auto_connection()
            self.winsize_monitor.start()
            self.win.start()
            self.auto_login()
            self.win.gen_default_tab()
            self.render()
            while self._running:
                self.inpt.get_input()
                # self.tps.delay()
                if not self.need_update:
                    continue
                # The following is to need update
                self._clear_dirty()
                self.render()
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
        self.dlock(self.win.update_screen)()

    def dlock(self, func):
        @wraps(func)
        def inner(*args, **kwargs):
            return lock(self._display_lock, func, *args, **kwargs)

        return inner

    def add_text(self, text: str):
        self.win.add_text(text)
