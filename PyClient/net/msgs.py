import ui.tab.chat as chat
from core.rooms import iroom_manager
from core.shared import *
from net.networks import msg, Context
from ui.core import *
from utils import get, not_none, to_seconds

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


def _fill_or_add_chat_tab(win: iwindow, tab: Optional[chat.chat_tab], token: server_token, account: userid,
                          room_id: roomid, vcode: int) -> chat.chat_tab:
    if tab:
        tab.user_info = uentity(token, account, vcode)
    else:
        tab = win.new_chat_tab()
        tab.user_info = uentity(token, account, vcode)
        win.tablist.add(tab)
    tab.connect(token)
    tab.join(room_id)
    tab.notify_authenticated()
    return tab


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
        win: iwindow = client.win
        # TODO:Change This
        """
        if self.OK:
            tablist = win.tablist
            tab = chat.find_best_incomplete(tablist, token, self.account, None)
            _fill_or_add_chat_tab(win, tab, token, self.account, 12345, self.vcode)
        else:
            win.add_string(tintedtxt(i18n.trans(
                "users.authentication.failure", ip=token.ip, port=token.port, account=self.account
            ), fgcolor=CmdFgColor.Red))
        """


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

    def read(self, json):
        pass

    def write(self, json):
        pass

    @staticmethod
    def handle(self: "register_result", context: Context):
        pass


class chatting(msg):
    name = "Chatting"
    channel = "Chatting"

    def read(self, json):
        account = get(json, k_Account)
        self.text = get(json, k_Text)
        tiemstamp = get(json, k_TimeStamp)
        room_id = get(json, k_ChatRoomID)
        if not not_none(account, self.text, tiemstamp, room_id):
            raise ValueError()
        self.room_id = room_id
        self.account = account
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
        win: iwindow = client.win
        tablist: tablist = win.tablist
        for room in rooms:
            room_id = room.info.room_id
            is_new = manager.add_room(token, room)
            if is_new:
                tab = chat.find_best_incomplete(tablist, token, account, room_id)
                _fill_or_add_chat_tab(win, tab, token, self.account, room_id, self.vcode)
            else:
                def predicate(t: "tab"):
                    if isinstance(t, chat.chat_tab):
                        return t.connected == token and t.joined == room_id and t.user_info.verified and \
                               t.user_info.account == account

                tab_i = tablist.find_first(predicate)
                if tab_i:
                    t,i = tab_i
                    t.user_info.vcode = self.vcode
                else:
                    tab = chat.find_best_incomplete(tablist, token, account, room_id)
                    _fill_or_add_chat_tab(win, tab, token, self.account, room_id, self.vcode)

