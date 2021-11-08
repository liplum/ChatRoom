import os
from datetime import datetime
from threading import RLock
from typing import Tuple, List, Dict, Optional

from core import utils
from core.utils import compose, separate
from ui.outputs import i_logger


class userid:
    def __init__(self, userid: str):
        self.userid = userid

    def __eq__(self, other):
        if isinstance(other, str):
            return self.userid == other
        elif isinstance(other, userid):
            return self.userid == other.userid
        return False

    def __hash__(self):
        return hash(self.userid)

    def __str__(self) -> str:
        return self.userid

    def __repr__(self):
        return self.userid


class roomid:
    def __init__(self, _id: int):
        self.id = _id

    def __eq__(self, other):
        if isinstance(other, int):
            return self.id == other
        elif isinstance(other, roomid):
            return self.id == other.id
        return False

    def __hash__(self):
        return hash(self.id)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self):
        return self.id


class chatting_room:
    def __init__(self, _id: roomid):
        self.id = _id
        self._history = msgstorage(f"records\\{self.id}.rec")

    @property
    def history(self) -> "msgstorage":
        return self._history


StorageUnit = Tuple[datetime, userid, str]


class msgstorage:
    def __init__(self, save_file: str = None):
        self._save_file = save_file
        self.__storage: List[StorageUnit] = []
        self.changed = False

    def store(self, msg_unit: StorageUnit):
        self.__storage.append(msg_unit)
        self.changed = True

    def sort(self):
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
                items = separate(line, '|', 2, False)
                if len(items) == 3:
                    time, uid, content = items
                    time = datetime.fromisoformat(time)
                    uid = userid(uid)
                    self.__storage.append((time, uid, content))
                else:
                    continue

    def retrieve(self, start: datetime, end: datetime, number_limit: Optional[int] = None,
                 reverse: bool = False) -> List[StorageUnit]:
        """

        :param start:the beginning time of message retrieval.
        :param end:the ending time of message retrieval.
        :param number_limit:the max number of message retrieval.If None,retrieves all.
        :param reverse:If true,retrieves msg starting from end datetime.Otherwise starting from start datetime.
        :return:
        """
        start = min(start, end)
        end = max(start, end)

        if self.changed:
            self.sort()
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

        if self.changed:
            self.sort()
        snapshot = self.__storage[:]
        if number_limit >= len(snapshot):
            return snapshot
        return snapshot[-number_limit:]

    def retrieve_until(self, end: datetime, number_limit: Optional[int] = None):
        if self.changed:
            self.sort()
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
    def load_lasted(self, room_id: roomid, amount: int) -> List[StorageUnit]:
        pass

    def retrieve(self, room_id: roomid, amount: int, start: datetime, end: datetime) -> List[StorageUnit]:
        pass

    def receive(self, room_id: roomid, msg_unit: StorageUnit):
        pass

    def load_until_today(self, room_id: roomid, amount: int) -> List[StorageUnit]:
        pass


class i_msgfiler:
    def save(self, room_id: roomid, storage: msgstorage):
        pass

    def get(self, room_id: roomid) -> Optional[str]:
        pass


class msgfiler(i_msgfiler):

    def init(self, container):
        self.logger: i_logger = container.resolve(i_logger)

    def __init__(self, msg_storages_dir: Optional[str] = None):
        self.msg_storages_dir = msg_storages_dir

    def save(self, room_id: roomid, storage: msgstorage):
        if self.msg_storages_dir:
            try:
                file = f"{self.msg_storages_dir}/{room_id}.rec"
                if storage.save_file == file:
                    if not os.path.exists(self.msg_storages_dir):
                        os.makedirs(self.msg_storages_dir)
                storage.serialize()
            except:
                self.logger.error(f'Cannot save msg into "{storage.save_file}"')

    def get(self, room_id: roomid) -> Optional[str]:
        if self.msg_storages_dir:
            file = f"{self.msg_storages_dir}/{room_id}.rec"
            if os.path.exists(file):
                return file
            else:
                if not os.path.exists(self.msg_storages_dir):
                    os.makedirs(self.msg_storages_dir)
                with open(file, "w"):
                    pass
                return file
        else:
            return None


class msgmager(i_msgmager):
    def __init__(self):
        self.cache: Dict[roomid, msgstorage] = {}
        self._lock = RLock()

    def init(self, container):
        self.filer: i_msgfiler = container.resolve(i_msgfiler)
        self.logger: i_logger = container.resolve(i_logger)

    def get_storage(self, room_id: roomid) -> Optional[msgstorage]:
        if room_id in self.cache:
            return self.cache[room_id]
        else:
            msgs_file = self.filer.get(room_id)
            if msgs_file:
                storage = msgstorage(msgs_file)
                storage.deserialize()
                self.cache[room_id] = storage
                return storage
            else:
                return None

    def load_lasted(self, room_id: roomid, amount: int) -> List[StorageUnit]:
        with self._lock:
            storage = self.get_storage(room_id)
            if storage:
                return storage.retrieve_lasted(amount)
            else:
                self.logger.error(f"Cannot load msg storage from {room_id}")

    def retrieve(self, room_id: roomid, amount: int, start: datetime, end: datetime) -> List[StorageUnit]:
        with self._lock:
            storage = self.get_storage(room_id)
            if storage:
                return storage.retrieve(start=start, end=end, number_limit=amount)
            else:
                self.logger.error(f"Cannot load msg storage from {room_id}")

    def receive(self, room_id: roomid, msg_unit: StorageUnit):
        with self._lock:
            if room_id in self.cache:
                storage = self.cache[room_id]
            else:
                msgs_file = self.filer.get(room_id)
                storage = msgstorage(msgs_file)
            storage.store(msg_unit)

    def load_until_today(self, room_id: roomid, amount: int) -> List[StorageUnit]:
        with self._lock:
            storage = self.get_storage(room_id)
            if storage:
                return storage.retrieve_until(end=datetime.now(), number_limit=amount)
            else:
                self.logger.error(f"Cannot load msg storage from {room_id}")
