from ui.control.textblocks import *
from ui.panel.stacks import align_left, horizontal, stack
from ui.tab.shared import *
from ui.tabs import *

_button_width = 8
_info_width = 50
_main_left_margin = 10


class text_popup(base_popup):

    def __init__(self, client: iclient, tablist: tablist):
        super().__init__(client, tablist)
        self.main: Optional[control] = None
        self.info: Optional[textblock] = None
        self._words: Words = []

    def on_input(self, char: chars.char) -> Generator:
        if self.main:
            self.main.on_input(char)
        yield Finished

    @property
    def words(self) -> Words:
        return self._words

    @words.setter
    def words(self, value: Words):
        if self._words != value:
            self._words = value
            if self.info:
                self.info.notify_content_changed()

    def paint_on(self, buf: buffer):
        if self.main:
            self.main.paint_on(buf)


class one_button_popup(text_popup):

    def __init__(self, client: iclient, tablist: tablist):
        super().__init__(client, tablist)
        self._button_return_value: Optional[Any] = None
        self._button_i18n_key = ""

    def on_added(self):
        m = stack()
        self.main = m
        m.on_content_changed.Add(lambda _: self.on_content_changed(self))

        l_title = label(self.get_title)
        l_title.prop(stack.Horizontal_Alignment, align_left)
        m.add(l_title)

        info = textblock(lambda: self._words)
        self.info = info
        info.width = _info_width
        m.add(info)

        b = i18n_button(self.button_i18n_key, self._on_press)
        b.width = _button_width
        m.add(b)

        m.left_margin = _main_left_margin
        m.switch_to_first_or_default_item()

    def _on_press(self):
        self._Return(self.button_return_value)

    @property
    def button_return_value(self) -> Optional[Any]:
        return self._button_return_value

    @button_return_value.setter
    def button_return_value(self, value: Optional[Any]):
        self._button_return_value = value

    @property
    def button_i18n_key(self) -> str:
        return self._button_i18n_key

    @button_i18n_key.setter
    def button_i18n_key(self, value: str):
        self._button_i18n_key = value


OneButtonPopupGen = Callable[[iclient, tablist], one_button_popup]
OneButtonPopupMetagen = Callable[[Words, TitleGetter], OneButtonPopupGen]


def one_button_popup_metagen(i18n_key: str, return_value: Any):
    def one_button_popup_gen(words: Words, title: TitleGetter) -> OneButtonPopupGen:
        def gen(client: iclient, tablist: tablist) -> one_button_popup:
            p = one_button_popup(client, tablist)
            p.words = words
            p.title_getter = title
            p.button_i18n_key = i18n_key
            p.button_return_value = return_value
            return p

        return gen

    return one_button_popup_gen


ok_popup_gen = one_button_popup_metagen("controls.ok", True)
cancel_popup_gen = one_button_popup_metagen("controls.cancel", False)


class ok_cancel_popup(text_popup):

    def __init__(self, client: iclient, tablist: tablist):
        super().__init__(client, tablist)
        button_stack = stack()
        button_stack.orientation = horizontal

        b_ok = i18n_button("controls.ok", self._on_ok)
        b_ok.width = _button_width
        button_stack.add(b_ok)

        b_cancel = i18n_button("controls.cancel", self._on_cancel)
        b_cancel.width = _button_width
        button_stack.add(b_cancel)

        button_stack.width = 20
        self.button_stack = button_stack

    def on_added(self):
        m = stack()
        self.main = m
        m.on_content_changed.Add(lambda _: self.on_content_changed(self))

        l_title = label(self.get_title)
        l_title.prop(stack.Horizontal_Alignment, align_left)
        m.add(l_title)

        info = textblock(lambda: self._words)
        self.info = info
        info.width = _info_width
        m.add(info)

        m.add(self.button_stack)
        m.left_margin = _main_left_margin
        m.switch_to_first_or_default_item()

    def _on_ok(self):
        self._Return(True)

    def _on_cancel(self):
        self._Return(False)


OnStateChanged = Optional[Callable[[Any], NoReturn]]


class waiting_popup(text_popup):
    def __init__(self, client: iclient, tablist: tablist):
        super().__init__(client, tablist)
        self._tag: Optional[Any] = None
        self._on_state_changed: OnStateChanged = None
        self._state = None

    def on_added(self):
        m = stack()
        self.main = m
        m.on_content_changed.Add(lambda _: self.on_content_changed(self))

        l_title = label(self.get_title)
        l_title.prop(stack.Horizontal_Alignment, align_left)
        m.add(l_title)

        info = textblock(lambda: self._words)
        self.info = info
        info.width = _info_width
        m.add(info)

        b_cancel = i18n_button("controls.cancel", self._on_press)
        b_cancel.width = _button_width
        m.add(b_cancel)

        m.left_margin = _main_left_margin
        m.switch_to_first_or_default_item()

    def _on_press(self):
        self._Return(False)

    def notify(self, value: Optional[Any] = None):
        self.need_refresh_instant = True
        self._Return(value)

    @property
    def tag(self) -> Optional[Any]:
        return self._tag

    @tag.setter
    def tag(self, value: Optional[Any]):
        if self._tag != value:
            self._tag = value

    @property
    def state(self) -> Any:
        return self._state

    @state.setter
    def state(self, value: Any):
        if self._state != value:
            self._state = value
            if self.on_state_changed:
                self.on_state_changed(value)

    @property
    def on_state_changed(self) -> OnStateChanged:
        return self._on_state_changed

    @on_state_changed.setter
    def on_state_changed(self, value: OnStateChanged):
        if self._on_state_changed != value:
            self._on_state_changed = value
