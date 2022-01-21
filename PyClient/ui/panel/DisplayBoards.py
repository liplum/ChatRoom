from ui.Controls import *
from ui.panel.ContentControls import ContentControl
from ui.themes import BorderTheme, rounded_rectangle

NoneType = type(None)
from ui.panel.Borders import Border


class DisplayBoard(ContentControl):
    InnerProp: DpProp

    def __init__(self, theme: BorderTheme = rounded_rectangle):
        super().__init__()
        self.Content: Border = Border(theme)

    @property
    def Inner(self) -> Control:
        return self.GetValue(self.InnerProp)

    @Inner.setter
    def Inner(self, value: Control):
        self.SetValue(self.InnerProp, value)

    @property
    def Focusable(self) -> bool:
        return False


def OnDisplayBoardInnerPropChangedCallback(elemt, value):
    elemt.NeedRerender()
    border: Border = elemt.Content
    border.Content = value


DisplayBoard.InnerProp = DpProp.Register(
    "Inner", Control, DisplayBoard,
    DpPropMeta(lambda: None, allowSameValue=False,
               propChangedCallback=OnDisplayBoardInnerPropChangedCallback)
)
