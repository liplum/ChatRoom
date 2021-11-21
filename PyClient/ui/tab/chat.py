import keys
import utils
from core.chats import i_msgmager
from core.settings import entity as settings
from core.shared import server_token, roomid, uentity, to_server_token, userid
from ui.cmd_modes import cmd_mode, cmd_hotkey_mode
from ui.k import kbinding
from ui.states import ui_state, ui_smachine
from ui.tab.shared import *
from ui.tabs import *
from ui.xtbox import xtextbox
from utils import get, all_none


class chat_tab(tab):
    def __init__(self, client: "client", tablist: tablist):
        super().__init__(client, tablist)
        self.textbox = xtextbox()
        self.history: List[str] = []
        self.max_display_line = 10
        self.fill_until_max = True
        self.msg_manager: i_msgmager = self.client.msg_manager
        self.network: "i_network" = self.client.network
        self.logger: "i_logger" = self.client.logger
        self.first_loaded = False
        self.focused = False
        self._unread_number = 0

        self._connected: Optional[server_token] = None
        self._joined: Optional[roomid] = None
        self._user_info: Optional[uentity] = None

        def set_chat_tab(state: ui_state) -> None:
            state.client = self.client
            state.textbox = self.textbox
            state.tablist = self.tablist
            state.tab = self
            if isinstance(state, cmd_mode):
                state.hotkey_cmd_mode_type = chat_cmd_hotkey_mode

        def gen_state(statetype: type) -> ui_state:
            if issubclass(statetype, ui_state):
                s = statetype()
                set_chat_tab(s)
                return s
            else:
                return statetype()

        self.sm = ui_smachine(state_pre=set_chat_tab, stype_pre=gen_state, allow_repeated_entry=False)
        self.sm.enter(cmd_mode)
        self.textbox.on_append.add(lambda b, p, c: client.mark_dirty())
        self.textbox.on_delete.add(lambda b, p, c: client.mark_dirty())
        self.textbox.on_cursor_move.add(lambda b, f, c: client.mark_dirty())
        self.textbox.on_list_replace.add(lambda b, f, c: client.mark_dirty())

    @property
    def unread_number(self) -> int:
        return self._unread_number

    @unread_number.setter
    def unread_number(self, value: int):
        if self._unread_number != value:
            self._unread_number = value
            self.client.mark_dirty()

    def send_text(self):
        info = self.user_info
        if self.connected and self.joined and info:
            if info.verified:
                inputs = self.textbox.inputs
                self.client.send_text(info, self.joined, inputs)
            else:
                self.add_string(i18n.trans("tabs.chat_tab.account_unverified", account=info.uid, ip=self.connected.ip))
        else:
            self.logger.error(f"[Tab][{self}]Haven't connected a server yet.")
        self.textbox.clear()

    @property
    def joined(self) -> Optional[roomid]:
        return self._joined

    def join(self, value):
        self._joined = value
        self.client.mark_dirty()

    @property
    def connected(self) -> Optional[server_token]:
        return self._connected

    def connect(self, server_token):
        if not self.network.is_connected(server_token):
            try:
                self.network.connect(server_token, strict=True)
            except:
                self.logger.error(f"[Tab][{self}]Cannot connect the server {server_token}")
                return
        self._connected = server_token
        self.client.mark_dirty()
        # self.logger.error(f"[Tab][{self}]Cannot access a unconnected/disconnected server.")

    @property
    def user_info(self) -> Optional[uentity]:
        return self._user_info

    @user_info.setter
    def user_info(self, value: Optional[uentity]):
        self._user_info = value
        self.client.mark_dirty()

    @property
    def authenticated(self) -> bool:
        return self.connected and self.user_info and self.user_info.verified

    def _add_msg(self, time, uid, text):
        configs = settings()
        date_format = configs.DateFormat
        self.history.append(f"{time.strftime(date_format)}\n  {uid}:  {text}")

    def first_load(self):
        self.history = []
        if self.connected and self.joined:
            li = self.msg_manager.load_until_today(self.connected, self.joined, self.max_display_line)
            for time, uid, text in li:
                self._add_msg(time, uid, text)
        self.first_loaded = True

    def draw_on(self, buf: buffer):
        if not self.first_loaded:
            self.first_load()

        self.render_connection_info(buf)
        buf.addtext(self.distext)
        self.sm.draw_on(buf)
        buf.addtext(self.textbox.distext)

    def render_connection_info(self, buf: buffer):
        if self.connected:
            if self.joined:
                tip = i18n.trans('tabs.chat_tab.joined',
                                 ip=self.connected.ip, port=self.connected.port, room_id=self.joined)
            else:
                tip = i18n.trans('tabs.chat_tab.connected',
                                 ip=self.connected.ip, port=self.connected.port)
        else:
            tip = i18n.trans('tabs.chat_tab.no_connection')
        buf.addtext(text=tip, bkcolor=CmdBkColor.White, fgcolor=CmdFgColor.Black, end='\n')

    @property
    def distext(self) -> str:
        if len(self.history) < self.max_display_line:
            displayed = self.history
            have_rest = True
        else:
            displayed = self.history[-self.max_display_line:]
            have_rest = False

        if have_rest and self.fill_until_max:
            with StringIO() as s:
                s.write(utils.compose(displayed, connector="\n"))
                displayed_len = len(displayed)
                s.write(utils.fill("", "\n", self.max_display_line - displayed_len))
                return s.getvalue()
        else:
            return utils.compose(displayed, connector="\n")

    def on_input(self, char):
        self.sm.on_input(char)

    @property
    def title(self) -> str:
        if self.connected and self.joined:
            badge = ""
            if self.user_info:
                if self.user_info.verified:
                    if self.unread_number > 0:
                        badge = f"[{self.unread_number}]"
                else:
                    badge = f"[{i18n.trans('tabs.chat_tab.badge.unverified')}]"
            else:
                badge = f"[{i18n.trans('tabs.chat_tab.badge.unlogin')}]"
            return f"{badge}{str(self.joined)}"
        return i18n.trans("tabs.chat_tab.name")

    def add_string(self, string: str):
        self.history.append(string)

    def on_added(self):
        self.msg_manager.on_received.add(self._on_received_msg)

    def _on_received_msg(self, manager, server, room_id, msg_unit):
        if server == self.connected and room_id == self.joined:
            time, uid, text = msg_unit
            self._add_msg(time, uid, text)
            if not self.focused:
                self.unread_number += 1

    def on_removed(self):
        self.msg_manager.on_received.remove(self._on_received_msg)

    @classmethod
    def deserialize(cls, data: dict, client: "client", tablist: "tablist") -> "chat_tab":
        server = get(data, "server")
        room_id = get(data, "room_id")
        account = get(data, "account")
        server = to_server_token(server)
        if all_none(server, room_id, account):
            raise CannotRestoreTab(chat_tab)

        t = chat_tab(client, tablist)
        if server:
            t.connect(server)
            if account:
                t.user_info = uentity(server, account)
        if room_id:
            t.join(room_id)
        return t

    @classmethod
    def serialize(cls, self: "chat_tab") -> dict:
        if all_none(self.connected, self.joined, self.user_info):
            raise CannotStoreTab(self)
        d = {
            "server": f"{self.connected.ip}:{self.connected.port}" if self.connected else None,
            "room_id": self.joined if self.joined else None,
            "account": self.user_info.uid if self.user_info else None
        }
        return d

    def on_focused(self):
        self.focused = True
        self.unread_number = 0

    def on_lost_focus(self):
        self.focused = False

    @classmethod
    def serializable(cls) -> bool:
        return True

    def __str__(self) -> str:
        c = f" {self.connected.ip}:{self.connected.port}" if self.connected else ""
        j = f"-{self.joined}" if self.joined else ""
        a = f"-{self.user_info.uid}" if self.user_info else ""
        return f"<chat_tab{c}{j}{a}>"

    def __hash__(self):
        account = self.user_info.uid if self.user_info else None
        return hash((self.connected, self.joined, account))

    def __eq__(self, other):
        if isinstance(other, chat_tab):
            return self.connected == other.connected and self.joined == other.joined and self.user_info == other.user_info
        else:
            return False


