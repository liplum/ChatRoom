from core.settings import config

configs = []


def add(*args) -> config:
    c = config(*args)
    configs.append(c)
    return c


language = add("Language", "en_us")
