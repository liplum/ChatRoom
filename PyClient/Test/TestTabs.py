from ui.cmd_modes import common_hotkey
from ui.control.buttons import button
from ui.control.checkboxes import checkbox
from ui.control.labels import label
from ui.control.xtbox import xtextbox
from ui.tabs import *


class TestTab(tab):

    def __init__(self, client: iclient, tablist: tablist):
        super().__init__(client, tablist)
        self.t_label = label("Test")
        self.t_button = button("Button", lambda: None)
        self.t_button.width = 10
        self.t_checkbox = checkbox()
        self.t_tbox = xtextbox()
        self.t_tbox.on_content_changed.Add(lambda _: self.on_content_changed(self))
        self.t_tbox.width = 10

    @property
    def title(self) -> str:
        return "Test"

    def PaintOn(self, canvas: Canvas):
        v = Viewer.ByCanvas(canvas)
        self.t_label.PaintOn(v.Sub(0, 0, v.Width, 1))
        self.t_button.PaintOn(v.Sub(0, 1, v.Width, 1))
        self.t_checkbox.PaintOn(v.Sub(0, 2, v.Width, 1))

        self.t_tbox.PaintOn(v.Sub(0, 3, v.Width, 3))

    def on_input(self, char: chars.char) -> Generator:
        if not self.t_tbox.on_input(char):
            common_hotkey(char, self, self.client, self.tablist, self.win)
        yield Finished
