import i18n
import ui.tab.chat as chat
from core.rooms import iroom_manager
from core.shared import *
from net.networks import msg, Context
from ui.Core import *
from ui.outputs import CmdFgColor, tintedtxt
from ui.tab.chat import fill_or_add_chat_tab
from ui.tab.popups import waiting_popup, base_popup
from utils import get, to_seconds

k_Account = "Account"
k_Password = "Password"
k_Text = "Text"
k_TimeStamp = "TimeStamp"
k_ChatRoomID = "ChatRoomID"
k_Name = "Name"
k_ChatRoomName = "ChatRoomName"
k_VCode = "VCode"
k_OK = "OK"
k_Result = "Result"
k_AllJoined = "AllJoined"
k_Cause = "Cause"
k_Sender = "Sender"
k_Receiver = "Receiver"
k_From = "From"
k_To = "To"
k_RequestID = "RequestID"
k_FriendRequests = "FriendRequests"
k_Results = "Results"


class authentication_req(msg):
    name = "AuthenticationReq"

    channel = "User"

    def read(self, json):
        self.account = get(json, k_Account)
        self.password = get(json, k_Password)

    def write(self, json):
        json[k_Account] = self.account
        json[k_Password] = self.password


class authentication_result(msg):
    name = "AuthenticationResult"

    channel = "User"

    def read(self, json):
        self.OK = get(json, k_OK)
        self.vcode = get(json, k_VCode)
        self.account = get(json, k_Account)

    def write(self, json):
        json[k_OK] = self.OK
        json[k_Account] = self.account
        json[k_VCode] = self.VCode

    @staticmethod
    def handle(self: "authentication_result", context: Context):
        client, channel, token, network = context

        win: iwindow = client.App

        def find_waiting_popup(p: base_popup):
            if isinstance(p, waiting_popup):
                return p.tag[0] == "login" and p.tag[1] == token and p.tag[2] == self.account
            return False

        if self.OK:
            popup: waiting_popup = win.find_first_popup(find_waiting_popup)
            if popup:
                popup.notify(self.vcode)
            else:
                tablist = win.Tablist
                tab = chat.find_best_incomplete(tablist, token, self.account, None, self.vcode)
                fill_or_add_chat_tab(win, tab, token, self.account, None, self.vcode)
        else:
            popup: waiting_popup = win.find_first_popup(find_waiting_popup)
            if popup:
                popup.state = "failed".lower()
            else:
                win.add_string(tintedtxt(i18n.trans(
                    "users.authentication.failed", ip=token.ip, port=token.port, account=self.account
                ), fgcolor=CmdFgColor.Red))


class register_request(msg):
    name = "RegisterRequest"
    channel = "User"

    def read(self, json):
        self.account = get(json, k_Account)
        self.password = get(json, k_Password)

    def write(self, json):
        json[k_Account] = self.account
        json[k_Password] = self.password


class register_result(msg):
    name = "RegisterResult"
    channel = "User"
    Failed = -1
    NoFinalResult = 0
    Succeed = 1

    AccountOccupied = 0
    InvalidAccount = 1
    InvalidPassword = 2
    Forbidden = 3
    causes = {
        AccountOccupied: "account_occupied",
        InvalidAccount: "invalid_account",
        InvalidPassword: "invalid_password",
        Forbidden: "forbidden"
    }

    def read(self, json):
        self.account = get(json, k_Account)
        self.result = get(json, k_Result)
        if self.result == register_result.Failed:
            self.cause = get(json, k_Cause)

    def write(self, json):
        json[k_Account] = self.account
        json[k_Result] = self.result
        if self.result == register_result.Failed:
            json[k_Cause] = self.cause

    @staticmethod
    def map(failure_code) -> Optional[str]:
        if failure_code in register_result.causes:
            return register_result.causes[failure_code]
        else:
            return None

    @staticmethod
    def handle(self: "register_result", context: Context):
        client, channel, token, network = context
        win: iwindow = client.App

        def find_waiting_popup(p: base_popup):
            if isinstance(p, waiting_popup):
                return p.tag[0] == "register" and p.tag[1] == token and p.tag[2] == self.account
            return False

        if self.result == register_result.Succeed:
            popup: waiting_popup = win.find_first_popup(find_waiting_popup)
            if popup:
                popup.state = "succeed".lower()
            else:
                win.add_string(tintedtxt(i18n.trans(
                    "users.register.succeed", ip=token.ip, port=token.port, account=self.account
                ), fgcolor=CmdFgColor.Green))
        else:
            popup: waiting_popup = win.find_first_popup(find_waiting_popup)
            if popup:
                popup.state = self.cause
            else:
                reason = register_result.map(self.cause)
                if reason:
                    win.add_string(tintedtxt(i18n.trans(
                        f"users.register.failed.{reason}", ip=token.ip, port=token.port, account=self.account
                    ), fgcolor=CmdFgColor.Red))


