import json
import os
import sys
from typing import TypeVar, Callable, Optional, Dict

T = TypeVar('T')

_dirpath, _filepath = os.path.split(os.path.abspath(sys.argv[0]))

if os.access(_dirpath, os.F_OK & os.R_OK & os.W_OK):
    _root_path = _dirpath
else:
    _root_path = ""


class convertTo:
    def convert(self, para: str) -> T:
        pass

    def __call__(self, para: str) -> T:
        return self.convert(para)


class convertFrom:
    def convert(self, para: T) -> str:
        pass

    def __call__(self, para: T) -> str:
        return self.convert(para)


class config:
    def __init__(self, key: str, default: T, convert_to: Optional[Callable[[str], T]] = None,
                 convert_from: Optional[Callable[[T], str]] = None):
        self.key = key
        self.default = default
        if convert_to is None:
            convert_to = type(default)
        self.convert_to = convert_to
        if convert_from is None:
            convert_from = str
        self.convert_from = convert_from


_meta: Dict[str, config] = {}


class settings:
    def __init__(self, meta: Dict[str, config]):
        self._meta = meta
        self.all_settings: Dict[str, T] = {}

    def __getattr__(self, item) -> Optional[T]:
        item = str(item)
        if item in self.all_settings:
            return self.all_settings[item]
        elif item in self._meta:
            item = str(item)
            config = self._meta[item]
            dv = config.default
            self.set(item, dv)
            return dv
        else:
            return None

    def set(self, key: str, value: T):
        self.all_settings[key] = value


_settings: Optional[settings] = None


def table() -> settings:
    if _settings is None:
        raise NotLoadedError()
    else:
        return _settings


def add(config: config):
    _meta[config.key] = config


def save(strict: bool = False):
    if _settings is None:
        raise NotLoadedError()
    file = f"{_root_path}/settings.json"
    try:
        _final: Dict[str, str] = {}
        for k, v in _settings.all_settings.items():
            if k in _meta:
                finalV = _meta[k].convert_from(v)
                _final[k] = finalV
            else:
                _final[k] = v
        with open(file, "w", encoding="utf-8") as f:
            json.dump(_final, f, indent=4)
    except Exception as e:
        if strict:
            raise SaveError(e, file)


def load(strict: bool = False):
    global _settings
    file = f"{_root_path}/settings.json"
    read = settings(_meta)
    try:
        with open(file, "r", encoding="utf-8") as f:
            cache: Dict[str, str] = json.load(f)
            for k, v in cache.items():
                if k in _meta:
                    try:
                        finalv = _meta[k].convert_to(v)
                        read.set(k, finalv)
                    except:
                        continue
                else:
                    read.set(k, v)
    except Exception as e:
        if strict:
            raise LoadError(e, file)
        else:
            for k, config in _meta.items():
                read.set(k, config.default)
    _settings = read


class NotLoadedError(Exception):
    def __init__(self):
        super().__init__()


class SaveError(Exception):
    def __init__(self, inner: Exception, file: str):
        super().__init__()
        self.inner = inner
        self.file = file


class LoadError(Exception):
    def __init__(self, inner: Exception, file: str):
        super().__init__()
        self.inner = inner
        self.file = file
