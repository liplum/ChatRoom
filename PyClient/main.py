import sys

import GLOBAL
import utils
from debugs import FakeStringIO
from utils import get_at

IDE = False
args = sys.argv
if get_at(args, -1) == "-debug":
    GLOBAL.DEBUG = True
elif get_at(args, -1) == "-debugX":
    GLOBAL.DEBUG = True
    GLOBAL.MONITOR = True
elif get_at(args, -1) == "-ide":
    GLOBAL.DEBUG = True
    IDE = True

import core.settings as settings
import configs

for config in configs.configs:
    settings.add(config)

settings.load()
configurations = settings.entity()
import i18n

i18n.load(configurations.Language)

server_ip = "127.0.0.1"
port = 25000
LOGIN = False
if get_at(args, 1) == "-login":
    may_ip = get_at(args, 2)
    server_ip = may_ip if may_ip and not may_ip.startswith("-") else server_ip
    try:
        may_port = int(get_at(args, 3))
    except:
        may_port = None
    port = may_port if may_port and not str(may_port).startswith("-") else port
    LOGIN = True

if IDE:
    utils.clear_screen = lambda: None

if IDE:
    GLOBAL.StringIO = FakeStringIO
else:
    import io

    GLOBAL.StringIO = io.StringIO

import platform

system_type = platform.system()


def main():
    from ui.clients import client
    _client = client()
    _client.on_service_register.add(init_plugin)
    _client.on_cmd_register.add(add_commands)
    _client.on_keymapping.add(mapkeys)
    _client.init()
    if LOGIN:
        _client.connect(server_ip, port)
    if GLOBAL.MONITOR:
        from pef.monitor import pef_monitor
        _client.container.resolve(pef_monitor)
    _client.start()
    settings.save()


from ioc import container


def init_plugin(client, registry: container):
    from ui.inputs import iinput
    if system_type == "Windows":
        from ui.wins import nonblocks
        registry.register_singleton(iinput, nonblocks.nbinput)
    elif system_type == "Linux":
        from ui.linuxs import nonblocks
        registry.register_singleton(iinput, nonblocks.nbinput)
    else:
        from ui.cmdprompt import cmd_input
        registry.register_singleton(iinput, cmd_input)

    if IDE:
        from ui.cmdprompt import cmd_input
        registry.register_singleton(iinput, cmd_input)

    if GLOBAL.MONITOR:
        from pef.monitor import pef_monitor
        registry.register_instance(pef_monitor, pef_monitor(interval=0.1))


import ui.k as uik


def mapkeys(client, keymap: uik.cmdkey):
    import keys
    import chars
    if keymap is client.key_enter_text:
        keymap.map(chars.c_t)
        return
    elif keymap is client.key_quit_text_mode:
        keymap.map(keys.k_quit)


from cmds import cmdmanager


def add_commands(client, cmd_manager: cmdmanager):
    from builtincmds import cmds
    for cmd in cmds:
        cmd_manager.add(cmd)


if __name__ == '__main__':
    main()
