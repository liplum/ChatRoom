from ui.control.textblocks import *
from ui.panels import *
from ui.tab.shared import *
from ui.tabs import *


class ok_popup(base_popup):

    def __init__(self, client: iclient, tablist: tablist):
        super().__init__(client, tablist)
        m = stack()
        self.main = m
        l_title = label(self.get_title)
        l_title.prop(stack.Horizontal_Alignment, align_left)
        m.add(l_title)

        m.on_content_changed.add(lambda _: self.on_content_changed(self))
        self._words: Words = []
        info = textblock(lambda: self._words)
        self.info = info
        m.add(info)
        b_ok = i18n_button("controls.ok", self._on_ok)
        b_ok.width = 5
        self.b_ok = b_ok
        m.add(b_ok)
        m.left_margin = 10
        m.switch_to_first_or_default_item()

    def _on_ok(self):
        self._Return(True)

    def on_input(self, char: chars.char) -> Generator:
        self.main.on_input(char)
        yield Finished

    def paint_on(self, buf: buffer):
        self.main.paint_on(buf)

    @property
    def words(self) -> Words:
        return self._words

    @words.setter
    def words(self, value: Words):
        self._words = value


class ok_cancel_popup(base_popup):

    def __init__(self, client: iclient, tablist: tablist):
        super().__init__(client, tablist)
        m = stack()
        self.main = m
        l_title = label(self.get_title)
        l_title.prop(stack.Horizontal_Alignment, align_left)
        m.add(l_title)

        m.on_content_changed.add(lambda _: self.on_content_changed(self))
        self._words: Words = []
        info = textblock(lambda: self._words)
        self.info = info
        m.add(info)
        info.width = 60
        button_stack = stack()
        button_stack.orientation = horizontal
        b_ok = i18n_button("controls.ok", self._on_ok)
        b_ok.width = 8
        button_stack.add(b_ok)
        b_cancel = i18n_button("controls.cancel", self._on_cancel)
        b_cancel.width = 8
        button_stack.add(b_cancel)
        button_stack.width = 20
        m.add(button_stack)
        m.left_margin = 10
        m.switch_to_first_or_default_item()

    def _on_ok(self):
        self._Return(True)

    def _on_cancel(self):
        self._Return(False)

    def on_input(self, char: chars.char) -> Generator:
        self.main.on_input(char)
        yield Finished

    def paint_on(self, buf: buffer):
        self.main.paint_on(buf)

    @property
    def words(self) -> Words:
        return self._words

    @words.setter
    def words(self, value: Words):
        self._words = value
