import core.verify as verify
from core import operations as op
from core.shared import *
from net.msgs import register_result
from ui.cmd_modes import common_hotkey
from ui.control.xtbox import xtextbox
from ui.panel.Grids import gen_grid, Column
from ui.panel.Stacks import horizontal, Stack
from ui.panels import *
from ui.tab.popups import ok_popup_gen, waiting_popup
from ui.tab.shared import *
from ui.tabs import *
from utils import get

RR = register_result


class register_tab(tab):
    def __init__(self, client: IClient, tablist: tablist):
        super().__init__(client, tablist)
        self.last_tab: Optional[tab] = None
        self.network: "inetwork" = self.client.network
        grid = gen_grid(5, [Column(Auto), Column(15)])
        excepted_chars = {keys.k_enter, chars.c_tab_key}
        self.t_ip = xtextbox(exceptedChars=excepted_chars)
        self.t_port = xtextbox(onlyAllowedChars=number_keys)
        self.t_account = xtextbox(exceptedChars=excepted_chars)
        self.t_password = xtextbox(exceptedChars=excepted_chars)
        self.t_password_again = xtextbox(exceptedChars=excepted_chars)

        grid[0, 0] = i18n_label("tabs.$shared$.labels.server_ip")
        grid[1, 0] = i18n_label("tabs.$shared$.labels.server_port")
        grid[2, 0] = i18n_label("tabs.$shared$.labels.account")
        grid[3, 0] = i18n_label("tabs.$shared$.labels.password")
        grid[4, 0] = i18n_label("tabs.$shared$.labels.password_again")

        grid[0, 1] = self.t_ip
        grid[1, 1] = self.t_port
        grid[2, 1] = self.t_account
        grid[3, 1] = self.t_password
        grid[4, 1] = self.t_password_again

        self.t_ip.Width = 15
        self.t_port.Width = 5
        self.t_account.Width = 16
        self.t_password.Width = 16
        self.t_password_again.Width = 16

        self.t_ip.MaxInputCount = 63
        self.t_port.MaxInputCount = 5
        self.t_account.MaxInputCount = 16
        self.t_password.MaxInputCount = 16
        self.t_password_again.MaxInputCount = 16

        self.t_ip.space_placeholder = "_"
        self.t_port.space_placeholder = "_"
        self.t_account.space_placeholder = "_"
        self.t_password.space_placeholder = "_"
        self.t_password_again.space_placeholder = "_"

        self.t_port.InputList = "25000"

        dialog_stack = Stack()
        dialog_stack.Orientation = horizontal

        def on_cancel_pressed():
            if self.last_tab:
                tablist.replace(self, self.last_tab)
            else:
                tablist.remove(self)

        self._register_pressed = False

        def on_register_pressed():
            self._register_pressed = True

        register = i18n_button("controls.register", on_register_pressed)
        register.margin = 3
        cancel = i18n_button("controls.cancel", on_cancel_pressed)
        cancel.margin = 3

        dialog_stack.add(register)
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

    @property
    def title(self) -> str:
        return i18n.trans("tabs.register_tab.name")

    def register(self) -> Union[Tuple[server_token, str], str]:
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
        password_again = self.t_password_again.inputs.strip()
        if password != password_again:
            return "password_again"
        if self.last_tab:
            self.tablist.replace(self, self.last_tab)
        else:
            main_menu = self.win.newtab("main_menu_tab")
            self.tablist.replace(self, main_menu)
        op.register(self.network, token, account, password)
        return token, account

    def on_replaced(self, last_tab: "tab") -> Need_Release_Resource:
        self.last_tab = last_tab
        return False

    def on_input(self, char: chars.char) -> Generator:
        consumed = self.main.on_input(char)
        if not consumed:
            if keys.k_down == char or keys.k_enter == char or chars.c_tab_key == char:
                self.main.switch_to_first_or_default_item()
            else:
                consumed = not common_hotkey(char, self, self.client, self.tablist, self.win)
        if self._register_pressed:
            self._register_pressed = False
            result = self.register()
            if isinstance(result, tuple):
                token, account = result
                tip = split_textblock_words("tabs.register_tab.register_tip")
                p = self.new_popup(waiting_popup)
                p.title_getter = lambda: i18n.trans("tabs.register_tab.registering")
                p.words = tip
                p.tag = "register", token, account

                def on_p_state_changed(state):
                    if state == "succeed".lower():
                        p.title_getter = lambda: i18n.trans("controls.succeed")
                        tip = split_textblock_words("tabs.register_tab.succeed_tip", account=account, ip=token.ip,
                                                    port=token.port)
                    else:
                        reason = RR.map(state)
                        if reason:
                            p.title_getter = lambda: i18n.trans("controls.failed")
                            tip = split_textblock_words(f"tabs.register_tab.failed_tip.{reason}", account=account,
                                                        ip=token.ip,
                                                        port=token.port)
                    p.words = tip
                    p.reload()

                p.on_state_changed = on_p_state_changed
                yield p
                v = self.win.retrieve_popup(p)
                if self.last_tab:
                    self.tablist.replace(self, self.last_tab)
                else:
                    main_menu = self.win.newtab("main_menu_tab")
                    self.tablist.replace(self, main_menu)
                yield Finished
            elif isinstance(result, str):
                error = result
                tip = split_textblock_words(f"tabs.$account$.error_tip.{error}")
                p = self.new_popup(ok_popup_gen(tip, lambda: i18n.trans("controls.error")))
                yield p

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
        return t

    @classmethod
    def serializable(cls) -> bool:
        return True
