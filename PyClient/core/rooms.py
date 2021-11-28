from abc import abstractmethod, ABC
from typing import Dict, Set, Callable

from core.shared import *
from net.networks import inetwork

IsNewRoom = bool


class iroom_manager(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def all_rooms(self, server: server_token) -> List[chat_room]:
        raise NotImplemented()

    @abstractmethod
    def add_room(self, server: server_token, room: chat_room) -> IsNewRoom:
        raise NotImplemented()

    @abstractmethod
    def find_room(self, server: server_token, predicate: Callable[[chat_room], bool]) -> Optional[chat_room]:
        raise NotImplemented()

    @abstractmethod
    def find_room_by_id(self, server: server_token, room_id: roomid) -> Optional[chat_room]:
        raise NotImplemented()


class room_manager(iroom_manager):

    def __init__(self):
        super().__init__()
        self.rooms: Dict[server_token, Set[chat_room]] = {}

    def init(self, container):
        self.network: inetwork = container.resolve(inetwork)
        self.network.on_connected.add(self.on_connect_new_server)
        self.network.on_disconnected.add(self.on_disconnect)

    def on_connect_new_server(self, network, server: server_token):
        self.rooms[server] = set()

    def on_disconnect(self, network, server: server_token):
        if server in self.rooms:
            del self.rooms[server]

    def all_rooms(self, server: server_token) -> Set[chat_room]:
        if server in self.rooms:
            return self.rooms[server]
        else:
            return set()

    def add_room(self, server: server_token, room: chat_room) -> IsNewRoom:
        if server not in self.rooms:
            self.rooms[server] = {room}
            return True
        else:
            rooms = self.rooms[server]
            if room not in rooms:
                rooms.add(room)
                return True
            else:
                return False

    def find_room(self, server: server_token, predicate: Callable[[chat_room], bool]) -> Optional[chat_room]:
        if server not in self.rooms:
            return None
        else:
            rooms = self.rooms[server]
            for r in rooms:
                if predicate(r):
                    return r

    def find_room_by_id(self, server: server_token, room_id: roomid) -> Optional[chat_room]:
        if server not in self.rooms:
            return None
        else:
            rooms = self.rooms[server]
            for r in rooms:
                if r.info.room_id == room_id:
                    return r
