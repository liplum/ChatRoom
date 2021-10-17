import core.ioc as ioc
from core.event import event
import ui.output as output
from select import select
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from core import convert
from network.network import i_network


class client:
    def __init__(self):
        self.container: ioc.container = ioc.container()
        self.on_service_register: event = event()

    def init(self) -> None:
        self.container.register_singleton(output.logger, output.cmd_logger)
        self.on_service_register(self.container)
        self.network: i_network = self.container.resolve(i_network)

    def set_input(self, _input):
        self.input = _input

    def init_connect(self, config):
        self.connect_config = config

    def connect(self):
        ip_and_port = self.connect_config
        self.network.connect(ip_and_port)

    def start(self):
        self.network.start()

    def __init_channels(self):
        pass
