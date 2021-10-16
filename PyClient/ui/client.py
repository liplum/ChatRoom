import core.ioc as ioc
from core.event import event
import ui.output as output
from select import select
from socket import socket,AF_INET,SOCK_STREAM


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
        self.socket=socket(AF_INET,SOCK_STREAM)

    def connect(self):
        ip_and_port=self.connect_config
        self.socket.connect(ip_and_port)

    def start(self):
        readable = [self.input,self.socket]
        writeable = []
        exception = []
        while True:
            rs, ws, es = select(readable, writeable, exception)
            for r in rs:
                if r is self.input:
                    pass
                elif r is self.socket:
                    pass

    def __init_channels(self):
        pass
