from cmd import command, WrongUsageError
from ui.controls import *

cmds = []


def add(cmd: command) -> command:
    cmds.append(cmd)
    return cmd


def _goto_tab(context, args: [str]):
    if len(args) != 1:
        raise WrongUsageError("para_number", 0)
    try:
        tab_number = int(args[0])
    except:
        raise WrongUsageError("para1.not_number", 0)
    tbl: tablist = context.tablist
    if 0 <= tab_number < len(tbl):
        tbl.goto(tab_number)
    else:
        raise WrongUsageError("para1.over_range", 0)


cmd_goto_tab = add(command("goto", _goto_tab))
