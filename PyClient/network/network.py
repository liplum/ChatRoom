from abc import ABC, abstractmethod

from typing import Dict, Tuple


class msg(ABC):
    @abstractmethod
    def read(self, json):
        pass

    @abstractmethod
    def write(self, json):
        pass


class channel:
    def __init__(self, name):
        self.name = name
        self.id2msg_and_handler: Dict[str, Tuple[type, function]] = {}
        self.msg2id: Dict[type, str] = {}

    def register(self, msg_type: type, **kwargs):
        if "msg_id" in kwargs:
            msg_id = kwargs["msg_type"]
        else:
            msg_id = msg_type.MessageID

        if "msg_handler" in kwargs:
            msg_handler = kwargs["msg_type"]
        elif hasattr(msg_type, "handle"):
            msg_handler = msg_type.handle
        else:
            msg_handler = None

        self.id2msg_and_handler[msg_id] = (msg_type, msg_handler)
        self.msg2id[msg_type] = msg_id

    def receive_datapack(self, datapack):
        pass


class network:
    def connect(self, ip):
        pass

    def send(self):
        pass

    def receive(self):
        pass


class datapack:
    pass
