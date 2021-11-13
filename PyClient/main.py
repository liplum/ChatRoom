import platform
import sys

import keys
from chars import *
from cmd import cmdmanager
import utils
from core.ioc import container
from utils import get_at
from ui.clients import client
from ui.inputs import i_input
from ui.k import cmdkey

DEBUG = False
IDE = False
args = sys.argv
if get_at(args, -1) == "-debug":
    DEBUG = True
elif get_at(args, -1) == "-ide":
    DEBUG = True
    IDE = True

server_ip = "127.0.0.1"
port = 5000
LOGIN = False
if get_at(args, 1) == "-login":
    server_ip = get_at(args, 2)
    port = int(get_at(args, 3))
    LOGIN = True

if IDE:
    setattr(utils, "clear_screen", lambda: None)

system_type = platform.system()

dirpath, filepath = utils.get_executed_path()


def main():
    _client = client()
    _client.root_path = dirpath
    _client.on_service_register.add(init_plugin)
    _client.on_cmd_register.add(add_commands)
    _client.on_keymapping.add(mapkeys)
    _client.init()
    if LOGIN:
        _client.connect(server_ip, port)
    _client.start()


def init_plugin(client, registry: container):
    if system_type == "Windows":
        from ui import nonblocks
        registry.register_singleton(i_input, nonblocks.nbinput)
    elif system_type == "Linux":
        from ui import linux
        registry.register_singleton(i_input, linux.nbinput)

    if DEBUG:
        from ui.cmdprompt import cmd_input
        registry.register_singleton(i_input, cmd_input)


def mapkeys(client, keymap: cmdkey):
    if keymap is client.key_enter_text:
        keymap.map(c_t)
        return
    elif keymap is client.key_quit_text_mode:
        keymap.map(keys.k_quit)


def add_commands(client, cmd_manager: cmdmanager):
    from cmds import cmds
    for cmd in cmds:
        cmd_manager.add(cmd)


if __name__ == '__main__':
    main()
