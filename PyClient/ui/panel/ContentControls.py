from ui.Controls import *


class ContentControl(Control):
    ContentProp: DpProp

    def GetChildren(self) -> Collection["UIElement"]:
        c = self.Content
        if c is None:
            return EmptyTuple
        else:
            return c,

    def PaintOn(self, canvas: Canvas):
        rw = self.RenderWidth
        rh = self.RenderHeight
        if rw <= 0 and rh <= 0:
            return
        content = self.Content
        if content:
            content.PaintOn(Viewer.ByCanvas(canvas))

    def Measure(self):
        if not self.IsVisible:
            self.DWidth = 0
            self.DHeight = 0
            return
        dWidth = self.Width
        dHeight = self.Height
        content = self.Content
        if dWidth == Auto:
            if content:
                w = content.DWidth
            else:
                w = 0
        else:
            w = dWidth

        if dHeight == Auto:
            if content:
                h = content.DHeight
            else:
                h = 0
        else:
            h = dHeight
        self.DWidth = w
        self.DHeight = h

    def Arrange(self, width: int, height: int) -> Tuple[int, int]:
        if not self.IsVisible:
            self.RenderWidth = 0
            self.RenderHeight = 0
            return 0, 0
        dWidth = self.Width
        dHeight = self.Height
        content = self.Content
        if content:
            if dWidth == Auto:
                bw = min(content.DWidth, width)
            else:
                bw = min(content.Width, width, dWidth)

            if dHeight == Auto:
                bh = min(content.DWidth, height)
            else:
                bh = min(content.DHeight, height, dHeight)
        else:
            if dWidth == Auto:
                bw = width
            else:
                bw = min(width, dWidth)

            if dHeight == Auto:
                bh = height
            else:
                bh = min(height, dHeight)
        rbw, rbh = content.Arrange(bw, bh)
        self.RenderWidth = rbw
        self.RenderHeight = rbh
        return self.RenderWidth, self.RenderHeight

    @property
    def Content(self) -> UIElement:
        return self.GetValue(self.ContentProp)

    @Content.setter
    def Content(self, value: UIElement):
        self.SetValue(self.ContentProp, value)


def OnContentControlContentPropChangedCallback(elemt: ContentControl, value: UIElement):
    elemt.NeedRerender()
    value.Parent = elemt


ContentControl.ContentProp = DpProp.Register(
    "Content", UIElement, ContentControl,
    DpPropMeta(lambda: None, allowSameValue=False,
               propChangedCallback=OnContentControlContentPropChangedCallback)
)
