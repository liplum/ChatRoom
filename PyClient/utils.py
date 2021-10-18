from typing import Dict


def get(dic: Dict, key):
    if key in dic:
        return dic[key]
    else:
        return None


def get_not_none_one(*args):
    """
    :param args:all selections
    :return: the first not none one otherwise None
    """
    for arg in args:
        if arg is not None:
            return arg
    return None


def not_none(*args) -> bool:
    for arg in args:
        if arg is None:
            return False
    return True
