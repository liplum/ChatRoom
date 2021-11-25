from typing import Dict

from core.shared import *

AP = Tuple[str, str]


class ipwd_manager:
    def __init__(self):
        self.pwds: Dict[server_token, AP] = {}

class paw_manager(ipwd_manager):
    def __init__(self):
        super().__init__()