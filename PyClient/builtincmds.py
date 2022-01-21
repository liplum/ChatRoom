import GLOBAL
import core.operations as op
import i18n
import ui.tabs as tabs
import ui.uiop as uiop
from cmds import *
from core.settings import entity as settings_table
from core.shared import *
from net.networks import CannotConnectError
from ui.cmd_modes import Cmd_Context

cmds = []


def add(*args) -> command:
    cmd = command(*args)
    cmds.append(cmd)
    return cmd


def _goto_tab(context: Cmd_Context, args: [str]):
    if len(args) != 1:
        raise WrongUsageError(i18n.trans("cmds.goto.usage"), -1)
    try:
        tab_number = int(args[0])
    except:
        raise WrongUsageError(i18n.trans("cmds.$tabs$.not_number", args[0]), 0)
    tbl: tablist = context.tablist
    start = 1
    end = len(tbl)
    if start - 1 <= tab_number <= end - 1:
        tbl.goto(tab_number - 1)
    else:
        raise WrongUsageError(i18n.trans("cmds.$tabs$.over_range", wrong=tab_number, start=start, end=end), 0)


cmd_goto_tab = add("goto", _goto_tab)


def _register(context: Cmd_Context, args: [str]):
    argslen = len(args)
    network: inetwork = context.network
    if argslen != 2 and argslen != 3:
        raise WrongUsageError(i18n.trans("cmds.reg.usage"), -1)
    if argslen == 3:  # first is server
        full_server = args[0:1]
        server = _con(context, full_server)
        account = args[1]
        pwd = args[2]
    elif argslen == 2:
        tab: chat_tab = context.tab
        server = tab.connected
        if not server:
            raise WrongUsageError(i18n.trans("cmds.$common$.cur_tab_unconnected"), 0)
        account = args[0]
        pwd = args[1]
    op.register(network, server, account, pwd)


cmd_register = add("reg", _register)


def _help_show_usage(tab, name):
    usage = i18n.trans(f"cmds.{name}.usage")
    description = i18n.trans(f"cmds.{name}.description")
    tab.add_string(f"{name}: {description}\n   {usage}")


def _help(context: Cmd_Context, args: [str]):
    argslen = len(args)
    manager: cmdmanager = context.cmd_manager
    tab: tabs.Tab = context.tab
    if argslen == 0:
        for name, cmd in manager:
            _help_show_usage(tab, name)
    elif argslen == 1:
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


def _con_shared(network, token):
    """
    connect a server
    :param network: inetwork
    :param token: server_token
    :exception  WrongUsageError("cmds.$common$.invalid_server_token")
    :exception  CmdError("cmds.$common$.cannot_connect_server")
    """
    if token:
        try:
            op.connect(network, token, strict=True)
        except CannotConnectError as cce:
            raise CmdError(
                i18n.trans("cmds.$common$.cannot_connect_server", ip=token.ip, port=token.port))
    else:
        raise WrongUsageError(i18n.trans("cmds.$common$.invalid_server_token"), 0)


def _con(context: Cmd_Context, args: [str]) -> server_token:
    argslen = len(args)
    if argslen != 1:
        raise WrongUsageError(i18n.trans("cmds.con.usage"), -1)
    server = server_token.by(args[0])
    _con_shared(context.network, server)
    tab = context.tab
    has_attr = hasattr(tab, "connected") and hasattr(tab, "connect")
    if has_attr:
        connected = tab.connected
        if connected and connected != server:
            raise WrongUsageError(i18n.trans("cmds.$common$.already_connected", ip=connected.ip, port=connected.port),
                                  0)
        else:
            tab.connect(server)
    return server


cmd_con = add("con", _con)

# Removed - join
"""
def _join(context: Cmd_Context, argTypes: [str]):
    argslen = len(argTypes)
    network = context.network
    if argslen == 2:  # 1:<server ip>:<port> 2:<chatting room id>
        server = server_token.by(argTypes[0])
        _con_shared(network, server)
        try:
            room_id = roomid(int(argTypes[1]))
        except:
            raise WrongUsageError(i18n.trans("cmds.$common$.invalid_room_id", argTypes[1]), 1)
        Tab: chat_tab = context.Tab
        if Tab.joined:
            raise CmdError(i18n.trans("cmds.join.already_joined", room_id))
        Tab.join(room_id)
    elif argslen == 1:
        try:
            room_id = roomid(int(argTypes[0]))
        except:
            raise WrongUsageError(i18n.trans("cmds.$common$.invalid_room_id", argTypes[0]), 1)
        Tab: chat_tab = context.Tab
        if Tab.connected is None:
            raise WrongUsageError(i18n.trans("cmds.$common$.cur_tab_unconnected"), -1)
        if Tab.joined:
            raise CmdError(i18n.trans("cmds.join.already_joined", room_id))
        Tab.join(room_id)
    else:
        raise WrongUsageError(i18n.trans("cmds.join.usage"), -1)


cmd_join = add("join", _join)
"""


