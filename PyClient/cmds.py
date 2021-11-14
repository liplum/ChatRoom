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
        raise CmdError(i18n.trans("cmds.goto.usage"))
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
    argslen = len(args)
    network: i_network = context.network
    if argslen == 2:
        pass
    elif argslen == 3:
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
        raise CmdError(i18n.trans("cmds.reg.usage"))


cmd_register = add("reg", _register)


def _help_show_usage(tab, name):
    usage = i18n.trans(f"cmds.{name}.usage")
    tab.add_string(f"{name}:{usage}")


def _help(context, args: [str]):
    argslen = len(args)
    manager: cmdmanager = context.cmd_manager
    tab: tab = context.tab
    if argslen == 1:
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
        raise CmdError(i18n.trans("cmds.help.usage"))


cmd_help = add("help", _help)


def _con(context, args: [str]):
    pass


cmd_con = add("con", _con)


def _exec(context, args: [str]):
    argslen = len(args)
    if argslen == 0:
        return
    if argslen == 1:
        code = args[0]
    elif argslen == 2 and args[0] == "-f":
        path = args[1]
        try:
            with open(path, "r") as f:
                code = f.read()
        except:
            raise WrongUsageError(i18n.trans("cmds.run.cannot_read_file", path=path), 0)
    else:
        raise CmdError(i18n.trans("cmds.run.usage"))
    try:
        exec(code)
    except Exception as e:
        raise WrongUsageError(i18n.trans("cmds.run.execute_error", code=code, exception=e), 0)


cmd_exec = add("run", _exec)


def _lang(context, args: [str]):
    argslen = len(args)
    if argslen == 0:
        i18n.reload()
    elif argslen == 1:
        lang = args[0]
        try:
            i18n.load(lang, strict=True)
        except i18n.LocfileLoadError as lle:
            raise WrongUsageError(i18n.trans("cmds.lang.cannot_load", lang), 0)
    else:
        raise CmdError(i18n.trans("cmds.lang.usage"))


cmd_lang = add("lang", _lang)
