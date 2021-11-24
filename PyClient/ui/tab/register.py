from core import operations as op
from ui.cmd_modes import common_hotkey
from ui.panels import *
from ui.tab.shared import *
from ui.tabs import *
from ui.xtbox import xtextbox
from utils import get


class register_tab(tab):
    def __init__(self, client: iclient, tablist: tablist):
        super().__init__(client, tablist)
        self.win = self.client.win
        self.last_tab: Optional[tab] = None
        self.network: "inetwork" = self.client.network
        grid = gen_grid(5, [column(auto), column(15)])
        excepted_chars = {keys.k_enter, chars.c_tab_key}
        self.t_ip = xtextbox(excepted_chars=excepted_chars)
        self.t_port = xtextbox(only_allowed_chars=number_keys)
        self.t_account = xtextbox(excepted_chars=excepted_chars)
        self.t_password = xtextbox(excepted_chars=excepted_chars)
        self.t_password_again = xtextbox(excepted_chars=excepted_chars)

        grid[0, 0] = i18n_label("tabs.register_tab.labels.server_ip")
        grid[1, 0] = i18n_label("tabs.register_tab.labels.server_port")
        grid[2, 0] = i18n_label("tabs.register_tab.labels.account")
        grid[3, 0] = i18n_label("tabs.register_tab.labels.password")
        grid[4, 0] = i18n_label("tabs.register_tab.labels.password_again")

        grid[0, 1] = self.t_ip
        grid[1, 1] = self.t_port
        grid[2, 1] = self.t_account
        grid[3, 1] = self.t_password
        grid[4, 1] = self.t_password_again

        self.t_ip.width = 15
        self.t_port.width = 5
        self.t_account.width = 16
        self.t_password.width = 16
        self.t_password_again.width = 16

        self.t_ip.max_inputs_count = 63
        self.t_port.max_inputs_count = 5
        self.t_account.max_inputs_count = 16
        self.t_password.max_inputs_count = 16
        self.t_password_again.max_inputs_count = 16

        self.t_ip.space_placeholder = "_"
        self.t_port.space_placeholder = "_"
        self.t_account.space_placeholder = "_"
        self.t_password.space_placeholder = "_"
        self.t_password_again.space_placeholder = "_"

        self.t_port.input_list = "25000"
        self.t_port.end()

        dialog_stack = stack()
        dialog_stack.orientation = horizontal

        def on_cancel_pressed():
            if self.last_tab:
                tablist.replace(self, self.last_tab)
            else:
                tablist.remove(self)

        register = i18n_button("controls.register", self.register)
        register.margin = 3
        cancel = i18n_button("controls.cancel", on_cancel_pressed)
        cancel.margin = 3

        dialog_stack.add(register)
        dialog_stack.add(cancel)
        dialog_stack.elemt_interval = 1

        main = stack()
        self.main = main
        self.main.on_content_changed.add(lambda _: self.on_content_changed(self))
        main.add(grid)
        main.add(dialog_stack)
        grid.elemt_interval_w = 7
        main.top_margin = 1
        main.left_margin = 7
        main.switch_to_first_or_default_item()

    @property
    def title(self) -> str:
        return i18n.trans("tabs.register_tab.name")

    def register(self):
        account = self.t_account.inputs.strip()
        password = self.t_password.inputs.strip()
        password_again = self.t_password_again.inputs.strip()
        if account == "" or password == "" or password_again == "":
            return
        if password != password_again:
            return
        ip = self.t_ip.inputs.strip()
        port = self.t_port.inputs.strip()
        full = f"{ip}:{port}" if port != "" else ip
        token = server_token.by(full)
        if token:
            if self.last_tab:
                self.tablist.replace(self, self.last_tab)
            else:
                main_menu = self.win.newtab("main_menu_tab")
                self.tablist.replace(self, main_menu)
            op.register(self.network, token, account, password)

    def on_replaced(self, last_tab: "tab") -> Need_Release_Resource:
        self.last_tab = last_tab
        return False

    def on_input(self, char: chars.char) -> Is_Consumed:
        consumed = self.main.on_input(char)
        if consumed:
            return Consumed
        if not consumed:
            if keys.k_down == char or keys.k_enter == char or chars.c_tab_key == char:
                self.main.switch_to_first_or_default_item()
                return Consumed
            else:
                consumed = not common_hotkey(char, self, self.client, self.tablist, self.win)
                return consumed
        return Not_Consumed

    def paint_on(self, buf: buffer):
        self.main.paint_on(buf)

    def reload(self):
        self.main.reload()

    @classmethod
    def serialize(cls, self: "register_tab") -> dict:
        ip = self.t_ip.inputs.strip()
        port = self.t_port.inputs.strip()
        account = self.t_account.inputs.strip()
        password = self.t_password.inputs.strip()
        password_again = self.t_password_again.inputs.strip()
        if ip == "" and port == "" and account == "" and password == "" and password_again == "":
            raise CannotStoreTab(self)
        d = {
            "ip": ip,
            "port": port,
            "account": account,
            "password": password,
            "password_again": password_again
        }
        return d

    @classmethod
    def deserialize(cls, data: dict, client: "client", tablist: "tablist") -> "tab":
        ip = get(data, "ip")
        port = get(data, "port")
        account = get(data, "account")
        password = get(data, "password")
        password_again = get(data, "password_again")
        if ip == "" and port == "" and account == "" and password == "" and password_again == "":
            raise CannotRestoreTab(self)
        t = register_tab(client, tablist)
        t.t_ip.input_list = ip
        t.t_port.input_list = port
        t.t_account.input_list = account
        t.t_password.input_list = password
        t.t_password_again.input_list = password
        t.t_ip.end()
        t.t_port.end()
        t.t_account.end()
        t.t_password.end()
        t.t_password_again.end()
        return t

    @classmethod
    def serializable(cls) -> bool:
        return True
