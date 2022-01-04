from ui.Controls import *


class AbstractContainer(Control):

    def __init__(self):
        super().__init__()
        self._subControls = []

    def Arrange(self, width: int, height: int):
        pass

    def AddControl(self, control: Control):
        AutoAdd(self,control)

    def RemoveControl(self, control: Control):
        AutoRemove(self,control)

    @property
    def SubControls(self):
        return self.SubControls
