from abc import ABC, abstractmethod

from typing import Dict, Tuple
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import json
from ui import output


class msg(ABC):
    @abstractmethod
    def read(self, json):
        pass

    @abstractmethod
    def write(self, json):
        pass


def get(dic, key):
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


class channel:
    def __init__(self, name):
        self.name = name
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

    def receive_datapack(self, _json, msg_id: str):
        pair = get(self.id2msg_and_handler, msg_id)
        if pair is not None:
            _msg = pair[0]
            handler = pair[0]
            if handler is not None:
                context = (self, self.client)
                handler(_msg, context)
        else:
            pass


class i_network:
    def connect(self, config):
        pass

    def send(self):
        pass

    def receive(self):
        pass

    def start(self):
        pass

    def new_channel(self, channel_name: str) -> channel:
        pass


class network(i_network):
    def __init__(self):
        self.socket: socket = socket(AF_INET, SOCK_STREAM)
        self.channels: Dict[str, channel] = {}

    def connect(self, config):
        self.socket.connect(config)

    def init(self, container):
        self.logger = container.resolve(output.logger)

    def start(self):
        self.listen_thread: Thread = Thread(target=self.__receive_datapack)
        self.listen_thread.start()

    def __receive_datapack(self):
        while True:
            _datapack: datapack = read_one(self.socket)
            _json_msg: json_msg = convert_to_json_msg(_datapack)
            self.__analyze(_json_msg)

    def __analyze(self, _json_msg: "json_msg"):
        _json = _json_msg.json
        channel_name = get(_json, "ChannelName")
        msg_id = get(_json, "MessageID")
        if not_none(channel_name, msg_id):
            _channel = get(self.channels, channel_name)
            if _channel is not None:
                _channel.receive_datapack(_json, msg_id)
            else:
                self.logger.error(f"Cannot find channel called {channel_name}")
        else:
            self.logger.error("Cannot analyze datapack")

    def send(self):
        pass

    def receive(self):
        pass

    def new_channel(self, channel_name: str) -> channel:
        c = channel(channel_name)
        self.channels[channel_name] = c
        return c


def not_none(*args):
    for arg in args:
        if arg is None:
            return False
    return True


class datapack:
    def __init__(self, barry: bytes):
        self.data = barry

    def get_bytes(self):
        return self.data


def read_one(_socket: socket) -> datapack:
    data_length_b = _socket.recv(4)
    total_length = convert.read_int(data_length_b)
    data = self.socket.recv(total_length)
    return datapack(data)


class json_msg:
    def __init__(self, _json):
        self.json = _json


def convert_to_json_msg(_datapack) -> json_msg:
    json_text = convert.read_str(data)
    _json = json.loads(json_text)
    return json_msg(_json)
