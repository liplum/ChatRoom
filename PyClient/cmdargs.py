from typing import Dict

class command:
    def __init__(self, name: str, tip: str, handler):
        self.name = name
        self.tip = tip
        self.handler = handler

    def match(self, text) -> bool:
        if text == self.name:
            return True
        else:
            return False

    def execute(self):
        self.handler()


class cmdmanager:
    def __init__(self):
        self.tree = dictrie()
        self.map: Dict[str, command] = {}

    def add(self, cmd: command):
        name = cmd.name
        self.tree.insert_word(name)
        self.map[name] = cmd

