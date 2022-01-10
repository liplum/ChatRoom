from enum import Enum
from typing import Callable, Dict, Optional,NoReturn
from typing import List, Type

from Events import Event
from utils import multiget


class DpKey:
    def __init__(self, name: str, ownerType: type):
        self._name = name
        self._ownerType = ownerType
        self._hashCode = hash(name) ^ hash(ownerType)

    def __hash__(self) -> int:
        return self._hashCode

    def __eq__(self, o: object) -> bool:
        return isinstance(o, DpKey) and self._name == o._name and self._ownerType == o._ownerType


class DpPropMeta:
    pass


ValidateValueFuncType = Callable[[object], bool]


class DpProp:
    _PropertyFromName: Dict[DpKey, "DpProp"] = {}

    @classmethod
    def Register(cls, name: str, propType: type,
                 ownerType: type, meta: DpPropMeta,
                 validateValueFunc: Optional[ValidateValueFuncType] = None) -> "DpProp":
        key = DpKey(name, ownerType)
        if key in cls._PropertyFromName:
            raise ExistedDpKeyError(f"{name} and {ownerType} already exist", name, ownerType)

        dp = DpProp(name, propType, ownerType, meta, validateValueFunc)
        cls._PropertyFromName[key] = dp
        return dp

    @classmethod
    def RegisterAttach(cls):
        pass

    def __init__(self, name: str, propType: type,
                 ownerType: type, meta: DpPropMeta,
                 validateValueFunc: Optional[ValidateValueFuncType]):
        """
        Private Constructor
        """
        super().__init__()
        self._name = name
        self._propType = propType
        self._ownerType = ownerType
        self._meta = meta
        self._validateValueFunc = validateValueFunc


EventHandlerType = Callable[["DpObj", "RoutedEventArgs"], NoReturn]
EventHandlerMap = Dict["RoutedEventType", List[EventHandlerType]]


class DpObj:
    def __init__(self):
        super().__init__()
        self.DpPropValueEntries: Dict[DpProp, Optional[object]] = {}
        self._onDpPropChanged = Event(DpObj, DpProp, object, object)
        self._eventHandlers: EventHandlerMap = {}

    def AddEventHandler(self, eventType: "RoutedEventType", handler: EventHandlerType):
        handlers = multiget(self.EventHandlers, eventType)
        handlers.append(handler)

    def RemoveEventHandler(self, eventType: "RoutedEventType", handler: EventHandlerType) -> bool:
        handlers = multiget(self.EventHandlers, eventType)
        try:
            handlers.remove(handler)
            return True
        except:
            return False

    def ClearEventHandler(self, eventType: "RoutedEventType"):
        self.EventHandlers[eventType] = []

    @property
    def EventHandlers(self):
        return self._eventHandlers

    def SetValue(self, prop: DpProp, value):
        self.DpPropValueEntries[prop] = value

    def GetValue(self, prop: DpProp):
        if prop not in self.DpPropValueEntries:
            self.DpPropValueEntries[prop] = None
        return self.DpPropValueEntries[prop]

    def TryCatchEvent(self, eventType: "RoutedEventType", sender: "DpObj", args: "RoutedEventArgs"):
        handlers = multiget(self.EventHandlers, eventType)
        for handler in handlers:
            if args.Cancelable and args.IsHandled:
                break
            handler(sender, args)


class ExistedDpKeyError(Exception):
    def __init__(self, *args: object):
        super().__init__(*args)


class RoutedStrategy(Enum):
    Bubble = 1
    Tunnel = 2
    Direct = 3


class RoutedEventType:
    _EventFromName: Dict[DpKey, "RoutedEventType"] = {}

    def __init__(self, name: str, ownerType: type
                 , argsType: Type["RoutedEventArgs"], strategy: RoutedStrategy):
        super().__init__()
        self._name = name
        self._ownerType = ownerType
        self._argsType: Type["RoutedEventArgs"] = argsType
        self._strategy = strategy

    @classmethod
    def Register(cls, name: str, ownerType: type
                 , argsType: Type["RoutedEventArgs"], strategy: RoutedStrategy) -> "RoutedEventType":
        key = DpKey(name, ownerType)
        if key in cls._EventFromName:
            raise ExistedDpKeyError(f"{name} and {ownerType} already exist", name, ownerType)
        e = RoutedEventType(name, ownerType, argsType, strategy)
        cls._EventFromName[key] = e
        return e

    @property
    def ArgsType(self) -> Type["RoutedEventArgs"]:
        return self._argsType

    @property
    def Strategy(self):
        return self._strategy


class RoutedEventArgs:
    def __init__(self, cancelable=True):
        super().__init__()
        self.IsHandled = False
        self.__cancelable = cancelable

    @property
    def Cancelable(self):
        return self.__cancelable


class EventTypeError(Exception):
    def __init__(self, *args: object):
        super().__init__(*args)
