import json
import socket as s
import traceback
from abc import ABC, abstractmethod, ABCMeta
from collections import namedtuple
from functools import wraps
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread, RLock
from typing import Dict, Tuple, Callable, List, Optional

from Events import Event
from core import converts
from core.shared import server_token
from ui import outputs
from utils import get, not_none

msg_name2type: Dict[str, type] = {}
msg_type2name: Dict[type, str] = {}


def _add_msgtype(name: str, msgtype: "metamsg"):
    msg_name2type[name] = msgtype
    msg_type2name[msgtype] = name


class metamsg(ABCMeta):
    def __init__(cls, name, bases, dic):
        super().__init__(name, bases, dic)
        if hasattr(cls, "name"):
            n = cls.name
        else:
            n = name
        _add_msgtype(n, cls)


class msg(metaclass=metamsg):
    @abstractmethod
    def read(self, json):
        pass

    @abstractmethod
    def write(self, json):
        pass


Context = namedtuple("Context", ["client", "channel", "token", "network"])
MsgHandler = Callable[[msg, Context], None]


class ichannel:
    def __init__(self, name):
        self.name = name
        self._on_msg_received = Event(ichannel, msg, Callable, cancelable=True)

    @property
    def on_msg_received(self) -> Event:
        """
        Para 1:ichannel object

        Para 2:msg object

        Para 2:the msg's corresponding handler (if it doesn't have,provide null)

        Cancelable:If yes,it will stop any more handle on this msg

        :return: Event(ichannel,msg,MsgHandler)
        """
        return self._on_msg_received

    def register(self, msg_type: type, msg_id: str = None, msg_handler=None):
        pass

    def receive_datapack(self, _json: Dict, msg_id: str, _from: server_token):
        pass

    def send(self, to: server_token, msg):
        pass


class channel(ichannel):
    def __init__(self, network: "inetwork", name):
        super().__init__(name)
        self.network = network
        self.logger: outputs.ilogger = network.logger
        self.client = network.client
        self.id2msg_and_handler: Dict[str, Tuple[type, Optional[MsgHandler]]] = {}
        self.msg2id: Dict[type, str] = {}

    def register(self, msg_type: type, msg_id: str = None, msg_handler: Optional[MsgHandler] = None):
        if msg_id is None:
            msg_id = msg_type.name

        if msg_handler is None:
            if hasattr(msg_type, "handle"):
                msg_handler = msg_type.handle
            else:
                msg_handler = None

        self.id2msg_and_handler[msg_id] = (msg_type, msg_handler)
        self.msg2id[msg_type] = msg_id

    def receive_datapack(self, _json: Dict, msg_id: str, _from: server_token):
        info = get(self.id2msg_and_handler, msg_id)
        if info is not None:
            msgtype, handler = info
            msg = msgtype()
            msg.read(_json)
            if not self.on_msg_received(self, msg, handler):
                if handler is not None:
                    context = Context(self.client, self, _from, self.network)
                    self.client.add_task(lambda: handler(msg, context))
        else:
            self.logger.error(f"[Channel<{self.name}>]Cannot find message type called {msg_id}")

    def send(self, to: server_token, msg):
        msg_id = get(self.msg2id, type(msg))
        if msg_id is not None:
            jobj = {
                "ChannelName": self.name,
                "MessageID": msg_id
            }
            self.network.send(to, msg, jobj)
        else:
            self.logger.error(f"[Channel<{self.name}>]Cannot find message type {msg_id}")


class inetwork(ABC):
    def __init__(self, client):
        self.client = client
        self._on_connected = Event(inetwork, server_token)
        self._on_disconnected = Event(inetwork, server_token)

    @property
    def on_connected(self) -> Event:
        """
        Para 1:inetwork object

        Para 2:server info

        :return: Event(inetwork,server_token)
        """
        return self._on_connected

    @property
    def on_disconnected(self) -> Event:
        """
        Para 1:inetwork object

        Para 2:server info

        :return: Event(inetwork,server_token)
        """
        return self._on_disconnected

    @abstractmethod
    def connect(self, server: server_token, strict: bool = False) -> bool:
        """

        :param server:
        :param strict:
        :return:
        :exception: CannotConnectError only strict mode
        """
        pass

    @abstractmethod
    def connectAsync(self, server: server_token, callback: Callable[[], None], strict: bool = False) -> bool:
        """

        :param server:
        :param callback:
        :param strict:
        :return:
        :exception: CannotConnectError only strict mode
        """
        pass

    @abstractmethod
    def is_connected(self, server: server_token):
        pass

    @abstractmethod
    def send(self, server: server_token, _msg: msg, jobj: Dict):
        pass

    @abstractmethod
    def new_channel(self, channel_name: str) -> ichannel:
        pass

    @abstractmethod
    def get_channel(self, name: str) -> ichannel:
        pass

    @property
    @abstractmethod
    def connected_servers(self) -> List[server_token]:
        pass

    def auto_register(self):
        pass


