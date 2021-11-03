import os
from datetime import datetime
from typing import Tuple, List, Union, Any

import utils
from utils import compose, separate


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

    def store(self, timestamp: datetime, userid_: Union[userid, Any], msg: str):
        if not isinstance(userid_, userid):
            userid_ = userid(userid_)
        self.__storage.append((timestamp, userid_, msg))
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

    def retrieve(self, start: datetime, end: datetime, number_limit: int = None,
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
        dt_snapshot = [unit[0] for unit in self.__storage]
        _, start_pos = utils.find_range(dt_snapshot, start)
        end_pos, _ = utils.find_range(dt_snapshot, end)
        if reverse:
            inrange = snapshot[start_pos:end_pos:-1]
        else:
            inrange = snapshot[start_pos:end_pos]
        if number_limit is None:
            return inrange
        else:
            return inrange[number_limit:]
