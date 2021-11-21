import GLOBAL
from core import operations as op
from core.shared import to_server_token, uentity
from ui.panels import *
from ui.tab.chat import chat_tab
from ui.tab.shared import *
from ui.tabs import *
from ui.xtbox import xtextbox
from utils import fill_2d_array, get


class login_tab2(tab):

    def __init__(self, client: "client", tablist: tablist):
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

        self.l_server_ip.width = 15
        self.l_server_port.width = 15
        self.l_account.width = 15
        self.l_password.width = 15

        self.t_server_ip: textbox = self.set(xtextbox(), 0, 1)
        self.t_server_port: textbox = self.set(xtextbox(), 1, 1)
        self.t_account: textbox = self.set(xtextbox(), 2, 1)
        self.t_password: textbox = self.set(xtextbox(), 3, 1)

        self.t_server_ip.space_placeholder = "_"
        self.t_server_ip.width = 16
        self.t_server_ip.max_inputs_count = 15

        self.t_server_port.input_list = "25000"
        self.t_server_port.space_placeholder = "_"
        self.t_server_port.end()
        self.t_server_port.width = 8
        self.t_server_port.max_inputs_count = 7

        self.t_account.space_placeholder = "_"
        self.t_account.width = 16
        self.t_account.max_inputs_count = 15

        self.t_password.space_placeholder = "_"
        self.t_password.width = 16
        self.t_password.max_inputs_count = 15

        self._focused: Optional[CTRL] = None

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
        return self._focused

    @focused.setter
    def focused(self, value: Optional[CTRL]):
        if self._focused == value:
            return
        if self._focused:
            self._focused.on_lost_focus()
        self._focused = value
        if value and value.focusable:
            value.on_focused()
        # TODO:Change this
        self.client.mark_dirty()

    def mark_dirt(self):
        self.client.mark_dirty()

    def set(self, control: control, i: int, j: int) -> T:
        self.container[i][j] = control
        control.on_content_changed.add(lambda _: self.mark_dirt())
        control.in_container = True
        return control

    def login(self):
        ip = self.t_server_ip.inputs.strip()
        port = self.t_server_port.inputs.strip()
        full = f"{ip}:{port}" if port != "" else ip
        account = self.t_account.inputs.strip()
        password = self.t_password.inputs.strip()
        token = to_server_token(full)
        if token:
            chat = chat_tab(self.client, self.tablist)
            chat.connect(token)
            chat.user_info = uentity(token, account)
            self.tablist.replace(self, chat)
            op.login(self.network, token, account, password)

    def on_input(self, char: chars.char):
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
            f: ctrl.control = self.focused
            consumed = False
            if f:
                consumed = f.on_input(char)

    def draw_on(self, buf: buffer):
        for i in range(self.container_row):
            buf.addtext("\t", end="")
            for j in range(self.container_column):
                ct = self.container[i][j]
                if ct:
                    ct.draw_on(buf)
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


# add_tabtype("login_tab", login_tab2)


class login_tab(tab):

    def __init__(self, client: "client", tablist: tablist):
        super().__init__(client, tablist)
        self.network: i_network = self.client.network
        grid = gen_grid(4, [column(auto), column(15)])
        excepted_chars = {keys.k_enter, chars.c_tab_key}
        self.t_ip = xtextbox(excepted_chars=excepted_chars)
        self.t_port = xtextbox(excepted_chars=excepted_chars)
        self.t_account = xtextbox(excepted_chars=excepted_chars)
        self.t_password = xtextbox(excepted_chars=excepted_chars)

        grid[0, 0] = i18n_label("tabs.login_tab.labels.server_ip")
        grid[1, 0] = i18n_label("tabs.login_tab.labels.server_port")
        grid[2, 0] = i18n_label("tabs.login_tab.labels.account")
        grid[3, 0] = i18n_label("tabs.login_tab.labels.password")

        grid[0, 1] = self.t_ip
        grid[1, 1] = self.t_port
        grid[2, 1] = self.t_account
        grid[3, 1] = self.t_password

        self.t_ip.width = 15
        self.t_port.width = 5
        self.t_account.width = 16
        self.t_password.width = 16

        self.t_ip.max_inputs_count = 15
        self.t_port.max_inputs_count = 5
        self.t_account.max_inputs_count = 16
        self.t_password.max_inputs_count = 16

        self.t_ip.space_placeholder = "_"
        self.t_port.space_placeholder = "_"
        self.t_account.space_placeholder = "_"
        self.t_password.space_placeholder = "_"

        self.t_port.input_list = "25000"
        self.t_port.end()

        dialog_stack = stack()
        dialog_stack.orientation = horizontal

        def on_ok_pressed():
            self.login()

        def on_cancel_pressed():
            self.client.stop()

        ok = i18n_button("controls.ok", on_ok_pressed)
        cancel = i18n_button("controls.cancel", on_cancel_pressed)

        ok.margin = 2
        cancel.margin = 1

        dialog_stack.add(ok)
        dialog_stack.add(cancel)
        main = stack()
        self._main = main
        self._main.on_content_changed.add(lambda _: self.client.mark_dirty())
        main.add(grid)
        main.add(dialog_stack)
        grid.elemt_interval_w = 7
        left_margin = 9
        grid.left_margin = left_margin
        dialog_stack.left_margin = left_margin
        main.top_margin = 1

        main.switch_to_first_or_default_item()

    def login(self):
        ip = self.t_ip.inputs.strip()
        port = self.t_port.inputs.strip()
        full = f"{ip}:{port}" if port != "" else ip
        account = self.t_account.inputs.strip()
        password = self.t_password.inputs.strip()
        token = to_server_token(full)
        if token:
            chat = chat_tab(self.client, self.tablist)
            chat.connect(token)
            chat.user_info = uentity(token, account)
            self.tablist.replace(self, chat)
            op.login(self.network, token, account, password)

    @property
    def title(self) -> str:
        return i18n.trans("tabs.login_tab.name")

    def on_input(self, char: chars.char):
        consumed = self._main.on_input(char)
        if not consumed:
            if keys.k_down == char or keys.k_enter == char or chars.c_tab_key == char:
                self._main.switch_to_first_or_default_item()

    def draw_on(self, buf: buffer):
        self._main.draw_on(buf)

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
        t.t_ip.end()
        t.t_port.end()
        t.t_account.end()
        t.t_password.end()
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


add_tabtype("login_tab", login_tab)