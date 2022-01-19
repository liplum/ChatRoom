import keys
from ui.cmd_modes import common_hotkey
from ui.control.Buttons import Button
from ui.control.Checkboxes import Checkbox
from ui.control.Labels import Label
from ui.control.TextAreas import TextArea
from ui.control.xtbox import XtextWrapper
from ui.panel.DisplayBoards import DisplayBoard
from ui.panel.Grids import gen_grid, Column
from ui.panel.Stacks import Stack, OrientationType, AlignmentType
from ui.tabs import *


class TestTab(tab):

    def __init__(self, client: IClient, tablist: Tablist):
        super().__init__(client, tablist)
        self.t_label = Label("Test")

        def switchFocusColor():
            b = self.t_button
            if b.IsFocused:
                b.OnLostFocused()
            else:
                b.OnFocused()
            self.db.IsVisible = not self.db.IsVisible
            self.tablist.ShowTabBar = not self.tablist.ShowTabBar

        self.t_button = Button("Button", switchFocusColor)
        self.t_button.width = 10
        self.t_checkbox = Checkbox(True)
        self.t_tbox = XtextWrapper(TextArea())
        self.t_tbox.Width = 40
        # self.t_tbox.Height = 10
        self.t_tbox.Height = Auto
        self.t_tbox.InputList = "Test Input Box"
        self.db = DisplayBoard()
        self.db.Inner = self.t_tbox
        self.dx = 0
        self.dy = 0
        self.Main = DisplayBoard()
        self.StackPanel = Stack()
        self.grid = gen_grid(2, [Column()])
        self.grid[0, 0] = Button("GridButton", lambda: None)
        self.grid[1, 0] = Button("Grid2", lambda: None)
        self.StackPanel.Orientation = OrientationType.Vertical
        self.StackPanel.AddControl(self.db)
        self.StackPanel.AddControl(self.t_label)
        self.StackPanel.AddControl(self.t_checkbox)
        self.StackPanel.AddControl(self.t_button)

        # self.tta = TestTabA(client, Tablist)
        # c.AddControl(self.tta)
        self.ShowLogo = False
        self.IsShowVisualTreeOrVisibleVTree = True
        self.tick = 0

        def switchShowLogo():
            self.ShowLogo = not self.ShowLogo

        self.Subscribe(UIElement.NeedRerenderEvent,
                       lambda sender, args:
                       self.OnRenderContentChanged(self) or switchShowLogo())
        self.Main.Inner = self.StackPanel
        self.AddChild(self.Main)
        self.UseNewRender = True

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
            for v in PrintVTree(self.tablist):
                w.Write(v)
                w.NextLine()
        else:
            w.Write("Visible Tree:")
            w.NextLine()
            for v in PrintVisibleVTree(self.tablist):
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
        """
        import random
        w = random.randint(10,50)
        h = random.randint(10,50)
        self.OnRenderContentChanged(self)
        self.Main.Arrange(w, h)
        self.Main.PaintOn(
            Viewer.ByCanvas(canvas,
                            x=random.randint(0,20),
                            y=random.randint(0,5)))
        # self.tta.PaintOn(Viewer(15, 2, 40, 20, canvas))
        """
        if self.ShowLogo:
            for i in range(10, 20):
                for j in range(10, 20):
                    canvas.Char(i, j, "-")

    def on_input(self, char: chars.char) -> Generator:
        self.tick += 1
        if chars.c_a == char:
            common_hotkey(char, self, self.client, self.tablist, self.win)
        elif chars.c_p == char:
            self.t_tbox.Raise(UIElement.NeedRerenderEvent, self.t_tbox, RoutedEventArgs(False))
        elif keys.k_enter == char:
            self.t_button.on_input(char)
        elif chars.c_m == char:
            self.IsShowVisualTreeOrVisibleVTree = not self.IsShowVisualTreeOrVisibleVTree
            self.OnRenderContentChanged(self)
        elif keys.k_down == char:
            o = self.StackPanel.Orientation
            if o == OrientationType.Horizontal:
                self.StackPanel.Orientation = OrientationType.Vertical
            elif o == OrientationType.Vertical:
                self.StackPanel.Orientation = OrientationType.Horizontal
        elif keys.k_pgdown == char:
            if self.tick % 3 == 0:
                Stack.SetVerticalAlignment(self.t_button, AlignmentType.Left)
                Stack.SetHorizontalAlignment(self.t_button, AlignmentType.Top)
            elif self.tick % 3 == 1:
                Stack.SetVerticalAlignment(self.t_button, AlignmentType.Center)
                Stack.SetHorizontalAlignment(self.t_button, AlignmentType.Center)
            else:
                Stack.SetVerticalAlignment(self.t_button, AlignmentType.Right)
                Stack.SetHorizontalAlignment(self.t_button, AlignmentType.Bottom)
        else:
            self.t_tbox.on_input(char)
        yield Finished
