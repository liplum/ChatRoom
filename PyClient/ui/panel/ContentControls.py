from ui.Controls import *


class FitMode(Enum):
    Fit = 1
    Stretch = 2


class ContentControl(Control):
    ContentProp: DpProp
    FitProp: DpProp

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
        fit = self.Fit
        if content:
            if dWidth == Auto:
                w = content.DWidth
            else:
                if fit == FitMode.Fit:
                    w = min(content.DWidth, dWidth)
                else:  # Stretch
                    w = dWidth
            if dHeight == Auto:
                h = content.DHeight
            else:
                if fit == FitMode.Fit:
                    w = min(content.DHeight, dHeight)
                else:  # Stretch
                    w = dHeight
        else:  # No content
            if dWidth == Auto:
                w = 0
            else:
                w = dWidth

            if dHeight == Auto:
                h = 0
            else:
                w = dHeight

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
        fit = self.Fit
        if content:
            cdw = content.DWidth
            cdh = content.DHeight
            if dWidth == Auto:
                bw = min(cdw, width)
            else:
                if fit == FitMode.Fit:
                    bw = min(cdw, width, dWidth)
                else:  # Stretch
                    bw = width

            if dHeight == Auto:
                bh = min(cdh, height)
            else:
                if fit == FitMode.Fit:
                    bh = min(cdh, height, dHeight)
                else:
                    bh = height
            bw, bh = content.Arrange(bw, bh)
        else:
            if dWidth == Auto:
                bw = width
            else:
                bw = min(width, dWidth)

            if dHeight == Auto:
                bh = height
            else:
                bh = min(height, dHeight)
        self.RenderWidth = bw
        self.RenderHeight = bh
        return self.RenderWidth, self.RenderHeight

    @property
    def Content(self) -> UIElement:
        return self.GetValue(self.ContentProp)

    @Content.setter
    def Content(self, value: UIElement):
        self.SetValue(self.ContentProp, value)

    @property
    def Fit(self) -> FitMode:
        return self.GetValue(self.FitProp)

    @Fit.setter
    def Fit(self, value: FitMode):
        self.SetValue(self.FitProp, value)


def OnContentControlContentPropChangedCallback(elemt: ContentControl, value: UIElement):
    elemt.NeedRerender()
    value.Parent = elemt


ContentControl.ContentProp = DpProp.Register(
    "Content", UIElement, ContentControl,
    DpPropMeta(lambda: None, allowSameValue=False,
               propChangedCallback=OnContentControlContentPropChangedCallback)
)
ContentControl.FitProp = DpProp.Register(
    "Fit", FitMode, ContentControl,
    DpPropMeta(FitMode.Fit,
               propChangedCallback=OnRenderPropChangedCallback))
