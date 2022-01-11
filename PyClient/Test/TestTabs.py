from ui.cmd_modes import common_hotkey
from ui.control.TextAreas import TextArea
from ui.control.buttons import button
from ui.control.checkboxes import checkbox
from ui.control.labels import label
from ui.control.xtbox import XtextWrapper
from ui.panel.AbstractContainers import AbstractContainer
from ui.panel.DisplayBoards import DisplayBoard
from ui.tabs import *


class TestTabA(tab):

    def __init__(self, client: IClient, tablist: tablist):
        super().__init__(client, tablist)
        c = AbstractContainer()
        self.t_container = c
        self.t_label = label("Test")
        self.t_button = button("Button", lambda: None)
        self.t_button.width = 10
        self.t_checkbox = checkbox(True)
        self.t_tbox = XtextWrapper(TextArea())
        self.t_tbox.on_content_changed.Add(lambda _: self.OnRenderContentChanged(self))
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
        self.AddChild(self.t_container)

        self.AddEventHandler(UIElement.NeedReRenderEvent, lambda sender, args: self.OnRenderContentChanged(self))

    @property
    def title(self) -> str:
        return "Test"

    def PaintOn(self, canvas: Canvas):
        w = StrWriter(canvas, autoWrap=True)
        for v in PrintVTree(self):
            w.Write(v)
            w.NextLine()

        w.NextLine()
        for v in PrintLTree(self):
            w.Write(v)
            w.NextLine()

    def on_input(self, char: chars.char) -> Generator:
        if chars.c_a == char:
            common_hotkey(char, self, self.client, self.tablist, self.win)
        elif chars.c_p == char:
            self.t_tbox.Raise(UIElement.NeedReRenderEvent, self.t_tbox, RoutedEventArgs(False))
        else:
            self.t_tbox.on_input(char)
        yield Finished


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
        self.t_tbox.on_content_changed.Add(lambda _: self.OnRenderContentChanged(self))
        self.t_tbox.width = 30
        self.t_tbox.height = auto
        self.t_tbox.InputList = "Test Input Box"
        self.db = DisplayBoard()
        self.db.Inner = self.t_tbox
        self.dx = 0
        self.dy = 0
        c.AddControl(self.t_button)
        c.AddControl(self.t_checkbox)
        c.AddControl(self.db)
        # self.tta = TestTabA(client, tablist)
        # c.AddControl(self.tta)
        self.AddChild(self.t_container)
        self.ShowLogo = False

        def switchShowLogo():
            self.ShowLogo = not self.ShowLogo

        self.AddEventHandler(UIElement.NeedReRenderEvent,
                             lambda sender, args: self.OnRenderContentChanged(self) or switchShowLogo())

    @property
    def title(self) -> str:
        return "Test"

    def PaintOn(self, canvas: Canvas):

        w = StrWriter(canvas, x=21, autoWrap=True)
        for v in PrintVTree(self):
            w.Write(v)
            w.NextLine()

        w.NextLine()
        for v in PrintLTree(self):
            w.Write(v)
            w.NextLine()

        for e in PostItV(self.db):
            e.Measure()
        self.db.Arrange(20, 20)
        self.db.PaintOn(canvas)

        # self.tta.PaintOn(Viewer(15, 2, 40, 20, canvas))
        if self.ShowLogo:
            for i in range(10, 20):
                for j in range(10, 20):
                    canvas.Char(i, j, "-")

    def on_input(self, char: chars.char) -> Generator:
        if chars.c_a == char:
            common_hotkey(char, self, self.client, self.tablist, self.win)
        elif chars.c_p == char:
            self.t_tbox.Raise(UIElement.NeedReRenderEvent, self.t_tbox, RoutedEventArgs(False))
        else:
            self.t_tbox.on_input(char)
        yield Finished
