class event:
    def __init__(self, cancelable=False):
        self.subscribers = []
        self.cancelable = cancelable

    def __call__(self, *args, **kwargs):
        self.invoke(*args, **kwargs)

    def add(self, *args) -> "event":
        for subscriber in args:
            self.subscribers.append(subscriber)
        return self

    def remove(self, subscriber) -> "event":
        self.subscribers.remove(subscriber)
        return self

    def clear(self) -> "event":
        self.subscribers.clear()
        return self

    def invoke(self, *args, **kwargs):
        if self.cancelable:
            for subscriber in self.subscribers:
                canceled = subscriber(*args, **kwargs)
                if canceled:
                    return True
        else:
            for subscriber in self.subscribers:
                subscriber(*args, **kwargs)
            return False
