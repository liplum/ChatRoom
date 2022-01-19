from itertools import islice

import core.operations as op
import keys
from core.chats import imsgmager
from core.rooms import iroom_manager
from core.settings import settings, entity
from core.shared import *
from core.shared import server_token, userid, roomid, uentity
from ui.cmd_modes import cmd_mode, cmd_hotkey_mode
from ui.control.xtbox import xtextbox
from ui.k import kbinding
from ui.tab.shared import *
from ui.tabs import *
from ui.uistates import ui_state, ui_smachine
from utils import get, all_none


class item(ABC):
    @abstractmethod
    def distexts(self, configs: settings) -> Collection[str]:
        pass

    @property
    def height(self) -> int:
        return 1


class chat_item(item):
    def __init__(self, time: datetime, account: userid, text: str):
        super().__init__()
        self.time: datetime = time
        self.account: userid = account
        self.text: str = text

    def distexts(self, configs: settings) -> Collection[str]:
        date_format = configs.DateFormat
        return f"{self.time.strftime(date_format)}", f"  {self.account}:  {self.text}"

    @property
    def height(self) -> int:
        return 2

    def __repr__(self):
        configs = entity()
        date_format = configs.DateFormat
        return f"{self.time.strftime(date_format)}\n  {self.account}:  {self.text}"


class plain_item(item):
    def __init__(self, text: str):
        super().__init__()
        self.text = text

    def distexts(self, configs: settings) -> Collection[str]:
        return self.text,

    def __repr__(self):
        return self.text


_empty_tuple = ()


def _return_empty_tuple():
    return _empty_tuple


_empty_dict = {}


def _return_empty_dict():
    return _empty_dict


class i18n_item(item):
    def __init__(self, key: str, args: Callable[[], tuple] = _return_empty_tuple,
                 kwargs: Callable[[], dict] = _return_empty_dict):
        super().__init__()
        self.key = key
        self.args = args
        self.kwargs = kwargs

    def distexts(self, configs: settings) -> Collection[str]:
        return i18n.trans(self.key, *self.args(), **self.kwargs()),

    def __repr__(self):
        return i18n.trans(self.key, *self.args(), **self.kwargs())


TotalHeightUntilNow = int


class history_viewer(notifiable, painter):
    def __init__(self, max_height: int = 10, fill_until_max: bool = False):
        super().__init__()
        self.item_history: List[Tuple[item, TotalHeightUntilNow]] = []
        self.max_height = max_height
        self.total_height = 0
        self.fill_until_max = fill_until_max
        self._start = 0

    def add(self, item: item):
        self.total_height += item.height
        self.item_history.append((item, self.total_height))
        if self.total_height > self.max_height:
            self.scroll_down()

    def scroll_up(self, unit: int = 1):
        self.start -= abs(unit)

    def scroll_down(self, unit: int = 1):
        if len(self.item_history) > 0:
            cur, curh = self.item_history[self.start]
            d = self.total_height - curh
            if d >= self.max_height:
                self.start += abs(unit)

    def page_up(self):
        self.start -= self.max_height

    def page_down(self):
        res = self.start + self.max_height
        final = min(res, len(self.item_history) - self.reversed_displayable_item_count)
        self.start = final

    def paint_on(self, buf: buffer):
        configs = entity()
        maxh = self.max_height
        totalh = self.total_height
        render_slidebar = totalh > maxh
        with StringIO() as s:
            if render_slidebar:
                th = 0
                percent = maxh / totalh
                bar_height = max(int(maxh * percent), 0)
                cur, curh = self.item_history[self.start]
                bar_start = int(maxh * curh / totalh)
                bar_end = bar_start + bar_height
                index = 0
                for i, h in islice(self.item_history, self.start, None):
                    if th >= maxh:
                        break
                    for text in i.distexts(configs):
                        if th >= maxh:
                            break
                        th += 1
                        index += 1
                        if bar_start < index <= bar_end + 1:
                            s.write('█')
                        else:
                            s.write(' ')
                        s.write(text)
                        s.write('\n')
            else:
                for i, h in self.item_history:
                    for text in i.distexts(configs):
                        s.write(text)
                        s.write('\n')
                if self.fill_until_max:
                    rest = maxh - totalh
                    utils.repeatIO(s, '\n', rest)
            buf.addtext(s.getvalue())

    def clear(self):
        self.item_history = []

    @property
    def reversed_displayable_item_count(self):
        i = 0
        curh = 0
        maxh = self.max_height
        for item, h in reversed(self.item_history):
            if curh >= maxh:
                return i
            curh += item.height
            i += 1
        return i

    @property
    def start(self) -> int:
        return self._start

    @start.setter
    def start(self, value: int):
        value = max(value, 0)
        value = min(value, len(self.item_history) - 1)
        if self._start != value:
            self._start = value
            self.on_content_changed(self)


