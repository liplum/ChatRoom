from datetime import datetime
from typing import TypeVar, Any

from core.settings import config, settings, ValueInvalidError, Style

configs = []

T = TypeVar('T')


def no_change(obj: T) -> T:
    return obj


def addx(key: str, default: Any) -> config:
    c = config(key, default, no_change, no_change)
    configs.append(c)
    return c


def add(*args, **kwargs) -> config:
    c = config(*args, **kwargs)
    configs.append(c)
    return c


def _verify_date_format(settings: settings, v: str):
    try:
        datetime.now().strftime(v)
    except:
        raise ValueInvalidError(v)
    settings["DateFormat"] = v


def _directly_set(config: config):
    def _set(settings: settings, v: str):
        settings.set(config.key, v)

    return _set


language = add("Language", "en_us")

date_format = add("DateFormat", "%Y-%m-%d %H:%M:%S").customizable().style(Style.AnyString).notice(
    _verify_date_format).build()

auto_connection = addx("AutoConnection", [])

auto_login = addx("AutoLogin", [])

last_opened_tabs = addx("LastOpenedTabs", {})

restore_tab_when_restart = addx("RestoreTabWhenRestart", False)
restore_tab_when_restart.customizable().style(Style.CheckBox).notice(
    _directly_set(restore_tab_when_restart)
).build()

auto_login_switch = addx("AutoLoginSwitch", False)
auto_login_switch.customizable().style(Style.CheckBox).notice(
    _directly_set(auto_login_switch)
).build()

colorful_main_menu = addx("ColorfulMainMenu", False)
colorful_main_menu.customizable().style(Style.CheckBox).notice(
    _directly_set(colorful_main_menu)
).build()
