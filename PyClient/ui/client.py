from typing import List

import core.ioc as ioc
from core.event import event
import ui.output as output
from select import select
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread, RLock
from core import convert
from network.network import i_network, server_token
from network import network
import ui.input as _input
import os
from utils import get


def clear_screen():
    os.system("cls")


def lock(lock: RLock, func, *args, **kwargs):
    lock.acquire()
    func(*args, **kwargs)
    lock.release()


class command:
    def __init__(self, _id: str, tip: str, handler):
        self.id_ = _id
        self.tip = tip
        self.handler = handler


def get_command_id_tip(cmd: command) -> str:
    return f"{cmd.id_} {cmd.tip}"


class cmd_list:
    def __init__(self):
        self.cmds = {}

    def add(self, cmd: command):
        self.cmds[cmd.id_] = cmd


class client:
    def __init__(self):
        self.container: ioc.container = ioc.container()
        self.on_service_register: event = event()
        self.on_command_register: event = event()
        self.cmds: cmd_list = cmd_list()
        self.running: bool = False
        self._display_lock: RLock = RLock()

    def init(self) -> None:
        self.container.register_singleton(output.i_logger, output.cmd_logger)
        self.container.register_singleton(_input.i_input, _input.cmd_input)
        self.container.register_singleton(output.i_display, output.cmd_display)
        self.network: network.network = network.network(self)
        self.container.register_instance(i_network, self.network)
        self.on_service_register(self.container)

        self.input_: _input.i_input = self.container.resolve(_input.i_input)
        self.logger: output.i_logger = self.container.resolve(output.i_logger)
        self.display: output.i_display = self.container.resolve(output.i_display)
        self.win = windows(self.display)

        self.gen_cmds()

    def gen_cmds(self):
        def send_text():
            pass

        def refresh():
            pass

        self.cmds.add(command("#1", "send text", send_text))
        self.cmds.add(command("#0", "refresh", refresh))

        self.on_command_register(self.cmds)
        res = "Command\n"
        cmds = self.cmds.cmds
        for cmd_k in sorted(cmds):
            cmd = cmds[cmd_k]
            res = f"{res}\t{get_command_id_tip(cmd)}\n"
        self.command_list_tip = res

    def connect(self, ip_and_port):
        self.network.connect(server_token(ip_and_port))

    def start(self):
        self.running = True
        while self.running:
            self.display_lock(self.win.display)
            self.display_lock(self.display.display_text, self.command_list_tip)
            self.display_lock(self.display.display_text, "Enter a command:")
            cmd_str = self.input_.get_input()
            cmd: command = get(self.cmds.cmds, cmd_str)
            if cmd is not None:
                cmd.handler()
            else:
                self.logger.error(f"Cannot identify command {cmd_str}")

    def display_lock(self, func, *args, **kwargs):
        lock(self._display_lock, func, *args, **kwargs)

    def add_text(self, text: str):
        self.win.add_text(text)

    def __init_channels(self):
        pass


class windows:
    def __init__(self, displayer: output.i_display):
        self.history: List[str] = []
        self.max_display_line = 10
        self.displayer: output.i_display = displayer

    def display(self):
        clear_screen()
        if len(self.history) < self.max_display_line:
            displayed = self.history
        else:
            displayed = self.history[-self.max_display_line]
        for d in displayed:
            self.displayer.display_text(d, end="\n")

    def add_text(self, text: str):
        self.history.append(text)

    def clear_all(self):
        self.history = []
