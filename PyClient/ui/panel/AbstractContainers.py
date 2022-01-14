from ui.Controls import *


class AbstractContainer(Control):

    def __init__(self):
        super().__init__()
        self._subControls = []

    def AddControl(self, control: Control) -> bool:
        self.AddChild(control)
        return True

    def RemoveControl(self, control: Control) -> bool:
        return self.RemoveChild(control)

    @property
    def SubControls(self):
        return self._subControls
