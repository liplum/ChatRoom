from core.chats import *
from core.shared import userid, roomid
from net.networks import msg
from utils import get, not_none, to_seconds


class authentication_req(msg):
    name = "AuthenticationReq"
    k_Account = "Account"
    k_Password = "Password"

    def read(self, json):
        self.account = get(json, register_request.k_Account)
        self.password = get(json, register_request.k_Password)

    def write(self, json):
        json[register_request.k_Account] = self.account
        json[register_request.k_Password] = self.password


class authentication_result(msg):
    name = "AuthenticationResult"
    k_OK="OK"
    k_VCode="VCode"

    def read(self, json):
        self.OK = get(json,authentication_result.k_OK)
        self.VCode = get(json,authentication_result.k_VCode)

    def write(self, json):
        json[authentication_result.k_OK] = self.OK
        json[authentication_result.k_VCode] = self.VCode

    @staticmethod
    def handle(self:"authentication_result", context):
        print(f"AuthenticationResult : {self.OK}")


class register_request(msg):
    name = "RegisterRequest"
    k_Account = "Account"
    k_Password = "Password"

    def read(self, json):
        self.account = get(json, register_request.k_Account)
        self.password = get(json, register_request.k_Password)

    def write(self, json):
        json[register_request.k_Account] = self.account
        json[register_request.k_Password] = self.password


class register_result(msg):
    name = "RegisterResult"

    def read(self, json):
        pass

    def write(self, json):
        pass

    @staticmethod
    def handle(self:"register_result", context):
        pass


class chatting(msg):
    name = "Chatting"
    k_Account = "Account"
    k_Text = "Text"
    k_TimeStamp = "TimeStamp"
    k_ChattingRoomID = "ChattingRoomID"

    def read(self, json):
        user_id = get(json, chatting.k_Account)
        if user_id is None:
            user_id = get(json, "UserID")
        self.text = get(json, chatting.k_Text)
        tiemstamp = get(json, chatting.k_TimeStamp)
        chatting_room_id = get(json, chatting.k_ChattingRoomID)
        if not not_none(user_id, self.text, tiemstamp, chatting_room_id):
            raise ValueError()
        self.room_id = roomid(chatting_room_id)
        self.user_id = userid(user_id)
        self.send_time = datetime.fromtimestamp(tiemstamp)

    def write(self, json):
        json[chatting.k_Account] = self.user_id.userid
        json["UserID"] = self.user_id.userid
        json[chatting.k_Text] = self.text
        json[chatting.k_TimeStamp] = to_seconds(self.send_time)
        json[chatting.k_ChattingRoomID] = self.room_id.id

    @staticmethod
    def handle(self:"chatting", context):
        client, channel, token, network = context
        client.receive_text(token, self.room_id, self.user_id, self.text, self.send_time)
