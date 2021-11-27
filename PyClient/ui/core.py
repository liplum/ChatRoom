from abc import abstractmethod, ABC
from threading import RLock
from typing import Union, Type, NoReturn, Any, Optional

from ui.shared import *


class iclient(ABC):
    def __init__(self):
        self._on_service_register = event()
        self._on_cmd_register = event()
        self._on_keymapping = event()

    @property
    @abstractmethod
    def win(self) -> "iwindow":
        raise NotImplementedError()

    @property
    def on_service_register(self) -> event:
        """
        Para 1:client object


        Para 2:container

        :return: event(client,container)
        """
        return self._on_service_register

    @property
    def on_cmd_register(self) -> event:
        """
        Para 1:the manager of cmd

        :return: event(client,cmdmanager)
        """
        return self._on_cmd_register

    @property
    def on_keymapping(self) -> event:
        """
        Para 1: client object


        Para 1: key map

        :return: event(client,cmdkey)
        """
        return self._on_keymapping

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def connect(self, ip: str, port: int):
        pass

    @abstractmethod
    def mark_dirty(self):
        pass

    @abstractmethod
    def init(self) -> None:
        pass

    @property
    @abstractmethod
    def container(self) -> "container":
        raise NotImplementedError()

    @property
    @abstractmethod
    def network(self) -> "inetwork":
        raise NotImplementedError()

    @property
    @abstractmethod
    def logger(self) -> "ilogger":
        raise NotImplementedError()

    @property
    @abstractmethod
    def displayer(self) -> "idisplay":
        raise NotImplementedError()

    @property
    @abstractmethod
    def msg_manager(self) -> "imsgmager":
        raise NotImplementedError()

    @property
    @abstractmethod
    def display_lock(self) -> RLock:
        raise NotImplementedError()


class iwindow(inputable, reloadable):
    def __init__(self, client: iclient):
        self.client = client
        self.displayer = self.client.displayer

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def newtab(self, tabtype: Union[Type[T], str]) -> T:
        pass

    @abstractmethod
    def new_chat_tab(self) -> "chat_tab":
        pass

    @abstractmethod
    def update_screen(self):
        pass

    @abstractmethod
    def gen_default_tab(self):
        pass

    @abstractmethod
    def popup(self, popup: "base_popup") -> NoReturn:
        pass

    @abstractmethod
    def retrieve_popup(self, popup: "base_popup") -> Optional[Any]:
        pass

    @property
    @abstractmethod
    def tablist(self) -> "tablist":
        pass
