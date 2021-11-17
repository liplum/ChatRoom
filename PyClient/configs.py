from typing import TypeVar

from core.settings import config

configs = []

T = TypeVar('T')


def _no_change(obj: T) -> T:
    return obj


def add(*args, **kwargs) -> config:
    c = config(*args, **kwargs)
    configs.append(c)
    return c


language = add("Language", "en_us")

auto_connection = add("AutoConnection", [], convert_to=_no_change, convert_from=_no_change)

auto_login = add("AutoLogin", {}, convert_to=_no_change, convert_from=_no_change)
