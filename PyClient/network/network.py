from abc import ABC, abstractmethod


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


class network:
    def connect(self, ip):
        pass

    def send(self):
        pass

    def receive(self):
        pass


class datapack:
    pass
