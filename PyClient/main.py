import io
import sys

import GLOBAL
import utils
from debugs import FakeStringIO
from utils import get_at

GLOBAL.StringIO = io.StringIO
IDE = False
args = sys.argv
finalarg: str = arg if (arg := get_at(args, -1)) is not None else ""
extra = []


def match_arg(para: str):
    matched = finalarg.startswith(para)
    if matched:
        global extra
        extra = finalarg.replace(para, "")
    return matched


if match_arg("-debug"):
    GLOBAL.DEBUG = True
elif match_arg("-ide"):
    GLOBAL.DEBUG = True
    IDE = True
elif match_arg(""):
    pass

if "M" in extra:
    GLOBAL.MONITOR = True
if "S" in extra:
    GLOBAL.StringIO = FakeStringIO

if IDE:
    utils.clear_screen = lambda: None

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

import platform

system_type = platform.system()


def detect_debug_attach():
    input("Attach the process and enter any text to start:")


if GLOBAL.DEBUG:
    detect_debug_attach()

import core.settings as settings
import configs

for config in configs.configs:
    settings.add(config)

settings.load()
configurations = settings.entity()
import i18n

i18n.load(configurations.Language)


def main():
    from ui.Clients import Client
    _client = Client()
    _client.on_service_register.Add(init_plugin)
    _client.on_cmd_register.Add(add_commands)
    _client.on_keymapping.Add(mapkeys)
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
    if IDE:
        from ui.cmds.cmdprompt import cmd_input
        registry.register_singleton(iinput, cmd_input)
    else:
        if system_type == "Windows":
            from ui.wins import nonblocks
            registry.register_singleton(iinput, nonblocks.nbinput)
        elif system_type == "Linux":
            from ui.linuxs import nonblocks
            registry.register_singleton(iinput, nonblocks.nbinput)
        else:
            from ui.cmds.cmdprompt import cmd_input
            registry.register_singleton(iinput, cmd_input)

    if GLOBAL.MONITOR:
        from pef.monitor import pef_monitor
        registry.register_instance(pef_monitor, pef_monitor(interval=0.5))


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
