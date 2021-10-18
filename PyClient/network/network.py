from abc import ABC, abstractmethod

from typing import Dict, Tuple
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import json
from ui import output
from utils import get, not_none
from core import convert


class server_token:
    def __init__(self, ip: str = None, port: int = None, server: Tuple[str, int] = None):
        if server is not None:
            self.target = server
        elif not_none(ip, port):
            self.target = (ip, port)
        else:
            self.target = ("127.0.0.1", 8080)

    def __str__(self):
        return self.target.__str__()


class msg(ABC):
    @abstractmethod
    def read(self, json):
        pass

    @abstractmethod
    def write(self, json):
        pass


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
            msg = _msg()
            msg.read(_json)
            handler = pair[0]
            if handler is not None:
                context = (self.network.client, server_token)
                handler(_msg, context)
        else:
            self.logger.error(f"Cannot find message type called {msg_id}")

    def send(self, to: server_token, msg):
        msg_id = get(self.msg2id, type(msg))
        if msg_id is not None:
            jobj = {
                "ChannelName": self.name,
                "MessageID": msg_id
            }
            self.network.send(to, msg, jobj)
        else:
            self.logger.error(f"Cannot find message type {msg_id}")


class i_network:
    def __init__(self, client):
        self.client = client

    def connect(self, server: server_token):
        pass

    def send(self, server: server_token, _msg: msg, jobj: Dict):
        pass

    def new_channel(self, channel_name: str) -> channel:
        pass

    def get_channel(self, name: str):
        pass


class network(i_network):
    def __init__(self, client):
        super().__init__(client)
        self.sockets: Dict[server_token, Tuple[socket, Thread]] = {}
        self.channels: Dict[str, channel] = {}

    def get_channel(self, name: str):
        return get(self.channels, name)

    def connect(self, server: server_token):
        skt = socket(AF_INET, SOCK_STREAM)
        skt.connect(server.target)
        listen = Thread(target=self.__receive_datapack, args=(self.socket,))
        self.sockets[server] = (skt, listen)
        listen.start()

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

    def send(self, server: server_token, _msg: msg, jobj: Dict):
        _msg.write(jobj)
        info = get(self.sockets, server)
        if info is not None:
            skt, _ = info
            skt: socket
            jobj_str = json.dumps(jobj)
            jobj_str_b = convert.write_str(jobj_str)
            dp = datapack(jobj_str_b)
            skt.send(to_bytes_starting_with_len(dp))
        else:
            self.logger.error(f"Cannot find server {server}")

    def new_channel(self, channel_name: str) -> channel:
        c = channel(self, channel_name)
        self.channels[channel_name] = c
        return c


def to_bytes_starting_with_len(dp: "datapack") -> bytes:
    length = len(dp.get_bytes())
    length_b = convert.write_int(length)
    res = bytearray(length_b)
    res.extend(dp.get_bytes())
    return bytes(bytearray)


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
