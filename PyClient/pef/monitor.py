import os
from threading import Thread
from time import sleep

import psutil

from ui.outputs import ilogger


class pef_monitor:
    def __init__(self, interval: float = 0.05):
        self.monitor = None
        self.interval = interval
        self.pid = os.getpid()
        self.process = psutil.Process(self.pid)
        self.lastMemoryMB: int = 0

    def init(self, container: "container"):
        self.logger: ilogger = container.resolve(ilogger)
        self.start()

    def start(self):
        if not self.monitor:
            self.monitor = Thread(target=self._monitor, name="PerMonitor")
            self.monitor.daemon = True
            self.monitor.start()

    def _monitor(self):
        while True:
            info = self.process.memory_full_info()
            usage = info.uss / 1024 / 1024
            usageInt = int(usage)
            if self.lastMemoryMB != usageInt:
                self.lastMemoryMB = usageInt
                self.logger.tip(f"[Monitor]Current Memory Usage: {usage} MB")
            sleep(self.interval)
