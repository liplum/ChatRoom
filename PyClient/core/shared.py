from collections import namedtuple
from datetime import datetime
from typing import Tuple, List, Optional

server_token = namedtuple("server_token", ["ip", "port"])

userid = str

roomid = int

sr_info = namedtuple("sr_info", ["server", "room_id"])

StorageUnit = Tuple[datetime, userid, str]

default_port = 25000


class chat_room:
    def __init__(self, info: sr_info):
        self.info = info
        self.members: List[userid] = []


class uentity:
    def __init__(self, server: server_token, uid: userid, vcode: Optional[int] = None):
        self.uid = uid
        self.server = server
        self.vcode: Optional[int] = vcode

    @property
    def verified(self) -> bool:
        return self.vcode is not None

    def __hash__(self):
        return hash((self.server, self.uid, self.vcode))

    def __eq__(self, other):
        if isinstance(other, uentity):
            return self.server == other.server and self.uid == other.uid and self.vcode == other.vcode
        return False


def to_server_token(full: str) -> Optional[server_token]:
    server_info = full.split(":")
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
