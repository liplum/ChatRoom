import os
from datetime import datetime
from threading import RLock
from typing import Tuple, List, Dict, Optional

import utils
from core.shared import server_token, userid, roomid, StorageUnit
from events import event
from core.filer import i_filer
from ui.outputs import i_logger
from utils import compose, separate


class chatting_room:
    def __init__(self, _id: roomid):
        self.id = _id
        self._history = msgstorage(f"records\\{self.id}.rec")

    @property
    def history(self) -> "msgstorage":
        return self._history


class msgstorage:
    def __init__(self, save_file: str = None):
        self._save_file = save_file
        self.__storage: List[StorageUnit] = []
        self._on_stored = event()
        self.changed = False

    def store(self, msg_unit: StorageUnit):
        self.__storage.append(msg_unit)
        self.changed = True

    @property
    def on_stored(self) -> event:
        """
        Para 1:msgstorage object

        Para 2:storage unit

        :return: event(msgstorage,StorageUnit)
        """
        return self._on_stored

    def sort(self):
        if self.changed:
            self.__storage.sort(key=lambda i: i[0])
            self.changed = False

    def __iter__(self) -> [StorageUnit]:
        return iter(self.__storage[:])

    @property
    def save_file(self) -> str:
        return self._save_file

    @save_file.setter
    def save_file(self, value):
        self._save_file = value
        if not os.path.exists(value):
            with open(value, "w"):
                pass

    def serialize(self):
        if not self._save_file:
            raise ValueError("You should provide a save file path first.")
        self.sort()
        with open(self._save_file, "w") as save:
            for unit in self.__storage:
                unit_str = (str(unit[0]), str(unit[1]), unit[2])
                saved_line = compose(unit_str, '|', end='\n')
                save.write(saved_line)

    def deserialize(self):
        if not self._save_file:
            raise ValueError("You should provide a save file path first.")
        self.__storage = []
        with open(self._save_file, "r") as save:
            lines = save.readlines()
            for line in lines:
                line = line.rstrip()
                items = separate(line, '|', 2, allow_emptychar=False)
                if len(items) == 3:
                    time, uid, content = items
                    try:
                        time = datetime.fromisoformat(time)
                        uid = userid(uid)
                        self.__storage.append((time, uid, content))
                    except:
                        continue
                else:
                    continue
        self.sort()

    def retrieve(self, start: datetime, end: datetime, number_limit: Optional[int] = None,
                 reverse: bool = False) -> List[StorageUnit]:
        """

        :param start:the beginning time of message retrieval.
        :param end:the ending time of message retrieval.
        :param number_limit:the max number of message retrieval.If None,retrieves all.
        :param reverse:If true,retrieves msg starting from end datetime.Otherwise starting from start datetime.
        :return:
        """
        if len(self.__storage) == 0:
            return []

        start = min(start, end)
        end = max(start, end)

        snapshot = self.__storage[:]
        dt_snapshot = [unit[0] for unit in snapshot]
        _, start_pos = utils.find_range(dt_snapshot, start)
        end_pos, _ = utils.find_range(dt_snapshot, end)

        order = -1 if reverse else 1
        if number_limit:
            if number_limit >= len(snapshot):
                if reverse:
                    return snapshot[::order]
                else:
                    return snapshot
            return inrange[start_pos:end_pos + 1 - number_limit:order]
        else:
            return snapshot[start_pos:end_pos + 1:order]

    def retrieve_lasted(self, number_limit: int) -> List[StorageUnit]:
        """

        :param number_limit:the max number of message retrieval.
        :return:
        """
        if len(self.__storage) == 0:
            return []

        snapshot = self.__storage[:]
        if number_limit >= len(snapshot):
            return snapshot
        return snapshot[-number_limit:]

    def retrieve_until(self, end: datetime, number_limit: Optional[int] = None) -> List[StorageUnit]:
        if len(self.__storage) == 0:
            return []

        snapshot = self.__storage[:]
        dt_snapshot = [unit[0] for unit in snapshot]
        end_pos, _ = utils.find_range(dt_snapshot, end)
        if number_limit:
            if number_limit >= len(snapshot):
                return snapshot[:end_pos + 1]
            else:
                start_pos = max(end_pos - number_limit, 0)
                return snapshot[start_pos:end_pos + 1]
        else:
            return snapshot[:end_pos + 1]


