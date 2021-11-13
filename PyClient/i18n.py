import json
import os
import sys
from typing import Dict
from typing import Optional

from events import event

_cache: Dict[str, str] = {"123": "123"}

_dirpath, _filepath = os.path.split(os.path.abspath(sys.argv[0]))

if os.access(_dirpath, os.F_OK & os.R_OK):
    _root_path = _dirpath
else:
    _root_path = ""

cur_lang = "en-us"

on_load = event()
"""
Para 1:current language

:return: event(str)
"""


def reload():
    file = f"{_root_path}/lang/{cur_lang}.json"
    try:
        with open(file, "r") as f:
            _cache = json.load(f)
            on_load(cur_lang)
    except:
        pass


def load(lang: Optional[str] = None):
    global _cache, cur_lang
    if lang is None:
        lang = cur_lang
    file = f"{_root_path}/lang/{lang}.json"
    try:
        with open(file, "r") as f:
            _cache = json.load(f)
            cur_lang = lang
            on_load(cur_lang)
    except:
        _cache = {}


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
