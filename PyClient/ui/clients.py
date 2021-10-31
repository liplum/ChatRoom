from typing import Set

import core.ioc as ioc
from core.events import event
import ui.outputs as output
from threading import RLock
from net.networks import i_network, server_token
from core.chats import *
from net import networks
import ui.inputs as _input
from ui.controls import xtextbox, window, state, smachine, client_state, cmd_mode
from utils import lock
from typing import Optional, Tuple
from io import StringIO
from datetime import datetime
import chars
import sys
import traceback
from net import msgs


class command:
    def __init__(self, _id: str, tip: str, handler):
        self.id_ = _id
        self.tip = tip
        self.handler = handler


def get_command_id_tip(cmd: command) -> str:
    s = StringIO()
    s.write(cmd.id_)
    s.write(" ")
    s.write(cmd.tip)
    res = s.getvalue()
    s.close()
    return res


class cmd_analyzer:
    def analyze(self, cmdline: str):
        pass


class cmdkey:
    def __init__(self):
        self.mappings: Set[chars.char] = set()
        self._on_map = event()
        self._on_demap = event()

    @property
    def on_map(self):
        """
        Para 1:cmdkey object


        Para 2:mapped char


        :return: event(textbox,int,str)
        """
        return self._on_map

    @property
    def on_demap(self):
        """
        Para 1:cmdkey object


        Para 2:demapped char


        :return: event(textbox,int,str)
        """
        return self._on_demap

    def map(self, char: chars.char) -> "cmdkey":
        self.mappings.add(char)
        self.on_map(self, char)
        return self

    def demap(self, char: chars.char, rematch: bool) -> "cmdkey":
        if rematch:
            for ch in self.mappings:
                if ch == char:
                    self.mappings.remove(ch)
                    self.on_demap(self, ch)
                    break
        else:
            try:
                self.mappings.remove(char)
                self.on_demap(self, char)
            except KeyError:
                pass
        return self

    def __eq__(self, other) -> bool:
        for ch in self.mappings:
            if ch == other:
                return True
        return False


class cmd_list:
    def __init__(self):
        self.cmds = {}

    def add(self, cmd: command):
        self.cmds[cmd.id_] = cmd


class client:
    def __init__(self):
        self.container: ioc.container = ioc.container()
        self._on_service_register = event()
        self._on_command_register = event()
        self._on_keymapping = event()
        self.cmds: cmd_list = cmd_list()
        self.running: bool = False
        self._display_lock: RLock = RLock()
        self._dirty = False
        self.logger = None
        self.cmdkeys = []
        self.key_quit_text_mode = self.key(cmdkey())
        self.key_enter_text = self.key(cmdkey())

    def key(self, ck: cmdkey) -> cmdkey:
        self.cmdkeys.append(ck)
        return ck

    @property
    def on_service_register(self) -> event:
        """
        Para 1:client object


        Para 1:container

        :return: event(client,container)
        """
        return self._on_service_register

    @property
    def on_command_register(self) -> event:
        """
        Para 1:

        :return: event()
        """
        return self._on_command_register

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
        return self.logger.logfile if self.logger is not None else None

    @log_file.setter
    def log_file(self, value):
        if self.logger is not None:
            self.logger.logfile = value

    def init(self) -> None:
        ct = self.container
        ct.register_singleton(output.i_logger, output.cmd_logger)
        ct.register_singleton(output.i_display, output.cmd_display)
        ct.register_instance(i_network, networks.network(self))

        # services register event
        self.on_service_register(self, ct)

        self.network: networks.network = ct.resolve(networks.i_network)
        self.inpt: _input.i_input = ct.resolve(_input.i_input)
        self.logger: output.i_logger = ct.resolve(output.i_logger)
        self.log_file = "cmd.log"
        self.display: output.i_display = ct.resolve(output.i_display)

        self.logger.msg("Service component initialized.")

        def on_msg_pre_analyzed(network, server_token, source, json):
            self.logger.msg(source)

        # self.network.on_msg_pre_analyzed.add(on_msg_pre_analyzed)

        self.win = window(self.display)
        self.win.fill_until_max = True
        self.gen_cmds()

        def set_client(state: state) -> None:
            state.client = self

        def gen_state(statetype: type) -> state:
            if issubclass(statetype, client_state):
                return statetype(self)
            else:
                return statetype()

        self.sm = smachine(state_pre=set_client, stype_pre=gen_state)

        self.textbox: xtextbox = xtextbox()

        self.textbox.on_append.add(lambda b, p, c: self.make_dirty())
        self.textbox.on_delete.add(lambda b, p, c: self.make_dirty())
        self.textbox.on_cursor_move.add(lambda b, f, c: self.make_dirty())
        self.textbox.on_list_replace.add(lambda b, f, c: self.make_dirty())

        self.channel_user = self.network.new_channel("User")
        self.channel_chatting = self.network.new_channel("Chatting")

        self.channel_chatting.register(msgs.chatting)

        def on_input(inpt, char):
            ch = inpt.consume_char()
            if ch is char:
                return self.sm.on_input(ch)
            else:
                self.logger.error(f"Input event provides a wrong char '{ch} -> {char}'.")

        self.inpt.on_input.add(on_input)

        for k in self.cmdkeys:
            self.on_keymapping(self, k)

    @property
    def need_update(self):
        return self._dirty

    def make_dirty(self):
        self._dirty = True

    def _clear_dirty(self):
        self._dirty = False

    def gen_cmds(self):
        def send_text():
            pass

        def refresh():
            pass

        self.cmds.add(command("#1", "send text", send_text))
        self.cmds.add(command("#0", "refresh", refresh))

        self.on_command_register(self.cmds)
        all_tips = StringIO()
        all_tips.write("Command\n")
        cmds = self.cmds.cmds
        for cmd_k in sorted(cmds):
            cmd = cmds[cmd_k]
            all_tips.write("\t")
            all_tips.write(get_command_id_tip(cmd))
            all_tips.write("\n")
        self.command_list_tip = all_tips.getvalue()
        all_tips.close()

    def connect(self, ip_and_port: Tuple[str, int]):
        self.network.connect(server_token(server=ip_and_port))

    def receive_text(self, user_id: userid, room_id: roomid, text: str, time: datetime):
        self.make_dirty()
        self.win.add_text(f"{time.strftime('%Y%m%d-%H:%M:%S')}\n\t{user_id}:{text}")

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
        _sm = self.sm
        _sm.enter(cmd_mode)
        while self.running:
            try:
                self.inpt.get_input()
                # self.tps.delay()
                if not self.need_update:
                    continue
                # The following is to need update
                self._clear_dirty()
                _sm.update()
                self.render()
            except Exception as e:
                traceback.print_exc()
                self.running = False
                """
                dlock(self.display.display_text, self.command_list_tip)
                dlock(self.display.display_text, "Enter a command:")
                inputs = i.input_list
                cmd_str = utils.compose(inputs)
                dlock(self.display.display_text, cmd_str) 
                cmd: command = get(self.cmds.cmds, cmd_str)
                if cmd is not None:
                    cmd.handler()
                else:
                    self.logger.error(f"Cannot identify command {cmd_str}")
                self.display_lock(self.display.render())
                """
        sys.exit(0)

    def render(self):
        tb = self.textbox.distext
        self.display_lock(self.display.display_text, tb)
        self.display_lock(self.display.render)

    def display_lock(self, func, *args, **kwargs):
        lock(self._display_lock, func, *args, **kwargs)

    def add_text(self, text: str):
        self.win.add_text(text)

    def __init_channels(self):
        pass