class i_msgmager:
    def load_lasted(self, server: server_token, room_id: roomid,
                    amount: int) -> List[StorageUnit]:
        pass

    def retrieve(self, server: server_token, room_id: roomid, amount: int, start: datetime,
                 end: datetime) -> List[StorageUnit]:
        pass

    def receive(self, server: server_token, room_id: roomid, msg_unit: StorageUnit):
        pass

    def load_until_today(self, server: server_token, room_id: roomid,
                         amount: int) -> List[StorageUnit]:
        pass

    def save_all(self):
        pass

    @property
    def on_received(self) -> event:
        """
        Para 1:i_msgmager object

        Para 2:server

        Para 3:room id

        Para 4:storage unit

        :return: event(i_msgmager,server_token,roomid,StorageUnit)
        """
        return event()


class i_msgfiler:
    def save(self, server: server_token, room_id: roomid, storage: msgstorage):
        pass

    def get(self, server: server_token, room_id: roomid) -> str:
        pass


class msgfiler(i_msgfiler):

    def init(self, container):
        self.logger: i_logger = container.resolve(i_logger)
        self.filer: i_filer = container.resolve(i_filer)

    def __init__(self):
        pass

    def save(self, server: server_token, room_id: roomid, storage: msgstorage):
        try:
            file = self.filer.get_file(f"/data/{server.ip}-{server.port}/{room_id}.rec")
            storage.save_file = file
            storage.serialize()
        except:
            self.logger.error(f'Cannot save msg into "{storage.save_file}"')

    def get(self, server: server_token, room_id: roomid) -> str:
        return self.filer.get_file(f"/data/{server.ip}-{server.port}/{room_id}.rec")


class msgmager(i_msgmager):
    def __init__(self):
        self.cache: Dict[Tuple[server_token, roomid], msgstorage] = {}
        self._lock = RLock()
        self._on_received = event()

    def init(self, container):
        self.filer: i_msgfiler = container.resolve(i_msgfiler)
        self.logger: i_logger = container.resolve(i_logger)

    def get_storage(self, server: server_token, room_id: roomid) -> Optional[msgstorage]:
        if (server, room_id) in self.cache:
            return self.cache[server, room_id]
        else:
            msgs_file = self.filer.get(server, room_id)
            if msgs_file:
                storage = msgstorage(msgs_file)
                storage.deserialize()
                self.cache[server, room_id] = storage
                return storage
            else:
                return None

    def load_lasted(self, server: server_token, room_id: roomid, amount: int) -> List[StorageUnit]:
        with self._lock:
            storage = self.get_storage(server, room_id)
            if storage:
                return storage.retrieve_lasted(amount)
            else:
                self.logger.error(f"Cannot load msg storage from {room_id}")

    def retrieve(self, server: server_token, room_id: roomid, amount: int, start: datetime,
                 end: datetime) -> List[StorageUnit]:
        with self._lock:
            storage = self.get_storage(server, room_id)
            if storage:
                return storage.retrieve(start=start, end=end, number_limit=amount)
            else:
                self.logger.error(f"Cannot load msg storage from {room_id}")

    def receive(self, server: server_token, room_id: roomid, msg_unit: StorageUnit):
        with self._lock:
            if (server, room_id) in self.cache:
                storage = self.cache[server, room_id]
            else:
                msgs_file = self.filer.get(server, room_id)
                storage = msgstorage(msgs_file)
                self.cache[server, room_id] = storage
            storage.store(msg_unit)
        self.on_received(self, server, room_id, msg_unit)

    def load_until_today(self, server: server_token, room_id: roomid, amount: int) -> List[StorageUnit]:
        with self._lock:
            storage = self.get_storage(server, room_id)
            if storage:
                return storage.retrieve_until(end=datetime.now(), number_limit=amount)
            else:
                self.logger.error(f"Cannot load msg storage from {room_id}")

    def save_all(self):
        for strg in self.cache.values():
            strg.serialize()

    @property
    def on_received(self) -> event:
        return self._on_received
