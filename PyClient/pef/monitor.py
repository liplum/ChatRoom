import os
from threading import Thread
from time import sleep

import psutil

from ui.outputs import i_logger


class pef_monitor:
    def __init__(self, interval: float = 0.05):
        self.monitor = None
        self.interval = interval
        self.pid = os.getpid()
        self.process = psutil.Process(self.pid)

    def init(self, container: "container"):
        self.logger: i_logger = container.resolve(i_logger)
        self.start()

    def start(self):
        if not self.monitor:
            self.monitor = Thread(target=self._monitor)
            self.monitor.daemon = True
            self.monitor.start()

    def _monitor(self):
        while True:
            info = self.process.memory_full_info()
            usage = info.uss / 1024 / 1024
            self.logger.tip(f"[Monitor]Current Memory Usage: {usage} MB")
            sleep(self.interval)
