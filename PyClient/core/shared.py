from collections import namedtuple
from datetime import datetime
from typing import Tuple, List, Optional

server_token = namedtuple("server_token", ["ip", "port"])

userid = str

roomid = int

sr_info = namedtuple("sr_info", ["server", "room_id"])

StorageUnit = Tuple[datetime, userid, str]


class chat_room:
    def __init__(self, info: sr_info):
        self.info = info
        self.members: List[userid] = []


class uentity:
    def __init__(self, server: server_token, uid: userid):
        self.uid = uid
        self.server = server
        self.vcode: Optional[int] = None

    @property
    def verified(self) -> bool:
        return self.vcode is not None

    def __hash__(self):
        return hash((self.server, self.uid, self.vcode))


def to_server_token(full: str) -> Optional[server_token]:
    server_info = full.split(":")
    if len(server_info) != 2:
        return None
    try:
        port = int(server_info[1])
    except:
        return None
    ip = server_info[0]
    return server_token(ip, port)
