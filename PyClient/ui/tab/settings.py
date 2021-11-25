from core.settings import *
from ui.cmd_modes import common_hotkey
from ui.control.checkboxes import checkbox
from ui.control.textboxes import textbox
from ui.panels import *
from ui.tab.shared import *
from ui.tabs import *
from ui.xtbox import xtextbox


def config_control(tab: "settings_tab", config: config, settings: settings) -> Tuple[control, Callable[[], NoReturn]]:
    if not config.is_customizable:
        raise ValueError(config.key)
    prop = config.prop
    style = prop.style
    init_value = settings[config.key]
    if style == Style.CheckBox:
        c = checkbox(init_value, theme=turn_on_off_check_theme)

        def on_checkbox_save():
            checked = c.checked
            if checked is not None:
                try:
                    prop.new_value_callback(settings, checked)
                except ValueInvalidError as vie:
                    pass

        return c, on_checkbox_save
    else:
        def gen_on_textbox_save(tbox: textbox):
            def on_textbox_save():
                inputs = tbox.inputs
                try:
                    prop.new_value_callback(settings, inputs)
                except ValueInvalidError as vie:
                    pass

            return on_textbox_save
    if style == Style.AnyString:
        c = xtextbox()
        c.input_list = init_value
        return c, gen_on_textbox_save(c)
    elif style == Style.OnlyNumber:
        c = xtextbox(only_allowed_chars=number_keys)
        c.input_list = init_value
        return c, gen_on_textbox_save(c)
    elif style == Style.OnlyAlphabet:
        c = xtextbox(only_allowed_chars=alphabet_keys)
        c.input_list = init_value
        return c, gen_on_textbox_save(c)
    elif style == Style.OnlyAlphabet:
        c = xtextbox(only_allowed_chars=number_alphabet_keys)
        c.input_list = init_value
        return c, gen_on_textbox_save(c)
    else:
        raise ValueError(config.key)


class settings_tab(tab):

    def __init__(self, client: iclient, tablist: tablist):
        super().__init__(client, tablist)
        self.win = self.client.win
        self.last_tab = None
        self.ctrl2on_save = {}
        # settings = gen_grid(4, [column(30), column(10)])
        main = stack()
        main.on_content_changed.add(lambda _: self.on_content_changed(self))
        main.left_margin = 3
        self.main = main
        # settings[0, 0] = i18n_label("settings.RestoreTabWhenRestart")
        # settings[0, 1] = checkbox(True, theme=turn_on_off_check_theme)
        # settings.elemt_interval_w = 4
        # main.add(settings)
        main.switch_to_first_or_default_item()
        save = i18n_button("controls.save", self.save_configs)
        self.b_save = save

        cancel = i18n_button("controls.cancel", self.quit_tab)
        self.b_cancel = cancel
        save_cancel = stack()
        save_cancel.orientation = horizontal
        save_cancel.add(save)
        save_cancel.add(cancel)
        self.save_cancel = save_cancel

    def save_configs(self):
        for ctrl, on_save in self.ctrl2on_save.items():
            on_save()
        self.quit_tab()

    def quit_tab(self):
        if self.last_tab:
            self.tablist.replace(self, self.last_tab)
        else:
            self.tablist.remove(self)

    def on_added(self):
        main = self.main
        main.clear()
        self.ctrl2on_save = {}
        customizable_configs = all_customizable()
        rows = len(customizable_configs)
        settings = gen_grid(rows, [column(30), column(15)])
        settings.elemt_interval_w = 4
        configs = entity()
        for i, entry in enumerate(customizable_configs.items()):
            key, config = entry
            settings[i, 0] = i18n_label(f"settings.{key}")
            c, on_save = config_control(self, config, configs)
            settings[i, 1] = c
            self.ctrl2on_save[c] = on_save
        main.add(settings)
        main.add(self.save_cancel)
        main.switch_to_first_or_default_item()

    @property
    def title(self) -> str:
        return i18n.trans("tabs.settings_tab.name")

    def paint_on(self, buf: buffer):
        self.main.paint_on(buf)

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

    def on_replaced(self, last_tab: "tab") -> Need_Release_Resource:
        self.last_tab = last_tab
        return False
