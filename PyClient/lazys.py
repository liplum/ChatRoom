from typing import Callable, Generic, Optional, TypeVar

T = TypeVar("T")


class lazy(Generic[T]):
    def __init__(self, getter: Callable[[], T]):
        self.getter: Callable[[], T] = getter
        self.delegate: Optional[T] = None

    def resolve(self):
        self.delegate = self.getter()
        if self.delegate is None:
            raise ValueError("Getter returns a None value.")

    def __call__(self, *args, **kwargs) -> T:
        if self.delegate is None:
            self.resolve()
        return self.delegate
