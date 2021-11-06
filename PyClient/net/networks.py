import json
from abc import ABC, abstractmethod
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from typing import Dict, Tuple, Callable

from core import converts
from core.events import event
from ui import outputs
from core.utils import get, not_none


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

    def __repr__(self):
        return self.target.__repr__()

    def __eq__(self, other):
        if isinstance(other, server_token):
            return self.target == other.target
        elif isinstance(other, tuple):
            return self.target == other
        return False

    def __hash__(self):
        return hash(self.target)


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
        self._on_msg_received = event(cancelable=True)

    @property
    def on_msg_received(self):
        """
        Para 1:network object

        Para 2:msg object

        Para 2:the msg's corresponding handler (if it doesn't have,provide null)

        Cancelable:If yes,it will stop any more handle on this msg

        :return: event(i_channel,msg,callable[msg,"context tuple"])
        """
        return self._on_msg_received

    def register(self, msg_type: type, msg_id: str = None, msg_handler=None):
        pass

    def receive_datapack(self, _json: Dict, msg_id: str, _from: server_token):
        pass


class channel(i_channel):
    def __init__(self, network: "i_network", name):
        super().__init__(name)
        self.network = network
        self.logger: outputs.i_logger = network.logger
        self.id2msgt_and_handler: Dict[str, Tuple[type, Callable[[msg, Tuple], None]]] = {}
        self.msg2id: Dict[type, str] = {}

    def register(self, msg_type: type, msg_id: str = None, msg_handler=None):
        if msg_id is None:
            msg_id = msg_type.name

        if msg_handler is None:
            if hasattr(msg_type, "handle"):
                msg_handler = msg_type.handle
            else:
                msg_handler = None

        self.id2msgt_and_handler[msg_id] = (msg_type, msg_handler)
        self.msg2id[msg_type] = msg_id

    def receive_datapack(self, _json: Dict, msg_id: str, _from: server_token):
        info = get(self.id2msgt_and_handler, msg_id)
        if info is not None:
            msgtype, handler = info
            msg = msgtype()
            msg.read(_json)
            if not self.on_msg_received(self, msg, handler):
                if handler is not None:
                    context = (self.network.client, self, server_token)
                    handler(msg, context)
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
        self._on_msg_pre_analyzed = event()

    @property
    def on_msg_pre_analyzed(self):
        """
        Para 1:network object

        Para 2:server token

        Para 3:source json text

        Para 4:json dictionary

        :return: event(network,server_token,source,json)
        """
        return self._on_msg_pre_analyzed

    def get_channel(self, name: str):
        return get(self.channels, name)

    def connect(self, server: server_token):
        skt = socket(AF_INET, SOCK_STREAM)
        skt.connect(server.target)
        listen = Thread(target=self.__receive_datapack, args=(server, skt))
        listen.daemon = True
        self.sockets[server] = (skt, listen)
        listen.start()

    def init(self, container):
        self.logger: outputs.i_logger = container.resolve(outputs.i_logger)

    def __receive_datapack(self, token: server_token, server_socket):
        while True:
            _datapack: datapack = read_one(server_socket)
            json_text = converts.read_str(_datapack.data)
            _json = json.loads(json_text)
            self.on_msg_pre_analyzed(self, token, json_text, _json)
            self.__analyse(_json, server_socket)

    def __analyse(self, _json: Dict, server: server_token):
        channel_name = get(_json, "ChannelName")
        msg_id = get(_json, "MessageID")
        if not_none(channel_name, msg_id):
            _channel: channel = get(self.channels, channel_name)
            if _channel is not None:
                if "Content" in _json:
                    content = _json["Content"]
                else:
                    content = {}
                    _json["Content"] = content
                _channel.receive_datapack(content, msg_id, server)
            else:
                self.logger.error(f"Cannot find channel called {channel_name}")
        else:
            self.logger.error("Cannot analyse datapack")

    def send(self, server: server_token, _msg: msg, jobj: Dict):
        content = {}
        jobj['Content'] = content
        _msg.write(content)
        info = get(self.sockets, server)
        if info is not None:
            skt, _ = info
            skt: socket
            jobj_str = json.dumps(jobj)
            jobj_str_b = converts.write_str(jobj_str)
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
    length_b = converts.write_int(length)
    res = bytearray(length_b)
    res.extend(dp.get_bytes())
    return bytes(res)


class datapack:
    def __init__(self, barry: bytes):
        self.data: bytes = barry

    def get_bytes(self) -> bytes:
        return self.data


def read_one(_socket: socket) -> datapack:
    data_length_b = _socket.recv(4)
    total_length: int = converts.read_int(data_length_b)
    data = _socket.recv(total_length)
    return datapack(data)