class chat_tab(tab):
    def __init__(self, client: IClient, tablist: Tablist):
        super().__init__(client, tablist)
        self.textbox = xtextbox()
        configs = entity()
        self.max_display_height = configs.MaxChatLine
        self.fill_until_max = True
        self.history: history_viewer = history_viewer(self.max_display_height, self.fill_until_max)
        self.history.on_content_changed.Add(lambda _: self.on_content_changed(self))
        self.msg_manager: imsgmager = self.client.msg_manager
        self.network: "inetwork" = self.client.network
        self.logger: "ilogger" = self.client.logger
        self.first_loaded = False
        self._unread_msg_number = 0
        self.room_manager: iroom_manager = self.client.container.resolve(iroom_manager)
        self._connected: Optional[server_token] = None
        self._joined: Optional[roomid] = None
        self._user_info: Optional[uentity] = None
        self._chat_room: Optional[chat_room] = None

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
        self.textbox.on_content_changed.Add(lambda _: self.on_content_changed(self))

    @property
    def unread_msg_number(self) -> int:
        return self._unread_msg_number

    @unread_msg_number.setter
    def unread_msg_number(self, value: int):
        if self._unread_msg_number != value:
            self._unread_msg_number = value
            self.on_content_changed(self)

    def send_text(self):
        info = self.user_info
        if self.connected and self.joined and info:
            if info.verified:
                inputs = self.textbox.inputs
                time = datetime.utcnow()
                op.send_text(self.network, self.user_info, self.joined, inputs, time)
                self.add_chat(self.connected, self.joined, (time, self.user_info.account, inputs), omit_self=False)
            else:
                self.add_string(
                    i18n.trans("tabs.chat_tab.account_unverified", account=info.account, ip=self.connected.ip))
        else:
            self.logger.error(f"[Tab][{self}]Haven't connected a server yet.")
        self.textbox.Clear()

    @property
    def joined(self) -> Optional[roomid]:
        return self._joined

    def join(self, value):
        if self._joined != value:
            self._joined = value
            if value is not None and self.connected:
                self._chat_room = self.room_manager.find_room_by_id(self.connected, value)
            self.on_content_changed(self)
            self.first_loaded = False

    @property
    def connected(self) -> Optional[server_token]:
        return self._connected

    def connect(self, server: server_token):
        if self.connected != server:
            if not self.network.is_connected(server):
                try:
                    self.network.connect(server, strict=True)
                except:
                    self.logger.error(f"[Tab][{self}]Cannot connect the server {server}")
                    return
            self._connected = server
            self.group_id = server
            self.on_content_changed(self)
            self.first_loaded = False
        # self.logger.error(f"[Tab][{self}]Cannot access a unconnected/disconnected server.")

    def notify_authenticated(self):
        if not self.first_loaded:
            self.first_load()
        self.on_content_changed(self)

    @property
    def user_info(self) -> Optional[uentity]:
        return self._user_info

    @user_info.setter
    def user_info(self, value: Optional[uentity]):
        if self.user_info != value:
            self._user_info = value
            self.on_content_changed(self)
            self.first_loaded = False

    @property
    def authenticated(self) -> bool:
        return self.connected and self.user_info and self.user_info.verified

    def add_msg(self, time, uid, text):
        t = chat_item(time, uid, text)
        self.history.add(t)

    def scroll_up(self, unit: int = 1):
        self.history.scroll_up(unit)

    def scroll_down(self, unit: int = 1):
        self.history.scroll_down(unit)

    def page_up(self):
        self.history.page_up()

    def page_down(self):
        self.history.page_down()

    def first_load(self):
        self.first_loaded = True
        self.history.clear()
        if self.connected and self.joined:
            li = self.msg_manager.load_until_today(self.connected, self.joined, None)
            for time, uid, text in li:
                self.add_msg(time, uid, text)

    def paint_on(self, buf: buffer):
        if not self.first_loaded:
            self.first_load()

        self.render_connection_info(buf)
        self.history.paint_on(buf)
        self.sm.paint_on(buf)
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

    def on_input(self, char) -> Generator:
        self.sm.on_input(char)
        yield Finished

    @property
    def title(self) -> str:
        if self.connected and self.joined:
            badge = ""
            if self.user_info:
                if self.user_info.verified:
                    if self.unread_msg_number > 0:
                        badge = f"[{self.unread_msg_number}]"
                else:
                    badge = f"[{i18n.trans('tabs.chat_tab.badge.unverified')}]"
            else:
                badge = f"[{i18n.trans('tabs.chat_tab.badge.unlogin')}]"
            room_name = self._chat_room.name if self._chat_room else self.joined
            return f"{badge}{str(room_name)}"
        return i18n.trans("tabs.chat_tab.name")

    def add_string(self, string: str):
        text = plain_item(string)
        self.history.add(text)

    def on_added(self):
        self.msg_manager.on_received.Add(self._on_received_msg)

    def _on_received_msg(self, manager: imsgmager, server: server_token, room_id: roomid, msg_unit: StorageUnit):
        self.add_chat(server, room_id, msg_unit, omit_self=True)

    def add_chat(self, server: server_token, room_id: roomid, msg_unit: StorageUnit, *, omit_self: bool = False):
        if server == self.connected and room_id == self.joined:
            time, uid, text = msg_unit
            if not omit_self or self.user_info.account != uid:
                self.add_msg(time, uid, text)
                if not self.is_focused:
                    self.unread_msg_number += 1

    def on_removed(self):
        self.msg_manager.on_received.Remove(self._on_received_msg)

    @classmethod
    def deserialize(cls, data: dict, client: "client", tablist: "Tablist") -> "chat_tab":
        server = get(data, "server")
        room_id = get(data, "room_id")
        account = get(data, "account")
        server = server_token.by(server)
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
        if self.connected:
            if self.connected.port == default_port:
                server = self.connected.ip
            else:
                server = f"{self.connected.ip}:{self.connected.port}"
        else:
            server = None
        d = {
            "server": server,
            "room_id": self.joined if self.joined else None,
            "account": self.user_info.account if self.user_info else None
        }
        return d

    def on_focused(self):
        super().on_focused()
        self.unread_msg_number = 0

    @classmethod
    def serializable(cls) -> bool:
        return False

    def __str__(self) -> str:
        c = f" {self.connected.ip}:{self.connected.port}" if self.connected else ""
        j = f"-{self.joined}" if self.joined else ""
        a = f"-{self.user_info.account}" if self.user_info else ""
        return f"<chat_tab{c}{j}{a}>"

    def equals(self, tab: "tab") -> bool:
        if isinstance(tab, chat_tab):
            return self.connected == tab.connected and self.joined == tab.joined and self.user_info == tab.user_info
        else:
            return False


