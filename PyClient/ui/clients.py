import sys
import traceback
from functools import wraps
from threading import Thread

import core.ioc as ioc
import ui.inputs as _input
import ui.outputs as output
from cmd import cmdmanager
from core.chats import *
from core.events import event
from core.utils import lock
from net import msgs
from net import networks
from net.networks import i_network, server_token
from ui.controls import window
from ui.k import cmdkey


class client:
    def __init__(self):
        self.container: ioc.container = ioc.container()
        self._on_service_register = event()
        self._on_cmd_register = event()
        self._on_keymapping = event()
        self.running: bool = False
        self._display_lock: RLock = RLock()
        self._dirty = False
        self.logger = None
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

    @property
    def log_file(self) -> Optional[str]:
        logger = self.logger
        return f"{logger.logfile_dir}{logger.logfile}" if logger else None

    @log_file.setter
    def log_file(self, dir_file):
        logger = self.logger
        if logger:
            logger.logfile_dir = dir_file[0]
            logger.logfile = dir_file[1]

    def init(self) -> None:
        ct = self.container
        ct.register_instance(client, self)
        ct.register_singleton(output.i_logger, output.cmd_logger)
        ct.register_singleton(output.i_display, output.cmd_display)
        ct.register_instance(i_network, networks.network(self))
        ct.register_singleton(cmdmanager, cmdmanager)
        ct.register_singleton(i_msgmager, msgmager)
        ct.register_singleton(i_msgfiler, msgfiler)

        # services register event
        self.on_service_register(self, ct)

        self.network: networks.network = ct.resolve(networks.i_network)
        self.inpt: _input.i_input = ct.resolve(_input.i_input)
        self.logger: output.i_logger = ct.resolve(output.i_logger)
        self.today = datetime.today()

        if not self.check_file_permission():
            self.root_path=""

        self.log_file = f"{self.root_path}/log", f"{self.today.strftime('%Y%m%d')}.log"
        self.display: output.i_display = ct.resolve(output.i_display)
        self.cmd_manger: cmdmanager = ct.resolve(cmdmanager)
        self.logger.msg("Service component initialized.")
        self.msg_filer: i_msgfiler = ct.resolve(i_msgfiler)
        self.msg_filer.msg_storages_dir = f"{self.root_path}/data"
        self.msg_manager: i_msgmager = ct.resolve(i_msgmager)

        def on_msg_pre_analyzed(network, server_token, source, json):
            self.logger.msg(source)

        # self.network.on_msg_pre_analyzed.add(on_msg_pre_analyzed)

        self.win = window(self, self.display)
        self._init_channels()
        self.on_cmd_register(self, self.cmd_manger)

        def on_input(inpt, char):
            ch = inpt.consume_char()
            if ch is char:
                return self.win.on_input(ch)
            else:
                self.logger.error(f"Input event provides a wrong char '{ch} -> {char}'.")

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

    def connect(self, ip_and_port: Tuple[str, int]):
        self.network.connect(server_token(server=ip_and_port))

    def receive_text(self, room_id: roomid, user_id: userid, text: str, time: datetime):
        self.msg_manager.receive(room_id, (time, user_id, text))
        self.mark_dirty()

    def send_text(self, room_id: roomid, text: str, server: server_token):
        msg = msgs.chatting()
        msg.room_id = room_id
        msg.send_time = datetime.utcnow()
        msg.text = text
        msg.user_id = userid("TestID")
        self.channel_chatting.send(server, msg)

    def start(self):
        self.running = True
        i = self.inpt
        i.initialize()
        self.winsize_monitor.start()
        self.win.start()
        self.render()
        while self.running:
            try:
                self.inpt.get_input()
                # self.tps.delay()
                if not self.need_update:
                    continue
                # The following is to need update
                self._clear_dirty()
                self.render()
            except Exception as e:
                traceback.print_exc()
                self.running = False
        sys.exit(0)

    def render(self):
        self.dlock(self.win.update_screen)()

    def dlock(self, func):
        @wraps(func)
        def inner(*args, **kwargs):
            return lock(self._display_lock, func, *args, **kwargs)

        return inner

    def add_text(self, text: str):
        self.win.add_text(text)
