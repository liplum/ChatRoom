import core.ioc as ioc
from core.event import event
import ui.output as output
from select import select
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from core import convert


class client:
    def __init__(self):
        self.container = ioc.container()
        self.on_service_register = event()

    def init(self) -> None:
        self.container.register_singleton(output.logger, output.cmd_logger)
        self.on_service_register(self.container)

    def set_input(self, _input):
        self.input = _input

    def init_connect(self, config):
        self.connect_config = config
        self.socket = socket(AF_INET, SOCK_STREAM)

    def connect(self):
        ip_and_port = self.connect_config
        self.socket.connect(ip_and_port)

    def start(self):
        self.listen_thread = Thread(target=self.__receive_datapack)
        self.listen_thread.start()

    def __receive_datapack(self):
        while True:
            data_length_b = self.socket.recv(4)
            total_length = convert.read_int(data_length_b)
            data = self.socket.recv(total_length)
            res = convert.read_str(data)
            print(res)

    def __init_channels(self):
        pass
