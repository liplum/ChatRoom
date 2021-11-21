import GLOBAL
import keys
from core import operations as op
from core.shared import to_server_token, uentity
from ui.controls import textbox
from ui.tab.chat import chat_tab
from ui.tab.shared import *
from ui.tabs import *
from ui.xtbox import xtextbox
from utils import fill_2d_array


class login_tab(tab):

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


add_tabtype("login_tab", login_tab)
