from collections import namedtuple
from datetime import datetime
from typing import Tuple, List, Optional

server_token = namedtuple("server_token", ["ip", "port"])

userid = str

roomid = int

sr_info = namedtuple("sr_info", ["server", "room_id"])

StorageUnit = Tuple[datetime, userid, str]

default_port = 25000

member = namedtuple("member", ["account", "nick_name"])


class chat_room:
    def __init__(self, info: sr_info, name: str):
        self.info = info
        self.name = name
        self.members: List[member] = []

    def __hash__(self):
        return hash(self.info)

    def __eq__(self, other):
        if isinstance(other, chat_room):
            return self.info == other.info
        return False

    def __repr__(self) -> str:
        info = self.info
        return f"chat_room({repr(self.info)},\"{self.name}\")"


class uentity:
    def __init__(self, server: server_token, account: userid, vcode: Optional[int] = None):
        self.account = account
        self.server = server
        self.vcode: Optional[int] = vcode

    @property
    def verified(self) -> bool:
        return self.vcode is not None

    def __hash__(self):
        return hash((self.server, self.account, self.vcode))

    def __eq__(self, other):
        if isinstance(other, uentity):
            return self.server == other.server and self.account == other.account and self.vcode == other.vcode
        return False


def to_server_token(full: Optional[str]) -> Optional[server_token]:
    if full is None or full == "":
        return None
    try:
        server_info = full.split(":")
    except:
        return None
    argslen = len(server_info)
    if argslen == 1:
        return server_token(server_info[0], default_port)
    elif argslen == 2:
        try:
            port = int(server_info[1])
        except:
            return None
        ip = server_info[0]
        return server_token(ip, port)
    else:
        return None


def token_to_str(self: server_token) -> str:
    return f"{self.ip}:{self.port}"


server_token.by = to_server_token
server_token.__str__ = token_to_str
server_token.__repr__ = token_to_str
