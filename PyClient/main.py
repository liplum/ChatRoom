from core.event import event
from core.ioc import container
from ui.client import client
from ui import output
from socket import socket, AF_INET, SOCK_STREAM
import sys
import threading
from threading import Lock, Thread
import time
import os
from ui.client import client

_client = client()

def main():
    _client.on_service_register.add(init_plugin)
    _client.on_command_register.add(add_commands)
    _client.init()
    _client.start()


def init_plugin(registry: container):
    pass

def add_commands(cmd_list):
    pass


if __name__ == '__main__':
    main()
