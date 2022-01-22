from typing import Optional, NoReturn

import ui.Renders as r
import ui.outputs as o
from ui.Renders import Canvas


def TranslateLegacyRender(canvas: r.Canvas, text: str, bk=None, fg=None):
    writer = r.StrWriter(canvas)
    for ch in text:
        if ch == "\n":
            writer.NextLine()
        else:
            writer.Write(ch, bk, fg)


def TranslateLegacyRenderW(writer: r.Writer, text: str, bk=None, fg=None):
    for ch in text:
        if ch == "\n":
            writer.NextLine()
        else:
            writer.Write(ch, bk, fg)


class LegacyBufferSimulator(r.StrWriter, o.buffer):
    Inited = False

    @classmethod
    def Init(cls):
        cls.BKMap = {
            o.CmdBkColor.Blue: r.BK.Blue,
            o.CmdBkColor.Red: r.BK.Red,
            o.CmdBkColor.Black: r.BK.Black,
            o.CmdBkColor.White: r.BK.White,
            o.CmdBkColor.Cyan: r.BK.Cyan,
            o.CmdBkColor.Yellow: r.BK.Yellow,
            o.CmdBkColor.Violet: r.BK.Violet,
        }
        cls.FGMap = {
            o.CmdFgColor.Blue: r.FG.Blue,
            o.CmdFgColor.Red: r.FG.Red,
            o.CmdFgColor.Black: r.FG.Black,
            o.CmdFgColor.White: r.FG.White,
            o.CmdFgColor.Cyan: r.FG.Cyan,
            o.CmdFgColor.Yellow: r.FG.Yellow,
            o.CmdFgColor.Violet: r.FG.Violet,
        }
        cls.Inited = True

    def __init__(self, canvas: Canvas, x: int = 0, y: int = 0, width: int = None, height: int = None, autoWrap=True):
        super().__init__(canvas, x, y, width, height, autoWrap)
        if not self.Inited:
            self.Init()

    def addtext(self, text: str = "", style: o.CmdStyleEnum = o.CmdStyle.Default,
                fgcolor: Optional[o.CmdFgColorEnum] = None,
                bkcolor: Optional[o.CmdBkColorEnum] = None, end: str = '\n') -> NoReturn:
        bk = self.BKMap[bkcolor] if bkcolor is not None else None
        fg = self.FGMap[fgcolor] if fgcolor is not None else None
        if text:
            TranslateLegacyRenderW(self, text, bk, fg)
        if end:
            TranslateLegacyRenderW(self, end, bk, fg)

    @property
    def width(self):
        return self.Width

    @property
    def height(self):
        return self.Height
