from enum import Enum, unique, auto
from inspect import signature

from typing import Dict, Any, Union


@unique
class RegisterType(Enum):
    Singleton = auto()
    Instance = auto()
    Transient = auto()


class item:
    def __init__(self, _type):
        self.in_type = _type
        self.register_type = None
        self.instance = None
        self.out_type = None


class container:
    def __init__(self):
        self.type2item: Dict[type, item] = {}
        self.name2item: Dict[str, item] = {}

    def resolve(self, in_type: Union[type, str]):
        if isinstance(in_type, type):
            if in_type not in self.type2item:
                raise ServiceNotRegistered(str(in_type))
            _item = self.type2item[in_type]
        elif isinstance(in_type, str):
            if in_type not in self.name2item:
                raise ServiceNotRegistered(in_type)
            _item = self.name2item[in_type]
        else:
            raise KeyError(in_type)

        register_type = _item.register_type
        res = None
        if register_type == RegisterType.Singleton:
            res = _item.instance
        elif register_type == RegisterType.Instance:
            res = _item.instance
        elif register_type == RegisterType.Transient:
            res = _item.out_type()
        self.__inject(res)
        return res

    def __inject(self, obj: Any):
        if isinstance(obj, injectable):
            obj.init(self)
        elif hasattr(obj, "init"):
            sig = signature(obj.init)
            paras = sig.parameters
            if len(paras) == 1:  # it means the object has two paras,one for self and one for container
                obj.init(self)

    def __get_or_gen_item(self, baseType: type):
        if baseType not in self.type2item:
            _item = item(baseType)
            self.type2item[baseType] = _item
            self.name2item[baseType.__qualname__] = _item
            return _item
        else:
            _item = self.type2item[baseType]
            return _item

    def register_instance(self, base_type, instance):
        _item = self.__get_or_gen_item(base_type)
        _item.register_type = RegisterType.Instance
        _item.instance = instance
        _item.out_type = type(instance)

    def register_transient(self, in_type, out_type):
        _item = self.__get_or_gen_item(in_type)
        _item.register_type = RegisterType.Transient
        _item.out_type = type(out_type)

    def register_singleton(self, in_type, out_type):
        _item = self.__get_or_gen_item(in_type)
        _item.register_type = RegisterType.Singleton
        _item.instance = out_type()
        _item.out_type = type(out_type)


class injectable:
    def init(self, container: container):
        pass


class ServiceNotRegistered(Exception):
    def __init__(self, service):
        self.args = (str(service),)
