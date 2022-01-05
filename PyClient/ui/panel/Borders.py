from ui.Controls import *
from ui.themes import theme, rounded_rectangle

NoneType = type(None)


class Border(VisualElement):

    def __init__(self, theme: theme = rounded_rectangle):
        super().__init__()
        self.Theme = theme
        self._inner: Optional[Control] = None
        self._onInnerChanged = Event(Border, (Control, NoneType), (Control, NoneType))
        self.OnInnerChanged.Add(lambda _, _1, _2: self.OnContentChanged)

    @property
    def Inner(self) -> Optional[Control]:
        return self._inner

    @Inner.setter
    def Inner(self, value: Optional[Control]):
        old = self._inner
        if old != value:
            if old:
                try:
                    self._subVElems.remove(old)
                except:
                    pass
            self._inner = value
            if value:
                self._subVElems.append(value)
            self.OnInnerChanged(self, old, value)

    @property
    def OnInnerChanged(self) -> Event:
        """
        Para 1:Border object

        Para 2:old inner Control

        Para 3:new inner Control

        :return: Event(Border,Optional[Control],Optional[Control])
        """
        return self._onInnerChanged
