from enum import Enum, unique, auto


class container:
    def __init__(self):
        self.all = {}

    def resolve(self, in_type):
        if in_type not in self.all:
            raise ServiceNotRegistered(str(in_type))
        _item = self.all[in_type]
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

    def __inject(self, obj):
        if hasattr(obj, "init"):
            obj.initialize(self)

    def __get_or_gen_item(self, baseType):
        if baseType not in self.all:
            _item = item(baseType)
            self.all[baseType] = _item
            return _item
        else:
            _item = self.all[baseType]
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


class ServiceNotRegistered(Exception):
    def __init__(self, arg):
        self.args = arg
