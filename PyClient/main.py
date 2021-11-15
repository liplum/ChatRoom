import sys

import GLOBAL
import utils
from utils import get_at

IDE = False
args = sys.argv
if get_at(args, -1) == "-debug":
    GLOBAL.DEBUG = True
elif get_at(args, -1) == "-ide":
    GLOBAL.DEBUG = True
    IDE = True

server_ip = "127.0.0.1"
port = 5000
LOGIN = False
if get_at(args, 1) == "-login":
    server_ip = get_at(args, 2)
    port = int(get_at(args, 3))
    LOGIN = True

if IDE:
    utils.clear_screen = lambda: None

import platform

system_type = platform.system()

dirpath, filepath = utils.get_executed_path()


def main():
    from ui.clients import client
    _client = client()
    _client.root_path = dirpath
    _client.on_service_register.add(init_plugin)
    _client.on_cmd_register.add(add_commands)
    _client.on_keymapping.add(mapkeys)
    _client.init()
    if LOGIN:
        _client.connect(server_ip, port)
    _client.start()


from ioc import container


def init_plugin(client, registry: container):
    from ui.inputs import i_input
    if system_type == "Windows":
        from ui import nonblocks
        registry.register_singleton(i_input, nonblocks.nbinput)
    elif system_type == "Linux":
        from ui import linux
        registry.register_singleton(i_input, linux.nbinput)

    if IDE:
        from ui.cmdprompt import cmd_input
        registry.register_singleton(i_input, cmd_input)


import ui.k as uik


def mapkeys(client, keymap: uik.cmdkey):
    import keys
    import chars
    if keymap is client.key_enter_text:
        keymap.map(chars.c_t)
        return
    elif keymap is client.key_quit_text_mode:
        keymap.map(keys.k_quit)


from cmd import cmdmanager


def add_commands(client, cmd_manager: cmdmanager):
    from cmds import cmds
    for cmd in cmds:
        cmd_manager.add(cmd)


if __name__ == '__main__':
    main()
