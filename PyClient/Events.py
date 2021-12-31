from inspect import signature
from typing import Iterable, Collection

IsCanceled = bool
Canceled = True
NotCanceled = False


def _GetTypes(args: Collection[object]) -> tuple:
    return tuple(type(obj) for obj in args)


class Event:
    def __init__(self, *argTypes, cancelable=False):
        self.argTypes = argTypes
        self.subscribers = set()
        self.cancelable = cancelable

    def __repr__(self) -> str:
        return f"Event(*{self.ArgTypes},cancelable={self.Cancelable})"

    @property
    def Cancelable(self) -> bool:
        return self.cancelable

    @property
    def ArgCount(self) -> int:
        return len(self.argTypes)

    @property
    def ArgTypes(self) -> tuple:
        return self.argTypes

    def __call__(self, *args, **kwargs) -> IsCanceled:
        """
        Raise the event
        :exception EventArgError: sds
        :return: whether the event was canceled
        """
        return self.Invoke(*args)

    def Add(self, *args) -> "Event":
        for subscriber in args:
            para = tuple(signature(subscriber).parameters)
            paralen = len(para)
            if paralen != self.ArgCount:
                raise EventArgError(f"{para} can't match required argument types {self.ArgTypes}.")
            self.subscribers.add(subscriber)
        return self

    def Remove(self, subscriber) -> "Event":
        self.subscribers.remove(subscriber)
        return self

    def Clear(self) -> "Event":
        self.subscribers.clear()
        return self

    def Invoke(self, *args) -> IsCanceled:
        """
        Raise the event
        :return: whether the event was canceled
        """
        arglen = len(args)
        argTypes = self.ArgTypes
        if arglen != self.ArgCount:
            raise EventArgError(f"{paraTypes} can't match required argument types {argTypes}.")
        for i in range(arglen):
            argType = argTypes[i]
            arg = args[i]
            if not isinstance(arg, argType):
                raise EventArgError(f"{args} can't match required argument types {argTypes} at [{i}]={arg}.")
        cancelable = self.Cancelable
        for subscriber in self.subscribers:
            canceled = subscriber(*args)
            if cancelable and canceled is True:
                return Canceled
        return NotCanceled

    def __iadd__(self, other):
        if isinstance(other, Iterable):
            self.Add(*other)
        else:
            self.Add(other)

    def Sub(self, *newArgTypes, cancelable=False) -> "Event":
        return SubEvent(self, *newArgTypes, cancelable=cancelable)


class SubEvent(Event):
    def __init__(self, parent: Event, *newArgTypes, cancelable=False):
        super().__init__(*parent.ArgTypes, cancelable=cancelable)
        self.parent = parent
        self.newArgTypes = newArgTypes

    def Invoke(self, *args) -> IsCanceled:
        """
        Raise the event
        :return: whether the event was canceled
        """
        arglen = len(args)
        argTypes = self.ArgTypes
        if arglen != self.ArgCount:
            raise EventArgError(f"{paraTypes} can't match required argument types {argTypes}.")
        for i in range(arglen):
            argType = argTypes[i]
            arg = args[i]
            if not isinstance(arg, argType):
                raise EventArgError(f"{args} can't match required argument types {argTypes} at [{i}]={arg}.")
        parentArgs = args[0:self.parent.ArgCount]
        self.parent.Invoke(*parentArgs)
        cancelable = self.Cancelable
        for subscriber in self.subscribers:
            canceled = subscriber(*args)
            if cancelable and canceled is True:
                return Canceled
        return NotCanceled

    @property
    def Parent(self) -> Event:
        return self.parent

    @property
    def ArgCount(self) -> int:
        return self.parent.ArgCount + len(self.newArgTypes)

    @property
    def ArgTypes(self) -> tuple:
        return self.parent.ArgTypes + self.newArgTypes


class EventArgError(Exception):
    def __init__(self, *args: object):
        super().__init__(*args)
