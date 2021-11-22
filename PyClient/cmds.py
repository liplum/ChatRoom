import i18n
import ui.tabs
import ui.tabs as tabs
from cmd import *
from core.operations import *
from core.settings import entity as settings_table
from net.msgs import register_request
from net.networks import CannotConnectError
from ui.cmd_modes import Cmd_Context
from ui.windows import *

cmds = []


def add(*args) -> command:
    cmd = command(*args)
    cmds.append(cmd)
    return cmd


def _goto_tab(context: Cmd_Context, args: [str]):
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


def _register(context: Cmd_Context, args: [str]):
    argslen = len(args)
    network: inetwork = context.network
    if argslen != 2 and argslen != 3:
        raise CmdError(i18n.trans("cmds.reg.usage"))
    if argslen == 3:  # first is server
        full_server = args[0:1]
        server = _con(context, full_server)
        account = args[1]
        pwd = args[2]
    elif argslen == 2:
        tab: chat_tab = context.tab
        server = tab.connected
        if not server:
            raise WrongUsageError(i18n.trans("cmds.reg.current_tab_is_unconnected"), 0)
        account = args[0]
        pwd = args[1]

    uc = network.get_channel("User")
    msg = register_request()
    msg.account = account
    msg.password = pwd
    uc.send(server, msg)


cmd_register = add("reg", _register)


def _help_show_usage(tab, name):
    usage = i18n.trans(f"cmds.{name}.usage")
    description = i18n.trans(f"cmds.{name}.description")
    tab.add_string(f"{name}: {description}\n   {usage}")


def _help(context: Cmd_Context, args: [str]):
    argslen = len(args)
    manager: cmdmanager = context.cmd_manager
    tab: tabs.tab = context.tab
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


def _con(context: Cmd_Context, args: [str]) -> server_token:
    argslen = len(args)
    if argslen != 1:
        raise WrongUsageError(i18n.trans("cmds.con.usage"), 0)
    server = to_server_token(args[0])
    if server is None:
        raise WrongUsageError(i18n.trans("cmds.con.para1.invalid"), 0)
    network = context.network
    try:
        connect(network, server, strict=True)
    except CannotConnectError as cce:
        raise CmdError(
            i18n.trans("cmds.reg.cannot_connect_server", ip=server.ip, port=server.port))
    tab = ui.tabs.tab
    has_attr = hasattr(tab, "connected") and hasattr(tab, "connect")
    if has_attr:
        connected = tab.connected
        if connected and connected != server:
            raise WrongUsageError(i18n.trans("cmds.con.already_connected", ip=connected.ip, port=connected.port), 0)
        else:
            tab.connect(server)
    return server


cmd_con = add("con", _con)


def _join(context: Cmd_Context, args: [str]):
    # TODO:Complete join cmd
    argslen = len(args)
    if argslen == 2:  # 1:<server ip>:<port> 2:<chatting room id>
        full_server = args[0:1]
        _con(context, full_server)
        try:
            room_id = roomid(int(args[1]))
        except:
            raise WrongUsageError(i18n.trans("cmds.con.para_invalid.room_id", args[1]), 1)
        tab: chat_tab = context.tab
        if tab.joined:
            raise CmdError(i18n.trans("cmds.con.already_joined", room_id))
        tab.join(room_id)
    elif argslen == 1:
        try:
            room_id = roomid(int(args[0]))
        except:
            raise WrongUsageError(i18n.trans("cmds.con.para_invalid.room_id", args[0]), 1)
        tab: chat_tab = context.tab
        if tab.joined:
            raise CmdError(i18n.trans("cmds.con.already_joined", room_id))
        tab.join(room_id)
    else:
        raise WrongUsageError(i18n.trans("cmds.join.usage"), 0)


cmd_join = add("join", _join)


def _close(context: Cmd_Context, args: [str]):
    argslen = len(args)
    tbl: tablist = context.tablist
    if argslen == 0:
        tbl.remove(context.tab)
    elif argslen == 1:
        try:
            tab_number = int(args[0])
        except:
            raise WrongUsageError(i18n.trans("cmds.close.para_invalid.not_number", args[0]), 0)
        if 0 <= tab_number < len(tbl):
            tbl.remove(tab_number)
        else:
            raise WrongUsageError(i18n.trans("cmds.close.para_invalid.over_range", tab_number), 0)
    else:
        raise WrongUsageError(i18n.trans("cmds.close.usage"), 0)


cmd_close = add("close", _close)


def _login(context: Cmd_Context, args: [str]):
    argslen = len(args)
    if argslen != 3 and argslen != 2:
        raise WrongUsageError(i18n.trans("cmds.close.usage"), 0)

    if argslen == 3:
        full_server = args[0:1]
        server = _con(context, full_server)
    elif argslen == 2:
        tab: chat_tab = context.tab
        server = tab.connected
        if server is None:
            raise WrongUsageError(i18n.trans("cmds.close.cur_tab_unconnected"), 0)

    login(context.network, server, args[argslen - 2], args[argslen - 1])


cmd_login = add("login", _login)


def _exec(context: Cmd_Context, args: [str]):
    argslen = len(args)
    if argslen == 0:
        return
    if argslen == 1:
        code = args[0]
    elif argslen == 2 and args[0] == "-f":
        path = args[1]
        try:
            with open(path, "r", encoding="utf-8") as f:
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


def _lang(context: Cmd_Context, args: [str]):
    win:iwindow = context.win
    argslen = len(args)
    if argslen == 0:  # reload & easy
        try:
            i18n.reload(strict=True)
            win.reload()
        except i18n.LocfileLoadError as lle:
            raise WrongUsageError(i18n.trans("cmds.lang.cannot_reload"), 0)
    elif argslen == 1:
        if args[0] == "-s":  # reload & strict
            try:
                i18n.reload(strict=True)
                win.reload()
            except i18n.LocfileLoadError as lle:
                raise WrongUsageError(i18n.trans("cmds.lang.cannot_reload_cause", cause=repr(lle.inner)), 0)
        else:  # load & easy
            lang = args[0]
            try:
                i18n.load(lang, strict=True)
                settings = settings_table()
                settings.set("Language", lang)
                win.reload()
            except i18n.LocfileLoadError as lle:
                raise WrongUsageError(i18n.trans("cmds.lang.cannot_load", lang=lang), 0)
    elif argslen == 2:
        if args[1] == "-s":  # load & strict
            lang = args[0]
            try:
                i18n.load(lang, strict=True)
                settings = settings_table()
                settings.set("Language", lang)
                win.reload()
            except i18n.LocfileLoadError as lle:
                raise WrongUsageError(i18n.trans("cmds.lang.cannot_load_cause", lang=lang, cause=repr(lle.inner)), 0)
        else:
            raise CmdError(i18n.trans("cmds.lang.usage"))
    else:
        raise CmdError(i18n.trans("cmds.lang.usage"))


cmd_lang = add("lang", _lang)
