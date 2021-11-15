from typing import Any

from core.filer import i_filer


class convert:
    def convert(self, arg) -> Any:
        pass

    def __call__(self, *args, **kwargs):
        return self.convert(*args, **kwargs)


class config:
    pass


class i_setting:
    def save(self):
        pass


class setting(i_setting):
    def init(self, container: "container"):
        self.filer = container.resolve(i_filer)
