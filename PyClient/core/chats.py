class userid:
    def __init__(self, userid: str):
        self.userid = userid

    def __eq__(self, other):
        if isinstance(other, str):
            return self.userid == other
        elif isinstance(other, userid):
            return self.userid == other.userid
        return False

    def __hash__(self):
        return hash(self.userid)

    def __str__(self) -> str:
        return self.userid

    def __repr__(self):
        return self.userid


class roomid:
    def __init__(self, _id: int):
        self.id = _id

    def __eq__(self, other):
        if isinstance(other, int):
            return self.id == other
        elif isinstance(other, roomid):
            return self.id == other.id
        return False

    def __hash__(self):
        return hash(self.id)

    def __str__(self) -> str:
        return str(self.id)

    def __repr__(self):
        return self.id
