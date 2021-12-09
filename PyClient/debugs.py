class FakeStringIO:
    def __init__(self):
        self.text = ""

    def write(self, s: str):
        self.text += s

    def getvalue(self) -> str:
        return self.text

    def close(self):
        return

    @staticmethod
    def writable() -> bool:
        return True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __repr__(self):
        return self.text
