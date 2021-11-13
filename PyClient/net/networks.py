import json
from abc import ABC, abstractmethod
from collections import namedtuple
from functools import wraps
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread, RLock
from typing import Dict, Tuple, Callable, List

from core import converts
from events import event
from core.shared import server_token
from utils import get, not_none
from ui import outputs


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

    def send(self, to: server_token, msg):
        pass


Context = namedtuple("Context", ["client", "channel", "token", "network"])


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
                    context = Context(self.network.client, self, _from, self.network)
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


class i_network(ABC):
    def __init__(self, client):
        self.client = client

    @abstractmethod
    def connect(self, server: server_token) -> bool:
        pass

    @abstractmethod
    def is_connected(self, server: server_token):
        pass

    @abstractmethod
    def send(self, server: server_token, _msg: msg, jobj: Dict):
        pass

    @abstractmethod
    def new_channel(self, channel_name: str) -> i_channel:
        pass

    @abstractmethod
    def get_channel(self, name: str) -> i_channel:
        pass

    @property
    @abstractmethod
    def connected_servers(self) -> List[server_token]:
        pass


class network(i_network):

    def is_connected(self, server: server_token):
        return server in self.sockets

    @property
    def connected_servers(self) -> List[server_token]:
        return list(self.sockets.keys())

    def __init__(self, client):
        super().__init__(client)
        self.sockets: Dict[server_token, Tuple[socket, Thread]] = {}
        self.channels: Dict[str, channel] = {}
        self._on_msg_pre_analyzed = event()
        self._lock = RLock()
        self._max_retry_time = 3

    @property
    def max_retry_time(self) -> int:
        return self._max_retry_time

    @max_retry_time.setter
    def max_retry_time(self, value: int):
        self._max_retry_time = max(1, int(value))

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

    def connect(self, server: server_token) -> bool:
        skt = socket(AF_INET, SOCK_STREAM)
        succeed = False
        for i in range(self.max_retry_time):
            try:
                self.logger.msg(f"Trying to connect {server} [{i + 1}]...")
                skt.connect(server)
                succeed = True
                break
            except:
                continue
        if not succeed:
            self.logger.error(f"Cannot connect {server}")
            return False
        listen = Thread(target=self.__receive_datapack, args=(server, skt))
        listen.daemon = True
        self.lock(self._add_socket)(server, skt, listen)
        listen.start()
        return True

    def _add_socket(self, server: server_token, skt: socket, listen: Thread) -> None:
        self.sockets[server] = (skt, listen)

    def _del_socket(self, server: server_token) -> bool:
        if server in self.sockets:
            del self.sockets[server]
            return True
        else:
            return False

    def init(self, container):
        self.logger: outputs.i_logger = container.resolve(outputs.i_logger)

    def __receive_datapack(self, token: server_token, server_socket):
        while True:
            try:
                _datapack: datapack = read_one(server_socket)
            except:
                break
            json_text = converts.read_str(_datapack.data)
            _json = json.loads(json_text)
            self.on_msg_pre_analyzed(self, token, json_text, _json)
            self.__analyse(_json, token)

    def disconnect(self, server: server_token):
        if server in self.sockets:
            sk, t = self.sockets[server]
            sk.close()
            self.lock(self._del_socket)(server)

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

    def lock(self, func):
        @wraps(func)
        def inner(*args, **kwargs):
            self._lock.acquire()
            res = func(*args, **kwargs)
            self._lock.release()
            return res

        return inner


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