class chat_cmd_hotkey_mode(cmd_hotkey_mode):
    def __init__(self, mode: cmd_mode):
        super().__init__(mode)

    def on_input(self, char: chars.char) -> IsConsumed:
        mode = self.mode
        tb = mode.textbox
        consumed = super().on_input(char)
        if not consumed:
            if mode.client.key_enter_text == char:
                mode.sm.enter(text_mode)
                return Consumed
        return NotConsumed


class text_mode(ui_state):
    tab: chat_tab

    def __init__(self):
        super().__init__()
        kbs = kbinding()
        self.kbs = kbs
        kbs.bind(keys.k_up, lambda c: self.tab.scroll_up())
        kbs.bind(keys.k_down, lambda c: self.tab.scroll_down())
        kbs.bind(keys.k_pgup, lambda c: self.tab.page_up())
        kbs.bind(keys.k_pgdown, lambda c: self.tab.page_down())
        kbs.on_any = lambda c: self.textbox.on_input(c)
        kbs.bind(keys.k_enter, lambda c: self.tab.send_text())

    def on_en(self):
        self.client.mark_dirty()
        self.textbox.Clear()

    def paint_on(self, buf: buffer):
        tip = utils.fillto(f"{i18n.trans('modes.text_mode.name')}:", " ", 40)
        buf.addtext(text=tip, fgcolor=CmdFgColor.White,
                    bkcolor=CmdBkColor.Blue,
                    end='\n')

    def on_input(self, char: chars.char) -> IsConsumed:
        c = self.client
        if c.key_quit_text_mode == char:
            self.sm.enter(cmd_mode)
            return True
        elif True:
            self.kbs.trigger(char)
            return True


def find_best_incomplete(tablist: "Tablist", server: server_token,
                         account: userid, room: Optional[roomid], vcode: Optional[int]) -> Optional["chat_tab"]:
    for t in tablist.it_all_tabs_is(chat_tab):
        if t.authenticated and t.user_info.vcode != vcode:
            continue
        ts = t.connected
        ta = t.user_info.account if t.user_info else None
        tr = t.joined
        if (ts and ts != server) or (ta and ta != account) or (tr and tr != room):
            continue
        else:
            return t
    return None


def fill_or_add_chat_tab(win: IApp, tab: Optional[chat_tab], token: server_token, account: userid,
                         room_id: Optional[roomid], vcode: int) -> chat_tab:
    if tab:
        tab.user_info = uentity(token, account, vcode)
    else:
        tab = win.new_chat_tab()
        tab.user_info = uentity(token, account, vcode)
        win.tablist.Add(tab)
    tab.connect(token)
    if room_id:
        tab.join(room_id)
    tab.notify_authenticated()
    return tab