add_tabtype("chat_tab", chat_tab)


class chat_cmd_hotkey_mode(cmd_hotkey_mode):
    def __init__(self, mode: cmd_mode):
        super().__init__(mode)

    def on_input(self, char: chars.char) -> Is_Consumed:
        mode = self.mode
        tb = mode.textbox
        consumed = super().on_input(char)
        if not consumed:
            if mode.client.key_enter_text == char:
                mode.sm.enter(text_mode)
                return True
        return False


class text_mode(ui_state):

    def __init__(self):
        super().__init__()
        kbs = kbinding()
        self.kbs = kbs

        kbs.on_any = lambda c: self.textbox.append(c)
        kbs.bind(keys.k_enter, lambda c: self.tab.send_text())

    def on_en(self):
        self.client.mark_dirty()
        self.textbox.clear()

    def draw_on(self, buf: buffer):
        tip = utils.fillto(f"{i18n.trans('modes.text_mode.name')}:", " ", 40)
        buf.addtext(text=tip, fgcolor=CmdFgColor.White,
                    bkcolor=CmdBkColor.Blue,
                    end='\n')

    def on_input(self, char: chars.char):
        c = self.client
        if c.key_quit_text_mode == char:
            self.sm.enter(cmd_mode)
        elif True:
            self.kbs.trigger(char)


def find_best_incomplete_chat_tab(tablist: "tablist", server: server_token,
                                  account: userid) -> Optional["chat_tab"]:
    possible = []
    for t in tablist.it_all_tabs_is(chat_tab):
        if t.authenticated:
            continue
        ts = t.connected
        ta = t.user_info.uid if t.user_info else None
        if (ts and ts != server) or (ta and ta != account):
            continue
        else:
            possible.append(t)
    if len(possible) == 0:
        return None
    return possible[0]
