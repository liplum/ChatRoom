from abc import ABC, abstractmethod

from typing import Dict, Tuple
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import json
from ui import output


class server_token:
    def __init__(self, ip: str = None, port: int = None, server: Tuple[str, int] = None):
        if server is not None:
            self.target = server
        elif not_none(ip, port):
            self.target = (ip, port)
        else:
            self.target = ("127.0.0.1", 8080)


class msg(ABC):
    @abstractmethod
    def read(self, json):
        pass

    @abstractmethod
    def write(self, json):
        pass


def get(dic: Dict, key):
    if key in dic:
        return dic[key]
    else:
        return None


def _get_not_none_one(*args):
    """
    :param args:all selections
    :return: the first not none one otherwise None
    """
    for arg in args:
        if arg is not None:
            return arg
    return None


class i_channel:
    def __init__(self, name):
        self.name = name

    def register(self, msg_type: type, msg_id: str = None, msg_handler=None):
        pass

    def receive_datapack(self, _json: Dict, msg_id: str, _from: server_token):
        pass


class channel(i_channel):
    def __init__(self, network: "i_network", name):
        super().__init__(name)
        self.network = network
        self.logger: output.i_logger = self.network.logger
        self.id2msg_and_handler: Dict[str, Tuple[type, function]] = {}
        self.msg2id: Dict[type, str] = {}

    def register(self, msg_type: type, msg_id: str = None, msg_handler=None):
        if msg_id is None:
            msg_id = msg_type.MessageID

        if msg_handler is None:
            if hasattr(msg_type, "handle"):
                msg_handler = msg_type.handle
            else:
                msg_handler = None

        self.id2msg_and_handler[msg_id] = (msg_type, msg_handler)
        self.msg2id[msg_type] = msg_id

    def receive_datapack(self, _json: Dict, msg_id: str, _from: server_token):
        pair = get(self.id2msg_and_handler, msg_id)
        if pair is not None:
            _msg = pair[0]
            handler = pair[0]
            if handler is not None:
                context = (self.network.client, server_token)
                handler(_msg, context)
        else:
            self.logger.error(f"Cannot find message type called {msg_id}")


class i_network:
    def __init__(self, client):
        self.client = client

    def connect(self, server: server_token):
        pass

    def send(self, server: server_token, _msg: msg):
        pass

    def receive(self):
        pass

    def new_channel(self, channel_name: str) -> channel:
        pass


class network(i_network):
    def __init__(self, client):
        super().__init__(client)
        self.socket: socket = socket(AF_INET, SOCK_STREAM)
        self.channels: Dict[str, channel] = {}

    def connect(self, server: server_token):
        self.socket.connect(server.target)
        self.listen_thread: Thread = Thread(target=self.__receive_datapack, args=(self.socket,))
        self.listen_thread.start()

    def init(self, container):
        self.logger = container.resolve(output.i_logger)

    def __receive_datapack(self, server_socket):
        while True:
            _datapack: datapack = read_one(server_socket)
            _json_msg: json_msg = convert_to_json_msg(_datapack)
            self.__analyse(_json_msg, server_socket)

    def __analyse(self, _json_msg: "json_msg", server: server_token):
        _json = _json_msg.json
        channel_name = get(_json, "ChannelName")
        msg_id = get(_json, "MessageID")
        if not_none(channel_name, msg_id):
            _channel: channel = get(self.channels, channel_name)
            if _channel is not None:
                _channel.receive_datapack(_json, msg_id, server)
            else:
                self.logger.error(f"Cannot find channel called {channel_name}")
        else:
            self.logger.error("Cannot analyse datapack")

    def send(self, server: server_token, _msg: msg):
        pass

    def receive(self):
        pass

    def new_channel(self, channel_name: str) -> channel:
        c = channel(self, channel_name)
        self.channels[channel_name] = c
        return c


def not_none(*args) -> bool:
    for arg in args:
        if arg is None:
            return False
    return True


class datapack:
    def __init__(self, barry: bytes):
        self.data: bytes = barry

    def get_bytes(self) -> bytes:
        return self.data


def read_one(_socket: socket) -> datapack:
    data_length_b = _socket.recv(4)
    total_length = convert.read_int(data_length_b)
    data = self.socket.recv(total_length)
    return datapack(data)


class json_msg:
    def __init__(self, _json):
        self.json: Dict = _json


def convert_to_json_msg(_datapack: datapack) -> json_msg:
    json_text = convert.read_str(data)
    _json = json.loads(json_text)
    return json_msg(_json)
