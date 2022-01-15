import core.verify as verify
from core import operations as op
from core.shared import *
from ui.cmd_modes import common_hotkey
from ui.control.passwordboxes import passwordbox, spot
from ui.control.xtbox import xtextbox
from ui.panel.Grids import gen_grid, Column
from ui.panel.Stacks import horizontal, Stack
from ui.panels import *
from ui.tab.chat import chat_tab
from ui.tab.popups import waiting_popup, ok_popup_gen
from ui.tab.shared import *
from ui.tabs import *
from utils import get


class login_tab(tab):

    def __init__(self, client: IClient, tablist: tablist):
        super().__init__(client, tablist)
        self.last_tab: Optional[tab] = None
        self.network: i_network = self.client.network
        grid = gen_grid(4, [Column(Auto), Column(15)])
        excepted_chars = {keys.k_enter, chars.c_tab_key}
        self.t_ip = xtextbox(exceptedChars=excepted_chars)
        self.t_port = xtextbox(onlyAllowedChars=number_keys)
        self.t_account = xtextbox(exceptedChars=excepted_chars)
        self.t_password = passwordbox(exceptedChars=excepted_chars, theme=spot)

        grid[0, 0] = i18n_label("tabs.$shared$.labels.server_ip")
        grid[1, 0] = i18n_label("tabs.$shared$.labels.server_port")
        grid[2, 0] = i18n_label("tabs.$shared$.labels.account")
        grid[3, 0] = i18n_label("tabs.$shared$.labels.password")

        grid[0, 1] = self.t_ip
        grid[1, 1] = self.t_port
        grid[2, 1] = self.t_account
        grid[3, 1] = self.t_password

        self.t_ip.Width = 15
        self.t_port.Width = 5
        self.t_account.Width = 16
        self.t_password.width = 16

        self.t_ip.MaxInputCount = 63
        self.t_port.MaxInputCount = 5
        self.t_account.MaxInputCount = 16
        self.t_password.MaxInputCount = 16

        self.t_ip.space_placeholder = "_"
        self.t_port.space_placeholder = "_"
        self.t_account.space_placeholder = "_"
        self.t_password.space_placeholder = "_"

        self.t_port.InputList = "25000"

        dialog_stack = Stack()
        dialog_stack.Orientation = horizontal

        def on_cancel_pressed():
            if self.last_tab:
                tablist.replace(self, self.last_tab)
            else:
                tablist.remove(self)

        self._login_pressed = False

        def on_login_pressed():
            self._login_pressed = True

        ok = i18n_button("controls.ok", on_login_pressed)
        ok.margin = 3
        cancel = i18n_button("controls.cancel", on_cancel_pressed)
        cancel.margin = 3

        dialog_stack.add(ok)
        dialog_stack.add(cancel)
        dialog_stack.elemt_interval = 1

        main = Stack()
        self.main = main
        self.main.on_content_changed.Add(lambda _: self.on_content_changed(self))
        main.add(grid)
        main.add(dialog_stack)
        grid.elemt_interval_w = 7
        main.top_margin = 1
        main.left_margin = 7
        main.switch_to_first_or_default_item()

    def login(self) -> Union[Tuple[server_token, str], str]:
        ip = self.t_ip.inputs.strip()
        if not verify.ip(ip):
            return "ip"
        port = self.t_port.inputs.strip()
        full = f"{ip}:{port}" if port != "" else ip
        token = server_token.by(full)
        if token is None:
            return "token"
        account = self.t_account.inputs.strip()
        if not verify.account(account):
            return "account"
        password = self.t_password.inputs.strip()
        if not verify.password(password):
            return "password"
        chat = chat_tab(self.client, self.tablist)
        chat.connect(token)
        chat.user_info = uentity(token, account)
        op.login(self.network, token, account, password)
        return token, account

    def on_replaced(self, last_tab: "tab") -> Need_Release_Resource:
        self.last_tab = last_tab
        return False

    @property
    def title(self) -> str:
        return i18n.trans("tabs.login_tab.name")

    def on_input(self, char: chars.char) -> Generator:
        consumed = self.main.on_input(char)
        if not consumed:
            if keys.k_down == char or keys.k_enter == char or chars.c_tab_key == char:
                self.main.switch_to_first_or_default_item()
            else:
                consumed = not common_hotkey(char, self, self.client, self.tablist, self.win)
        if self._login_pressed:
            self._login_pressed = False
            result = self.login()
            if isinstance(result, tuple):
                token, account = result
                tip = split_textblock_words("tabs.login_tab.login_tip")
                p = self.new_popup(waiting_popup)
                p.title_getter = lambda: i18n.trans("tabs.login_tab.logging")
                p.words = tip
                p.tag = "login", token, account

                def on_p_state_changed(state):
                    if state == "failed".lower():
                        p.title_getter = lambda: i18n.trans("tabs.login_tab.failed")
                        tip = split_textblock_words("tabs.login_tab.failed_tip")
                        p.words = tip
                        p.reload()

                p.on_state_changed = on_p_state_changed
                yield p
                v = self.win.retrieve_popup(p)
                self.tablist.remove(self)
                yield Finished
            elif isinstance(result, str):
                error = result
                tip = split_textblock_words(f"tabs.$account$.error_tip.{error}")
                p = self.new_popup(ok_popup_gen(tip, lambda: i18n.trans("controls.error")))
                yield p

    def paint_on(self, buf: buffer):
        self.main.paint_on(buf)

    @classmethod
    def deserialize(cls, data: dict, client: "client", tablist: "tablist") -> "tab":
        ip = get(data, "ip")
        port = get(data, "port")
        account = get(data, "account")
        password = get(data, "password")
        if ip == "" and port == "" and account == "" and password == "":
            raise CannotRestoreTab(self)
        t = login_tab(client, tablist)
        t.t_ip.input_list = ip
        t.t_port.input_list = port
        t.t_account.input_list = account
        t.t_password.input_list = password
        return t

    @classmethod
    def serialize(cls, self: "login_tab") -> dict:
        ip = self.t_ip.inputs.strip()
        port = self.t_port.inputs.strip()
        account = self.t_account.inputs.strip()
        password = self.t_password.inputs.strip()
        if ip == "" and port == "" and account == "" and password == "":
            raise CannotStoreTab(self)
        d = {
            "ip": ip,
            "port": port,
            "account": account,
            "password": password
        }
        return d

    @classmethod
    def serializable(cls) -> bool:
        return True

    def reload(self):
        self.main.reload()


