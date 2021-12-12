from time import time
from typing import Generator

Suspend = -1
Finished = 0


def wait_for_seconds(seconds: float) -> Generator:
    start = time()
    while time() - start < seconds:
        yield Suspend
    yield Finished
