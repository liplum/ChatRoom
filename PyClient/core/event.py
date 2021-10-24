from typing import Callable, List


class event:
    def __init__(self):
        self.subscribers: List[Callable] = []

    def __call__(self, *args, **kwargs):
        return self.invoke(*args, **kwargs)

    def add(self, subscriber: Callable) -> None:
        self.subscribers.append(subscriber)

    def remove(self, subscriber: Callable) -> None:
        self.subscribers.remove(subscriber)

    def clear(self) -> None:
        self.subscribers.clear()

    def invoke(self, *args, **kwargs):
        returnValue = None
        for subscriber in self.subscribers:
            returnValue = subscriber(*args, **kwargs)
        return returnValue
