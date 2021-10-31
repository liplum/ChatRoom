class command:
    def __init__(self, _id: str, tip: str, handler):
        self.id = _id
        self.tip = tip
        self.handler = handler

    def match(self, text) -> bool:
        if text == self.id:
            return True
        else:
            return False

    def execute(self):
        self.handler()
