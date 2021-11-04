from core.chats import *
from net.networks import msg
from utils import get, not_none, to_seconds


class authentication(msg):
    name = "Authentication"

    def read(self, json):
        pass

    def write(self, json):
        pass

    @staticmethod
    def handle(self, context):
        pass


class authentication_result(msg):
    name = "AuthenticationResult"

    def read(self, json):
        pass

    def write(self, json):
        pass

    @staticmethod
    def handle(self, context):
        pass


class register_request(msg):
    name = "RegisterRequest"

    def read(self, json):
        pass

    def write(self, json):
        pass

    @staticmethod
    def handle(self, context):
        pass


class register_result(msg):
    name = "RegisterResult"

    def read(self, json):
        pass

    def write(self, json):
        pass

    @staticmethod
    def handle(self, context):
        pass


class chatting(msg):
    name = "Chatting"

    def read(self, json):
        user_id = get(json, "UserID")
        self.text = get(json, "Text")
        tiemstamp = get(json, "TimeStamp")
        chatting_room_id = get(json, "ChattingRoomID")
        if not not_none(user_id, self.text, tiemstamp, chatting_room_id):
            raise ValueError()
        self.room_id = roomid(chatting_room_id)
        self.user_id = userid(user_id)
        self.send_time = datetime.fromtimestamp(tiemstamp)

    def write(self, json):
        json["UserID"] = self.user_id.userid
        json["Text"] = self.text
        json["TimeStamp"] = to_seconds(self.send_time)
        json["ChattingRoomID"] = self.room_id.id

    @staticmethod
    def handle(self, context):
        client, channel, token = context
        client.receive_room_text(self.user_id, self.room_id, self.text, self.send_time)
