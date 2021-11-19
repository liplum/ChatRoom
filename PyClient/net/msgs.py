import i18n
import ui.windows as ws
from core.shared import *
from net.networks import msg
from ui.outputs import CmdFgColor, tintedtxt
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
    k_OK = "OK"
    k_VCode = "VCode"
    k_Account = "Account"

    def read(self, json):
        self.OK = get(json, authentication_result.k_OK)
        self.vcode = get(json, authentication_result.k_VCode)
        self.account = get(json, authentication_result.k_Account)

    def write(self, json):
        json[authentication_result.k_OK] = self.OK
        json[authentication_result.k_Account] = self.account
        json[authentication_result.k_VCode] = self.VCode

    @staticmethod
    def handle(self: "authentication_result", context):
        client, channel, token, network = context
        win: ws.window = client.win
        if self.OK:
            tablist = win.tablist
            tab = ws.find_best_incomplete_chat_tab(tablist, token, self.account)
            if tab:
                if tab.user_info is None:
                    tab.user_info = uentity(token, self.account)
                info = tab.user_info
                info.vcode = self.vcode
            else:
                tab = win.new_chat_tab()
                # TODO:Change this
                tab.join(12345)
                tab.connect(token)
                tab.user_info = uentity(token, self.account, self.vcode)
        else:
            win.add_string(tintedtxt(i18n.trans(
                "users.authentication.failure", ip=token.ip, port=token.port, account=self.account
            ), fgcolor=CmdFgColor.Red))


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
    def handle(self: "register_result", context):
        pass


class chatting(msg):
    name = "Chatting"
    k_Account = "Account"
    k_Text = "Text"
    k_TimeStamp = "TimeStamp"
    k_ChattingRoomID = "ChattingRoomID"
    k_VCode = "VCode"

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
        self.vcode = get(json, chatting.k_VCode)

    def write(self, json):
        json[chatting.k_Account] = self.user_id
        json["UserID"] = self.user_id
        json[chatting.k_Text] = self.text
        json[chatting.k_TimeStamp] = to_seconds(self.send_time)
        json[chatting.k_ChattingRoomID] = self.room_id
        json[chatting.k_VCode] = self.vcode

    @staticmethod
    def handle(self: "chatting", context):
        client, channel, token, network = context
        client.receive_text(token, self.room_id, self.user_id, self.text, self.send_time)
