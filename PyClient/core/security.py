from abc import ABC, abstractmethod
from typing import Dict

from core.shared import *

AP = Tuple[str, str]


class ipwd_manager(ABC):
    @abstractmethod
    def add_entry(self, server: server_token, account: userid, password: str):
        pass

    @abstractmethod
    def loads(self):
        pass

    @abstractmethod
    def save(self):
        pass


class paw_manager(ipwd_manager):

    def __init__(self):
        self.pwds: Dict[server_token, AP] = {}

    def save(self):
        pass

    def loads(self):
        pass

    def add_entry(self, server: server_token, account: userid, password: str):
        pass
