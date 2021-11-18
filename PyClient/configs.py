from typing import TypeVar, Any

from core.settings import config

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


language = add("Language", "en_us")

auto_connection = addx("AutoConnection", [])

auto_login = addx("AutoLogin", {})

last_opened_tabs = addx("LastOpenedTabs", {})

restore_tab_when_restart = addx("RestoreTabWhenRestart", False)
