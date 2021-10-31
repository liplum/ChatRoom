from core.events import event
from core.ioc import container
from ui.clients import client, cmdkey
from ui import outputs
from socket import socket, AF_INET, SOCK_STREAM
import sys
import threading
from threading import Lock, Thread
import time
import os
from ui.clients import client
from core.chats import msgstorage
import platform
from ui.inputs import i_nbinput, i_input
from ui import inputs
from chars import *
from linuxchars import *
import sys
import utils
import keys

DEBUG = False
args = sys.argv
if utils.get_at(args, 1) == "debug":
    DEBUG = True

system_type = platform.system()

_client = client()


def main():
    _client.on_service_register.add(init_plugin)
    _client.on_command_register.add(add_commands)
    _client.on_keymapping.add(mapkeys)
    _client.init()
    st = msgstorage("record.rec")
    st.deserialize()
    _client.win.history = [unit[2] for unit in st]
    # _client.connect(("127.0.0.1", 5000))
    _client.start()


def init_plugin(client, registry: container):
    if system_type == "Windows":
        from ui import nonblocks
        registry.register_singleton(i_input, nonblocks.nbinput)
    elif system_type == "Linux":
        from ui import linux
        registry.register_singleton(i_input, linux.nbinput)

    if DEBUG:
        from ui.inputs import cmd_input
        registry.register_singleton(i_input, cmd_input)


def mapkeys(client, keymap: cmdkey):
    if keymap is client.key_enter_text:
        keymap.map(c_t)
        return
    elif keymap is client.key_quit_text_mode:
        keymap.map(keys.k_quit)

    """if system_type == "Windows":
        if keymap is client.key_quit_text_mode:
            keymap.map(c_esc)
            return
    elif system_type == "Linux":
        if keymap is client.key_quit_text_mode:
            keymap.map(linux_eot)
            return"""


def add_commands(cmd_list):
    pass


if __name__ == '__main__':
    main()
