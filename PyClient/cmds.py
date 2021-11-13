from cmd import command
from net.msgs import register_request
from net.networks import i_network
from ui.controls import *

cmds = []


def add(*args) -> command:
    cmd = command(*args)
    cmds.append(cmd)
    return cmd


def _goto_tab(context, args: [str]):
    if len(args) != 1:
        raise WrongUsageError(i18n.trans("usage"), 0)
    try:
        tab_number = int(args[0])
    except:
        raise WrongUsageError(i18n.trans("cmds.goto.para1.not_number", args[0]), 0)
    tbl: tablist = context.tablist
    if 0 <= tab_number < len(tbl):
        tbl.goto(tab_number)
    else:
        raise WrongUsageError(i18n.trans("cmds.goto.para1.over_range", tab_number), 0)


cmd_goto_tab = add("goto", _goto_tab)


def _register(context, args: [str]):
    arglen = len(args)
    network: i_network = context.network
    if arglen == 2:
        pass
    elif arglen == 3:
        server_info = args[0].split(":")
        if len(server_info) != 2:
            raise WrongUsageError(i18n.trans("cmds.reg.para1.invalid"), 0)
        ip = server_info[0]
        try:
            port = int(server_info[1])
        except:
            raise WrongUsageError(i18n.trans("cmds.reg.para1.invalid"), 0)
        uc = network.get_channel("User")
        msg = register_request()
        msg.account = args[1]
        msg.password = args[2]
        uc.send(server_token(ip, port), msg)
    else:
        raise WrongUsageError(i18n.trans("cmds.reg.usage"), 0)


cmd_register = add("reg", _register)


def _help_show_usage(tab, name):
    usage = i18n.trans(f"cmds.{name}.usage")
    tab.add_string(f"{name}:{usage}")


def _help(context, args: [str]):
    arglen = len(args)
    manager: cmdmanager = context.cmd_manager
    tab: tab = context.tab
    if arglen == 1:
        if args[0] == "all":
            for name, cmd in manager:
                _help_show_usage(tab, name)
        else:
            name = args[0]
            if manager.has(name):
                _help_show_usage(tab, name)
            else:
                raise WrongUsageError(i18n.trans("cmds.help.cannot_find", name), 0)
    else:
        raise WrongUsageError(i18n.trans("cmds.help.usage"), 0)


cmd_help = add("help", _help)


def _con(context, args: [str]):
    pass


cmd_con = add("con", _con)


def _exec(context, args: [str]):
    if len(args) == 0:
        return
    code = args[0].strip('\"')
    try:
        exec(code)
    except Exception as e:
        raise CmdError(i18n.trans("cmds.exec.execute_error", code=code, exception=e))


cmd_exec = add("exec", _exec)
