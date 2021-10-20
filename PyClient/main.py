from core.event import event
from core.ioc import container
from ui.client import| client
from ui import output
from socket import socket, AF_INET, SOCK_STREAM
import sys
import threading
from threading import Lock, Thread
import time
import os
from ui.client import client
import platform
from ui.input import i_nbinput

system_type=platform.system()
if system_type == "Linux":
    pass
elif system_type=="Winodws":
    from ui.nbinput import nbinput

_client = client()

def main():
    _client.on_service_register.add(init_plugin)
    _client.on_command_register.add(add_commands)
    _client.init()
    _client.start()


def init_plugin(registry: container):
    if system_type=="Windows":
        registry.register_singleton(i_nbinput,nbinput)

def add_commands(cmd_list):
    pass


if __name__ == '__main__':
    main()