class chatting(msg):
    name = "Chatting"
    channel = "Chatting"

    def read(self, json):
        self.account = get(json, k_Account)
        self.text = get(json, k_Text)
        tiemstamp = get(json, k_TimeStamp)
        room_id = get(json, k_ChatRoomID)
        self.room_id = room_id
        self.send_time = datetime.fromtimestamp(tiemstamp)
        self.vcode = get(json, k_VCode)

    def write(self, json):
        json[k_Account] = self.account
        json[k_Text] = self.text
        json[k_TimeStamp] = to_seconds(self.send_time)
        json[k_ChatRoomID] = self.room_id
        json[k_VCode] = self.vcode

    @staticmethod
    def handle(self: "chatting", context: Context):
        client, channel, token, network = context

        client.msg_manager.receive(token, self.room_id, (self.send_time, self.account, self.text))


class whisper(msg):
    name = "Whisper"
    channel = "Chatting"

    def read(self, json):
        self.sender = get(json, k_Sender)
        self.receiver = get(json, k_Receiver)
        self.text = get(json, k_Text)
        tiemstamp = get(json, k_TimeStamp)
        self.send_time = datetime.fromtimestamp(tiemstamp)
        self.vcode = get(json, k_VCode)

    def write(self, json):
        json[k_Sender] = self.sender
        json[k_Receiver] = self.receiver
        json[k_Text] = self.text
        json[k_TimeStamp] = to_seconds(self.send_time)
        json[k_VCode] = self.vcode

    @staticmethod
    def handle(self: "chatting", context: Context):
        client, channel, token, network = context

        # TODO:Support whisper
        client.msg_manager.receive(token, self.room_id, (self.send_time, self.account, self.text))


class join_room_req(msg):
    name = "JoinRoomReq"
    channel = "User"

    def read(self, json):
        self.account = get(json, k_Account)
        self.room_id = get(json, k_ChatRoomID)
        self.vcode = get(json, k_VCode)

    def write(self, json):
        json[k_Account] = self.account
        json[k_ChatRoomID] = self.room_id
        json[k_VCode] = self.vcode


class join_room_result(msg):
    name = "JoinRoomResult"
    channel = "User"
    NotFound = -2
    AlreadyJoined = -1
    Forbidden = 0
    Succeed = 1

    def read(self, json):
        self.account = get(json, k_Account)
        self.room_id = get(json, k_ChatRoomID)
        self.vcode = get(json, k_VCode)
        self.result = get(json, k_Result)

    def write(self, json):
        json[k_Account] = self.account
        json[k_ChatRoomID] = self.room_id
        json[k_VCode] = self.vcode
        json[k_Result] = self.result

    @staticmethod
    def handle(self: "join_room_result", context: Context):
        client, channel, token, network = context


class create_room_req(msg):
    name = "CreateRoomReq"
    channel = "User"

    def read(self, json):
        self.account = get(json, k_Account)
        self.room_name = get(json, k_ChatRoomName)
        self.vcode = get(json, k_VCode)

    def write(self, json):
        json[k_Account] = self.account
        json[k_ChatRoomName] = self.room_name
        json[k_VCode] = self.vcode