"""
class login_tab2(tab):

    def __init__(self, client: IClient, tablist: tablist):
        super().__init__(client, tablist)
        self.network: i_network = self.client.network
        self.container_row = 4
        self.container_column = 2
        self.container: List[List[CTRL]] = fill_2d_array(self.container_row, self.container_column, None)
        self.l_server_ip: label = self.set(
            i18n_label("tabs.login_tab.labels.server_ip"),
            0, 0)
        self.l_server_port: label = self.set(
            i18n_label("tabs.login_tab.labels.server_port"),
            1, 0)
        self.l_account: label = self.set(
            i18n_label("tabs.login_tab.labels.account"),
            2, 0)
        self.l_password: label = self.set(
            i18n_label("tabs.login_tab.labels.password"),
            3, 0)

        self.l_server_ip.tw = 15
        self.l_server_port.tw = 15
        self.l_account.tw = 15
        self.l_password.tw = 15

        self.t_server_ip: textbox = self.set(xtextbox(), 0, 1)
        self.t_server_port: textbox = self.set(xtextbox(), 1, 1)
        self.t_account: textbox = self.set(xtextbox(), 2, 1)
        self.t_password: textbox = self.set(xtextbox(), 3, 1)

        self.t_server_ip.space_placeholder = "_"
        self.t_server_ip.tw = 16
        self.t_server_ip.max_inputs_count = 15

        self.t_server_port.input_list = "25000"
        self.t_server_port.space_placeholder = "_"
        self.t_server_port.end()
        self.t_server_port.tw = 8
        self.t_server_port.max_inputs_count = 7

        self.t_account.space_placeholder = "_"
        self.t_account.tw = 16
        self.t_account.max_inputs_count = 15

        self.t_password.space_placeholder = "_"
        self.t_password.tw = 16
        self.t_password.max_inputs_count = 15

        self._isFocused: Optional[CTRL] = None

        self._textbox_index = 0
        self.textbox_index = 0

    @property
    def textbox_index(self) -> int:
        return self._textbox_index

    @textbox_index.setter
    def textbox_index(self, value: int):
        value = min(value, self.container_row - 1)
        value = max(value, 0)
        self._textbox_index = value
        self.focused = self.container[value][1]
        self.focused_index = (1, value)

    @property
    def focused(self) -> Optional[CTRL]:
        return self._isFocused

    @focused.setter
    def focused(self, value: Optional[CTRL]):
        if self._isFocused == value:
            return
        if self._isFocused:
            self._isFocused.on_lost_focus()
        self._isFocused = value
        if value and value.focusable:
            value.on_focused()
        # TODO:Change this
        self.client.mark_dirty()

    def mark_dirt(self):
        self.client.mark_dirty()

    def set(self, Control: Control, i: int, j: int) -> T:
        self.container[i][j] = Control
        Control.on_content_changed.add(lambda _: self.mark_dirt())
        Control.in_container = True
        return Control

    def login(self):
        ip = self.t_server_ip.inputs.strip()
        port = self.t_server_port.inputs.strip()
        full = f"{ip}:{port}" if port != "" else ip
        account = self.t_account.inputs.strip()
        password = self.t_password.inputs.strip()
        token = server_token.by(full)
        if token:
            chat = chat_tab(self.client, self.tablist)
            chat.connect(token)
            chat.user_info = uentity(token, account)
            self.tablist.replace(self, chat)
            op.login(self.network, token, account, password)

    def on_input(self, char: chars.char) -> Generator:
        if keys.k_up == char:
            self.textbox_index -= 1
        elif keys.k_down == char or chars.c_table == char:
            self.textbox_index += 1
        elif keys.k_enter == char:
            if self.textbox_index < self.container_row - 1:
                self.textbox_index += 1
            else:
                self.login()
        elif chars.c_esc == char:
            if isinstance(self.focused, textbox):
                tb: textbox = self.focused
                tb.clear()
        else:
            f: ctrl.Control = self.focused
            consumed = False
            if f:
                consumed = f.on_input(char)
        yield Finished

    def paint_on(self, buf: buffer):
        for i in range(self.container_row):
            buf.addtext("\t", end="")
            for j in range(self.container_column):
                ct: Control = self.container[i][j]
                if ct:
                    ct.paint_on(buf)
                buf.addtext("  ", end="")
            buf.addtext()

        if GLOBAL.DEBUG:
            buf.addtext()
            pos = self.focused_index
            pos = f"focused pos : ({pos[0]},{pos[1]})"
            buf.addtext(pos)
            if isinstance(self.focused, textbox):
                tb: textbox = self.focused
                info = f"cursor pos = {tb.cursor}\ninput count= {tb.input_count}\nfull inputs = \"{tb.inputs}\""
                buf.addtext(info)

    @property
    def title(self) -> str:
        return i18n.trans("tabs.login_tab.name")
"""
