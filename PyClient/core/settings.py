import json
import os
import sys
from typing import TypeVar, Callable, Optional, Dict, Any, NoReturn

from utils import not_none

T = TypeVar('T')

_dirpath, _filepath = os.path.split(os.path.abspath(sys.argv[0]))

if os.access(_dirpath, os.F_OK & os.R_OK & os.W_OK):
    _root_path = _dirpath
else:
    _root_path = ""


class convertTo:
    def convert(self, para: Any) -> T:
        pass

    def __call__(self, para: Any) -> T:
        return self.convert(para)


class convertFrom:
    def convert(self, para: T) -> Any:
        pass

    def __call__(self, para: T) -> Any:
        return self.convert(para)


Config_Style = int


class Style:
    CheckBox = 0
    OnlyNumber = 1
    OnlyAlphabet = 2
    AnyString = 3
    OnlyNumber_Alphabet = 4


New_Value = Any
New_Value_Callback = Callable[["settings", New_Value], NoReturn]


class prop:
    def __init__(self, style: Config_Style, new_value_callback: New_Value_Callback):
        self.style: Config_Style = style
        self.new_value_callback: New_Value_Callback = new_value_callback


class prop_builder:
    def __init__(self, config: "config"):
        self.config = config
        self._new_value_callback = None

    def style(self, style: Config_Style) -> "prop_builder":
        if style is None:
            raise ValueError(style)
        self._control_style = style
        return self

    def notice(self, callback: New_Value_Callback) -> "prop_builder":
        if callback is None:
            raise ValueError(callback)
        self._new_value_callback = callback
        return self

    def build(self) -> "config":
        if not_none(self._new_value_callback, self._control_style):
            self.config.prop = prop(self._control_style, self._new_value_callback)
            return self.config
        raise BuildError(self.config)


class config:
    def __init__(self, key: str, default: T, convert_to: Optional[Callable[[Any], T]] = None,
                 convert_from: Optional[Callable[[T], Any]] = None, json_type: Optional[type] = None):
        self.key: str = key
        self.default = default
        self._is_customizable = False
        if json_type is None:
            json_type = type(default)
        self.json_type: type = json_type
        self.prop: Optional[prop] = None
        if convert_to is None:
            convert_to = type(default)
        self.convert_to = convert_to
        if convert_from is None:
            convert_from = str
        self.convert_from = convert_from

    def customizable(self) -> prop_builder:
        self._is_customizable = True
        return prop_builder(self)

    @property
    def is_customizable(self) -> bool:
        return self._is_customizable


class ValueInvalidError(Exception):
    def __init__(self, msg: str):
        super().__init__()
        self.msg = msg


class BuildError(Exception):

    def __init__(self, config: config) -> None:
        super().__init__(config.key)


_meta: Dict[str, config] = {}


def all_meta() -> Dict[str, config]:
    return _meta


def all_customizable() -> Dict[str, config]:
    return {key: config for key, config in _meta.items() if config.is_customizable}


class settings:
    def __init__(self, meta: Dict[str, config]):
        self._meta = meta
        self.all_settings: Dict[str, T] = {}

    def __getattr__(self, item) -> Optional[T]:
        return self.get(item)

    def get(self, item):
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

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, key, value):
        key = str(key)
        self.set(key, value)


_settings: Optional[settings] = None


def entity() -> settings:
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
                meta = _meta[k]
                if isinstance(v, meta.json_type):
                    finalV = meta.convert_from(v)
                    _final[k] = finalV
            else:
                _final[k] = v
        settings_text = json.dumps(_final, indent=2, ensure_ascii=False)
        with open(file, "w", encoding="utf-8") as f:
            f.write(settings_text)
    except Exception as e:
        if strict:
            raise SaveError(e, file)


def load(strict: bool = False):
    global _settings
    file = f"{_root_path}/settings.json"
    read = settings(_meta)
    try:
        with open(file, "r", encoding="utf-8") as f:
            settings_text = f.read()
        cache: Dict[str, Any] = json.loads(settings_text)
        for k, v in cache.items():
            if k in _meta:
                try:
                    meta = _meta[k]
                    if isinstance(v, meta.json_type):
                        finalv = meta.convert_to(v)
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
