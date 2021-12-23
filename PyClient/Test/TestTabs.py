from ui.control.labels import label
from ui.tabs import *


class TestTab(tab):

    def __init__(self, client: iclient, tablist: tablist):
        super().__init__(client, tablist)
        self.test_label = label("Test")
        self.viewer = Viewer()

    @property
    def title(self) -> str:
        return "Test"

    def PaintOn(self, canvas: Canvas):
        v = self.viewer
        v.X = self.X
        v.Y = self.Y
        v.Width = canvas.Width
        v.Height = canvas.Height - 2
        v.Bind(canvas)
        self.test_label.PaintOn(v)
