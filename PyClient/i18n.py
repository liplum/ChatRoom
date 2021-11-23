import json
import os
import sys
from typing import Dict, List, Iterable, Tuple
from typing import Optional

from events import event

_cache: Dict[str, str] = {}

_dirpath, _filepath = os.path.split(os.path.abspath(sys.argv[0]))

if os.access(_dirpath, os.F_OK & os.R_OK):
    _root_path = _dirpath
else:
    _root_path = ""

lang_folder = f"{_root_path}/lang"
cur_lang = "en_us"

on_load = event()
"""
Para 1:current language

:return: event(str)
"""

Without_Extension = str
Name = str


def _all_file() -> Iterable[Name]:
    for root, ds, fs in os.walk(lang_folder):
        for f in fs:
            yield f


def _all_file_with_extension(extension: str) -> Iterable[Tuple[Without_Extension, Name]]:
    for root, ds, fs in os.walk(lang_folder):
        for f in fs:
            n, e = os.path.splitext(f)
            if e == extension:
                yield n, f


Language_ID = str


def all_languages() -> List[Language_ID]:
    return [no_e for no_e, name in _all_file_with_extension('.json')]


def reload(strict: bool = False):
    global _cache, cur_lang
    file = f"{lang_folder}/{cur_lang}.json"
    try:
        with open(file, "r", encoding="utf-8") as f:
            _cache = json.load(f)
            on_load(cur_lang)
    except Exception as e:
        if strict:
            raise LocfileLoadError(e, cur_lang)
        else:
            _cache = {}


def load(lang: Optional[str] = None, strict: bool = False):
    global _cache, cur_lang
    if lang is None:
        lang = cur_lang
    lang = lang.lower()
    file = f"{lang_folder}/{lang}.json"
    try:
        with open(file, "r", encoding="utf-8") as f:
            _cache = json.load(f)
            cur_lang = lang
            on_load(cur_lang)
    except Exception as e:
        if strict:
            raise LocfileLoadError(e, lang)
        else:
            _cache = {}


class LocfileLoadError(Exception):

    def __init__(self, inner: Exception, lang):
        super().__init__()
        self.lang = lang
        self.inner: Exception = inner


def trans(key: str, *args, **kwargs):
    parts = key.split(".")
    cur = _cache
    try:
        for part in parts:
            cur = cur[part]
        if isinstance(cur, dict):
            return key
        try:
            return cur.format(*args, **kwargs)
        except:
            return cur
    except:
        return key
