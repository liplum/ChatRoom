from core.ioc import container
import platform
import sys

import keys
import utils
from chars import *
from core.chats import msgstorage
from core.ioc import container
from ui.clients import client
from ui.inputs import i_input
from ui.k import cmdkey

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
