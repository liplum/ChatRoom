import keys
from ui.cmd_modes import common_hotkey
from ui.control.TextAreas import TextArea
from ui.control.buttons import button
from ui.control.checkboxes import checkbox
from ui.control.labels import label
from ui.control.xtbox import XtextWrapper
from ui.panel.DisplayBoards import DisplayBoard
from ui.panel.Stacks import Stack
from ui.tabs import *


class TestTab(tab):

    def __init__(self, client: IClient, tablist: tablist):
        super().__init__(client, tablist)
        self.t_label = label("Test")

        def switchFocusColor():
            b = self.t_button
            if b.IsFocused():
                b.OnLostFocused()
            else:
                b.OnFocused()
            self.db.IsVisible = not self.db.IsVisible

        self.t_button = button("Button", switchFocusColor)
        self.t_button.width = 10
        self.t_checkbox = checkbox(True)
        self.t_tbox = XtextWrapper(TextArea())
        self.t_tbox.Width = 40
        self.t_tbox.Height = auto
        self.t_tbox.InputList = "Test Input Box"
        self.db = DisplayBoard()
        self.db.Inner = self.t_tbox
        self.dx = 0
        self.dy = 0
        self.Main = DisplayBoard()
        self.StackPanel = Stack()
        self.StackPanel.add(self.db)
        self.StackPanel.add(self.t_label)
        self.StackPanel.add(self.t_checkbox)
        self.StackPanel.add(self.t_button)
        # self.tta = TestTabA(client, tablist)
        # c.AddControl(self.tta)
        self.ShowLogo = False
        self.IsShowVisualTreeOrVisibleVTree = True

        def switchShowLogo():
            self.ShowLogo = not self.ShowLogo

        self.Subscribe(UIElement.NeedRerenderEvent,
                       lambda sender, args: self.OnRenderContentChanged(self) or switchShowLogo())
        self.Main.Inner = self.StackPanel
        self.AddChild(self.Main)

    @property
    def title(self) -> str:
        return "Test"

    def Arrange(self, width: int, height: int) -> Tuple[int, int]:
        # self.StackPanel.Arrange(Width, Height)
        return width, height

    def Measure(self):
        pass

    def PaintOn(self, canvas: Canvas):
        w = StrWriter(canvas, x=40, autoWrap=True)
        if self.IsShowVisualTreeOrVisibleVTree:
            w.Write("Visual Tree:")
            w.NextLine()
            for v in PrintVTree(self):
                w.Write(v)
                w.NextLine()
        else:
            w.Write("Visible Tree:")
            w.NextLine()
            for v in PrintVisibleVTree(self):
                w.Write(v)
                w.NextLine()

        w.Write("Logical Tree:")
        w.NextLine()
        for v in PrintLTree(self):
            w.Write(v)
            w.NextLine()

        for e in PostItV(self.Main):
            e.Measure()
        self.Main.Arrange(40, 20)
        self.Main.PaintOn(Viewer.ByCanvas(canvas))

        # self.tta.PaintOn(Viewer(15, 2, 40, 20, canvas))
        if self.ShowLogo:
            for i in range(10, 20):
                for j in range(10, 20):
                    canvas.Char(i, j, "-")

    def on_input(self, char: chars.char) -> Generator:
        if chars.c_a == char:
            common_hotkey(char, self, self.client, self.tablist, self.win)
        elif chars.c_p == char:
            self.t_tbox.Raise(UIElement.NeedRerenderEvent, self.t_tbox, RoutedEventArgs(False))
        elif keys.k_enter == char:
            self.t_button.on_input(char)
        elif chars.c_m == char:
            self.IsShowVisualTreeOrVisibleVTree = not self.IsShowVisualTreeOrVisibleVTree
            self.OnRenderContentChanged(self)
        else:
            self.t_tbox.on_input(char)
        yield Finished