class create_room_result(msg):
    name = "CreateRoomResult"
    channel = "User"
    NotFound = -2
    AlreadyJoined = -1
    Forbidden = 0
    Succeed = 1

    def read(self, json):
        self.account = get(json, k_Account)
        self.room_id = get(json, k_ChatRoomID)
        self.vcode = get(json, k_VCode)
        self.result = get(json, k_Result)

    def write(self, json):
        json[k_Account] = self.account
        json[k_ChatRoomID] = self.room_id
        json[k_VCode] = self.vcode
        json[k_Result] = self.result

    @staticmethod
    def handle(self: "create_room_result", context: Context):
        client, channel, token, network = context


class joined_rooms_info(msg):
    name = "JoinedRoomsInfo"
    channel = "User"

    def read(self, json):
        self.account = get(json, k_Account)
        self.vcode = get(json, k_VCode)
        self.all_joined = get(json, k_AllJoined)

    def write(self, json):
        json[k_Account] = self.account
        json[k_VCode] = self.vcode
        json[k_AllJoined] = self.all_joined

    @staticmethod
    def handle(self: "joined_rooms_info", context: Context):
        client, channel, token, network = context

        manager: iroom_manager = client.container.resolve(iroom_manager)
        account = self.account
        rooms = []
        for room in self.all_joined:
            try:
                room_id = room[k_ChatRoomID]
                name = room[k_Name]
                rooms.append(chat_room(sr_info(token, room_id), name))
            except:
                pass
        win: iwindow = client.App
        tablist: tablist = win.Tablist
        for room in rooms:
            room_id = room.info.room_id
            is_new = manager.add_room(token, room)
            if is_new:
                tab = chat.find_best_incomplete(tablist, token, account, room_id, self.vcode)
                fill_or_add_chat_tab(win, tab, token, self.account, room_id, self.vcode)
            else:
                def predicate(t: "tab"):
                    if isinstance(t, chat.chat_tab):
                        return t.connected == token and t.joined == room_id and t.user_info.verified and \
                               t.user_info.account == account

                tab_i = tablist.find_first(predicate)
                if tab_i:
                    t, i = tab_i
                    t.user_info.vcode = self.vcode
                else:
                    tab = chat.find_best_incomplete(tablist, token, account, room_id, self.vcode)
                    fill_or_add_chat_tab(win, tab, token, self.account, room_id, self.vcode)


class add_friend_req(msg):
    name = "AddFriendReq"
    channel = "Friend"

    def read(self, json):
        self.from_account = get(json, k_From)
        self.to_account = get(json, k_To)
        self.vcode = get(json, k_VCode)

    def write(self, json):
        json[k_From] = self.from_account
        json[k_To] = self.to_account
        json[k_VCode] = self.vcode


class add_friend_reply(msg):
    name = "AddFriendReply"
    channel = "Friend"
    Null = 0
    Accept = 1
    Refuse = 2
    Dismiss = 3

    def read(self, json):
        self.account = get(json, k_Account)
        self.vcode = get(json, k_VCode)
        self.request_id = get(json, k_RequestID)
        self.result = get(json, k_Result)

    def write(self, json):
        json[k_Account] = self.account
        json[k_VCode] = self.vcode
        json[k_RequestID] = self.request_id
        json[k_Result] = self.result


class received_friend_requests_info(msg):
    name = "ReceivedFriendRequestsInfo"
    channel = "Friend"

    def read(self, json):
        self.account = get(json, k_Account)
        self.vcode = get(json, k_VCode)
        self.friend_requests = get(json, k_FriendRequests)

    def write(self, json):
        json[k_Account] = self.account
        json[k_VCode] = self.vcode
        json[k_FriendRequests] = self.friend_requests


class sent_friend_requests_results(msg):
    name = "SentFriendRequestsResults"
    channel = "Friend"

    def read(self, json):
        self.account = get(json, k_Account)
        self.vcode = get(json, k_VCode)
        self.results = get(json, k_Results)

    def write(self, json):
        json[k_Account] = self.account
        json[k_VCode] = self.vcode
        json[k_Results] = self.results
