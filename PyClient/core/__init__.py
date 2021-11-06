import platform

from core import utils

system_type = platform.system()

if system_type == "Windows":
    utils.clear_screen = utils.clear_screen_win
elif system_type == "Linux":
    utils.clear_screen = utils.clear_screen_linux