def _jroom_room(context: Cmd_Context, args: [str]):
    argslen = len(args)
    network = context.network
    if argslen == 1:
        tab: chat_tab = context.tab
        if tab.connected is None:
            raise WrongUsageError(i18n.trans("cmds.$common$.cur_tab_unconnected"), 0)
        if tab.user_info is None or not tab.user_info.verified:
            raise WrongUsageError(i18n.trans("cmds.$common$.cur_tab_unauthenticated"), 0)
        try:
            room_id = roomid(int(args[0]))
        except:
            raise WrongUsageError(i18n.trans("cmds.$common$.invalid_room_id", args[0]), 1)
        op.join(network, tab.user_info, room_id)
    else:
        raise WrongUsageError(i18n.trans("cmds.join.usage"), -1)


cmd_jroom = add("join", _jroom_room)


def _close(context: Cmd_Context, args: [str]):
    argslen = len(args)
    tbl: tablist = context.tablist
    if argslen == 0:
        uiop.close_cur_tab(tbl, context.win)
    elif argslen == 1:
        try:
            tab_number = int(args[0])
        except:
            raise WrongUsageError(i18n.trans("cmds.$tabs$.not_number", args[0]), 0)
        start = 1
        end = len(tbl)
        if start - 1 <= tab_number <= end - 1:
            tbl.Remove(tab_number - 1)
        else:
            raise WrongUsageError(i18n.trans("cmds.$tabs$.over_range", wrong=tab_number, start=start, end=end), 0)
    else:
        raise WrongUsageError(i18n.trans("cmds.close.usage"), -1)


cmd_close = add("close", _close)


def _login(context: Cmd_Context, args: [str]):
    argslen = len(args)
    network = context.network
    if argslen != 3 and argslen != 2:
        raise WrongUsageError(i18n.trans("cmds.login.usage"), -1)
    if argslen == 3:
        server = server_token.by(args[0])
        _con_shared(network, server)
    elif argslen == 2:
        tab: chat_tab = context.tab
        server = tab.connected
        if server is None:
            raise WrongUsageError(i18n.trans("cmds.$common$.cur_tab_unconnected"), 0)

    op.login(context.network, server, args[argslen - 2], args[argslen - 1])


cmd_login = add("login", _login)


def _lang(context: Cmd_Context, args: [str]):
    win: iwindow = context.win
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
                settings["Language"] = lang
                win.reload()
            except i18n.LocfileLoadError as lle:
                raise WrongUsageError(i18n.trans("cmds.lang.cannot_load", lang=lang), 0)
    elif argslen == 2:
        if args[1] == "-s":  # load & strict
            lang = args[0]
            try:
                i18n.load(lang, strict=True)
                settings = settings_table()
                settings["Language"] = lang
                win.reload()
            except i18n.LocfileLoadError as lle:
                raise WrongUsageError(i18n.trans("cmds.lang.cannot_load_cause", lang=lang, cause=repr(lle.inner)), 0)
        else:
            raise WrongUsageError(i18n.trans("cmds.lang.usage"), 0)
    else:
        raise WrongUsageError(i18n.trans("cmds.lang.usage"), -1)


cmd_lang = add("lang", _lang)


def _croom(context: Cmd_Context, args: [str]):
    network = context.network
    argslen = len(args)
    if argslen != 1:
        raise WrongUsageError(i18n.trans("cmds.create.usage"), -1)
    tab: chat_tab = context.tab
    server = tab.connected
    if server is None:
        raise WrongUsageError(i18n.trans("cmds.$common$.cur_tab_unconnected"), 0)
    if tab.user_info is None or not tab.user_info.verified:
        raise WrongUsageError(i18n.trans("cmds.$common$.cur_tab_unauthenticated"), 0)
    room_name = args[0]
    op.create_room(network, tab.user_info, room_name)


cmd_croom = add("create", _croom)


def _main(context: Cmd_Context, args: [str]):
    win: iwindow = context.win
    argslen = len(args)
    if argslen != 0:
        raise WrongUsageError(i18n.trans("cmds.main.usage"), -1)
    main_menu = win.newtab('main_menu_tab')
    tablist: tablist = context.tablist
    tablist.Add(main_menu)


cmd_main = add("main", _main)

if GLOBAL.DEBUG:

    def _run(context: Cmd_Context, args: [str]):
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
            raise WrongUsageError(i18n.trans("cmds.run.usage"), -1)
        try:
            exec(code)
        except Exception as e:
            raise WrongUsageError(i18n.trans("cmds.run.execute_error", code=code, exception=e), 0)


    cmd_run = add("run", _run)


    def _reload(context: Cmd_Context, args: [str]):
        argslen = len(args)
        if argslen == 0:
            utils.reload_all_modules()
        elif argslen == 1:
            module_name = args[0]
            found = utils.reload_module(module_name)
            if not found:
                raise WrongUsageError(i18n.trans("cmds.reload.no_such_module", module=module_name), 0)
        else:
            raise WrongUsageError(i18n.trans("cmds.reload.usage"), -1)


    cmd_reload = add("reload", _reload)