class ChannelNotFoundError(Exception):

    def __init__(self, channel_name: str):
        super().__init__()
        self.channel_name = channel_name


class CannotConnectError(Exception):
    def __init__(self, server: server_token):
        super().__init__()
        self.server = server


class network(inetwork):

    def is_connected(self, server: server_token):
        return server in self.sockets

    @property
    def connected_servers(self) -> List[server_token]:
        with self._lock:
            return list(self.sockets.keys())

    def __init__(self, client):
        super().__init__(client)
        self.sockets: Dict[server_token, Tuple[socket, Thread]] = {}
        self.channels: Dict[str, channel] = {}
        self._on_msg_pre_analyzed = Event(network, server_token, str, dict)
        self._lock = RLock()
        self._max_retry_time = 3

    @property
    def max_retry_time(self) -> int:
        return self._max_retry_time

    @max_retry_time.setter
    def max_retry_time(self, value: int):
        self._max_retry_time = max(1, int(value))

    @property
    def on_msg_pre_analyzed(self) -> Event:
        """
        Para 1:network object

        Para 2:server token

        Para 3:source json text

        Para 4:json dictionary

        :return: Event(network,server_token,str,dict)
        """
        return self._on_msg_pre_analyzed

    def get_channel(self, name: str):
        if name in self.channels:
            return self.channels[name]
        else:
            raise ChannelNotFoundError(name)

    def connect(self, server: server_token, strict: bool = False) -> bool:
        if server in self.sockets.keys():
            return True
        skt = socket(AF_INET, SOCK_STREAM)
        skt.settimeout(5)
        succeed = False
        for i in range(self.max_retry_time):
            try:
                self.logger.msg(f"[Network]Trying to connect {server} [{i + 1}]...")
                ip = s.gethostbyname(server.ip)
                token = ip, server.port
                skt.connect(token)
                succeed = True
                break
            except:
                continue
        if not succeed:
            if strict:
                raise CannotConnectError(server)
            else:
                self.logger.error(f"[Network]Cannot connect {server}")
                return False
        skt.settimeout(None)
        listen = Thread(target=self.__receive_datapack, args=(server, skt), name=str(token))
        listen.daemon = True
        self.lock(self._add_socket)(server, skt, listen)
        listen.start()
        self.on_connected(self, server)
        return True

    def connectAsync(self, server: server_token, callback: Callable[[], None], strict: bool = False) -> bool:
        pass

    def _add_socket(self, server: server_token, skt: socket, listen: Thread) -> None:
        self.sockets[server] = (skt, listen)

    def _del_socket(self, server: server_token) -> bool:
        if server in self.sockets:
            del self.sockets[server]
            return True
        else:
            return False

    def init(self, container):
        self.logger: outputs.ilogger = container.resolve(outputs.ilogger)

    def __receive_datapack(self, token: server_token, server_socket):
        while True:
            try:
                _datapack: datapack = read_one(server_socket)
            except:
                self.logger.error(f"[Network]Can't receive data from {token} because \n{traceback.format_exc()}")
                self.logger.tip("Maybe it occurred because of disconnection.")
                break
            json_text = converts.read_str(_datapack.data)
            _json = json.loads(json_text)
            self.on_msg_pre_analyzed(self, token, json_text, _json)
            self.__analyse(_json, token)
        self.disconnect(token)

    def disconnect(self, server: server_token):
        if server in self.sockets:
            sk, t = self.sockets[server]
            sk.close()
            self.lock(self._del_socket)(server)
            self.on_connected(self, server)

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
                self.logger.error(f"[Network]Cannot find channel called {channel_name}")
        else:
            self.logger.error("[Network]Cannot analyse datapack")

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
            self.logger.error(f"[Network]Cannot find server {server}")

    def new_channel(self, channel_name: str) -> channel:
        c = channel(self, channel_name)
        self.channels[channel_name] = c
        return c

    def auto_register(self):
        for name, channel in self.channels.items():
            for msgtype in msg_type2name.keys():
                if hasattr(msgtype, "channel") and msgtype.channel == name:
                    channel.register(msgtype)

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
