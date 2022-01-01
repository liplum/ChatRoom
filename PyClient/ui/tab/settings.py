from core.settings import *
from ui.cmd_modes import common_hotkey
from ui.control.checkboxes import checkbox
from ui.control.numeric_up_downs import numeric_up_down
from ui.control.textboxes import textbox
from ui.control.xtbox import xtextbox
from ui.panel.grids import gen_grid, column
from ui.panel.stacks import horizontal, stack
from ui.panels import *
from ui.tab.shared import *
from ui.tabs import *

OnSave = Callable[[], NoReturn]
Ctrl_OnSave = Tuple[control, OnSave]
OnSaveGen = Callable[[config, settings], Ctrl_OnSave]

_style2control: Dict[Style, OnSaveGen] = {}


def _add_control(style: Style, gen: Callable[[config, settings], Ctrl_OnSave]):
    _style2control[style] = gen


def config_control(tab: "settings_tab", config: config, settings: settings) -> Ctrl_OnSave:
    if not config.is_customizable:
        raise ValueError(config.key)
    style = config.prop.style
    if style in _style2control:
        return _style2control[style](config, settings)
    else:
        raise KeyError(config.key)


class settings_tab(tab):

    def __init__(self, client: iclient, tablist: tablist):
        super().__init__(client, tablist)
        self.last_tab = None
        self.ctrl2on_save = {}
        main = stack()
        main.on_content_changed.Add(lambda _: self.on_content_changed(self))
        main.left_margin = 3
        self.main = main
        main.switch_to_first_or_default_item()
        save = i18n_button("controls.save", self.save_configs)
        save.width = 10
        self.b_save = save

        cancel = i18n_button("controls.cancel", self.quit_tab)
        cancel.width = 10
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

    def on_input(self, char: chars.char) -> Generator:
        consumed = self.main.on_input(char)
        if not consumed:
            if keys.k_down == char or keys.k_enter == char or chars.c_tab_key == char:
                self.main.switch_to_first_or_default_item()
            else:
                consumed = not common_hotkey(char, self, self.client, self.tablist, self.win)
        yield Finished

    def on_replaced(self, last_tab: "tab") -> Need_Release_Resource:
        self.last_tab = last_tab
        return False


def _Style_CheckBox(config: config, settings: settings) -> Ctrl_OnSave:
    prop = config.prop
    init_value = settings[config.key]
    c = checkbox(init_value, theme=turn_on_off_check_theme)

    def on_checkbox_save():
        checked = c.checked
        if checked is not None:
            try:
                prop.new_value_callback(settings, checked)
            except ValueInvalidError as vie:
                pass

    return c, on_checkbox_save


_add_control(Style.CheckBox, _Style_CheckBox)


def _gen_on_textbox_save(config: config, settings: settings, prop: prop, tbox: textbox):
    def on_textbox_save():
        inputs = tbox.inputs
        final = config.convert_to(inputs)
        try:
            prop.new_value_callback(settings, final)
        except ValueInvalidError as vie:
            pass

    return on_textbox_save


def _Style_AnyString(config: config, settings: settings) -> Ctrl_OnSave:
    prop = config.prop
    init_value = settings[config.key]
    c = xtextbox()
    c.input_list = init_value
    return c, _gen_on_textbox_save(config, settings, prop, c)


_add_control(Style.AnyString, _Style_AnyString)


def _Style_OnlyNumber(config: config, settings: settings) -> Ctrl_OnSave:
    prop = config.prop
    init_value = settings[config.key]
    c = xtextbox(onlyAllowedChars=number_keys)
    c.input_list = str(init_value)
    return c, _gen_on_textbox_save(config, settings, prop, c)


_add_control(Style.OnlyNumber, _Style_OnlyNumber)


def _Style_OnlyAlphabet(config: config, settings: settings) -> Ctrl_OnSave:
    prop = config.prop
    init_value = settings[config.key]
    c = xtextbox(onlyAllowedChars=alphabet_keys)
    c.input_list = init_value
    return c, _gen_on_textbox_save(config, settings, prop, c)


_add_control(Style.OnlyAlphabet, _Style_OnlyAlphabet)


def _Style_OnlyNumberAlphabet(config: config, settings: settings) -> Ctrl_OnSave:
    prop = config.prop
    init_value = settings[config.key]
    c = xtextbox(onlyAllowedChars=number_alphabet_keys)
    c.input_list = init_value
    return c, _gen_on_textbox_save(config, settings, prop, c)


_add_control(Style.OnlyNumberAlphabet, _Style_OnlyNumberAlphabet)


def _Style_NumericUpDown(config: config, settings: settings) -> Ctrl_OnSave:
    prop = config.prop
    init_value = settings[config.key]
    d = prop.extra_data
    c = numeric_up_down(d["min"], d["max"])
    c.number = init_value

    def on_numeric_up_down_save():
        number = c.number
        if number is not None:
            try:
                prop.new_value_callback(settings, number)
            except ValueInvalidError as vie:
                pass

    return c, on_numeric_up_down_save


_add_control(Style.NumericUpDown, _Style_NumericUpDown)
