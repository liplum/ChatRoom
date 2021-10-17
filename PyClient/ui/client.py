import core.ioc as ioc
from core.event import event
import ui.output as output
from select import select
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread, RLock
from core import convert
from network.network import i_network, server_token
import ui.input as _input


def lock(lock: RLock, func, *args):
    lock.acquire()
    func(args)
    lock.release()


class client:
    def __init__(self):
        self.container: ioc.container = ioc.container()
        self.on_service_register: event = event()
        self.running: bool = False
        self.display_lock: RLock = RLock()

    def init(self) -> None:
        self.container.register_singleton(output.i_logger, output.cmd_logger)
        self.container.register_singleton(_input.i_input, _input.cmd_input)
        self.container.register_singleton(output.i_display, output.cmd_display)
        self.on_service_register(self.container)
        self.network: i_network = self.container.resolve(i_network)
        self.input: _input.i_input = self.container.resolve(_input.i_input)
        self.display: output.i_display = self.container.resolve(output.i_display)

    def set_input(self, _input):
        self.input = _input

    def connect(self, ip_and_port):
        self.network.connect(server_token(ip_and_port))

    def start(self):
        self.running = True
        while self.running:
            pass

    def display_lock(self, func, *args):
        lock(self.display_lock, func, args)

    def __init_channels(self):
        pass


class windows:
    def __init__(self):
        self.history = []

    def display(self):
        pass
