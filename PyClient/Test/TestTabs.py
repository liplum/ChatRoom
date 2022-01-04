from ui.Controls import *
from ui.cmd_modes import common_hotkey
from ui.control.TextAreas import TextArea
from ui.control.buttons import button
from ui.control.checkboxes import checkbox
from ui.control.labels import label
from ui.control.xtbox import XtextWrapper
from ui.panel.AbstractContainers import AbstractContainer
from ui.panel.DisplayBoards import DisplayBoard
from ui.tabs import *


class TestTab(tab):

    def __init__(self, client: IClient, tablist: tablist):
        super().__init__(client, tablist)
        c = AbstractContainer()
        self.t_container = c
        self.t_label = label("Test")
        self.t_button = button("Button", lambda: None)
        self.t_button.width = 10
        self.t_checkbox = checkbox(True)
        self.t_tbox = XtextWrapper(TextArea())
        self.t_tbox.on_content_changed.Add(lambda _: self.OnContentChanged(self))
        self.t_tbox.width = 30
        self.t_tbox.height = auto
        self.db = DisplayBoard()
        self.db.Inner = self.t_tbox
        self.dx = 0
        self.dy = 0
        c.AddControl(self.t_label)
        c.AddControl(self.t_button)
        c.AddControl(self.t_checkbox)
        c.AddControl(self.t_tbox)
        c.AddControl(self.db)

    @property
    def title(self) -> str:
        return "Test"

    def PaintOn(self, canvas: Canvas):
        w = StrWriter(canvas, autoWrap=True)
        for v in PrintTreeV(self.t_container):
            w.Write(v)
            w.NextLine()
        """
        v = Viewer.ByCanvas(canvas)
        self.t_label.PaintOn(v.Sub(0, 0, v.Width, 1))
        self.t_button.PaintOn(v.Sub(0, 1, v.Width, 1))
        self.t_checkbox.PaintOn(v.Sub(0, 2, v.Width, 1))

        self.t_tbox.PaintOn(v.Sub(0, 3, 20, 8))
        dbX = self.dx
        dbY = self.dy + 5
        if dbX >= canvas.Width + 20 or dbX <= 0:
            self.dx = 0
            dbX = 0
        if dbY >= canvas.Height + 4 or dbY <= 0:
            self.dy = 0
            dbY = 0
        self.db.PaintOn(v.Sub(dbX, dbY, 20, 8))
        # self.dx += 1
        # self.dy += 1
        """

    def on_input(self, char: chars.char) -> Generator:
        if chars.c_a == char:
            common_hotkey(char, self, self.client, self.tablist, self.win)
        else:
            self.t_tbox.on_input(char)
        yield Finished
