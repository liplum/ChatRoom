from ui.Controls import *


class AbstractContainer(Control):

    def __init__(self):
        super().__init__()
        self._subControls = []

    def Arrange(self, width: int, height: int):
        pass

    def AddControl(self, control: Control):
        self.AddChild(control)

    def RemoveControl(self, control: Control) -> bool:
        return self.RemoveChild(control)

    @property
    def SubControls(self):
        return self.SubControls
