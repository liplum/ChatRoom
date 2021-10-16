class event:
    def __init__(self):
        self.subscribers = []

    def __call__(self, *args, **kwargs):
        return self.invoke(*args, **kwargs)

    def add(self, subscriber) -> None:
        self.subscribers.append(subscriber)

    def remove(self, subscriber) -> None:
        self.subscribers.remove(subscriber)

    def clear(self) -> None:
        self.subscribers.clear()

    def invoke(self, *args, **kwargs):
        returnValue = None
        for subscriber in self.subscribers:
            returnValue = subscriber(*args, **kwargs)
        return returnValue
