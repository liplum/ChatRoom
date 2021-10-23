from typing import List, Dict, Tuple

import core.ioc as ioc
from core.event import event
import ui.output as output
from threading import RLock
from network.network import i_network, server_token, userid
from network import network
import ui.input as _input
from utils import get, clear_screen, lock, clock, separate, compose
import utils
from typing import Optional, Union, Any, Tuple, List, Dict
from io import StringIO
from datetime import datetime


class command:
    def __init__(self, _id: str, tip: str, handler):
        self.id_ = _id
        self.tip = tip
        self.handler = handler


def get_command_id_tip(cmd: command) -> str:
    s = StringIO()
    s.write(cmd.id_)
    s.write(" ")
    s.write(cmd.tip)
    res = s.getvalue()
    s.close()
    return res


def do_noting():
    pass


class state:
    def on_en(self):
        pass

    def on_ex(self):
        pass

    def update(self):
        pass


class smachine:
    def __init__(self):
        self.cur: Optional[state] = None
        self.pre: Optional[state] = None

    def enter(self, s: state):
        if self.pre is not None:
            self.pre.on_ex()
        self.pre = self.cur
        self.cur = s
        if self.cur is not None:
            self.cur.on_en()

    def back(self):
        self.enter(self.pre)

    def update(self):
        if self.cur is not None:
            self.cur.update()


class client_state(state):
    def __init__(self, client):
        super().__init__()
        self.client = client

    def on_en(self):
        pass

    def on_ex(self):
        pass

    def update_input_list(self, input_list):
        self.input_list: list = input_list

    def update(self):
        super().update()


class cmd_state(client_state):

    def update(self):
        client = self.client
        client.display_lock(client.win.display)
        client.display_lock(client.display.display_text, client.command_list_tip)
        client.display_lock(client.display.display_text, "Enter a command:")
        client.input_.get_input()
        inputs = client.input_.get_input_list()
        client.input_.flush()
        cmd_str = "".join(inputs)
        cmd: command = get(client.cmds.cmds, cmd_str)
        if cmd is not None:
            cmd.handler()
        else:
            client.logger.error(f"Cannot identify command {cmd_str}")


class cmd_list:
    def __init__(self):
        self.cmds = {}

    def add(self, cmd: command):
        self.cmds[cmd.id_] = cmd


class client:
    def __init__(self):
        self.container: ioc.container = ioc.container()
        self.on_service_register: event = event()
        self.on_command_register: event = event()
        self.cmds: cmd_list = cmd_list()
        self.running: bool = False
        self._display_lock: RLock = RLock()
        # self.tps = clock(4)
        self.log_file: Optional[str] = None
        self.changed = False

    def set_changed(self):
        self.changed = True

    def init(self) -> None:
        self.container.register_singleton(output.i_logger, output.cmd_logger)
        self.container.register_singleton(output.i_display, output.cmd_display)
        self.network: network.network = network.network(self)
        self.container.register_instance(i_network, self.network)
        self.on_service_register(self.container)

        self.input_: _input.i_nbinput = self.container.resolve(_input.i_nbinput)
        self.logger: output.i_logger = self.container.resolve(output.i_logger)
        self.logger.logfile = self.log_file
        self.display: output.i_display = self.container.resolve(output.i_display)
        self.win = window(self.display)
        self.win.fill_until_max = True
        self.gen_cmds()
        self.sm = smachine()
        self.textbox = textbox()

    def gen_cmds(self):
        def send_text():
            pass

        def refresh():
            pass

        self.cmds.add(command("#1", "send text", send_text))
        self.cmds.add(command("#0", "refresh", refresh))

        self.on_command_register(self.cmds)
        all_tips = StringIO()
        all_tips.write("Command\n")
        cmds = self.cmds.cmds
        for cmd_k in sorted(cmds):
            cmd = cmds[cmd_k]
            all_tips.write("\t")
            all_tips.write(get_command_id_tip(cmd))
            all_tips.write("\n")
        self.command_list_tip = all_tips.getvalue()
        all_tips.close()

    def connect(self, ip_and_port):
        self.network.connect(server_token(ip_and_port))

    def start(self):
        self.running = True
        while self.running:
            # self.tps.delay()
            self.sm.update()
            self.display_lock(self.win.display)
            self.display_lock(self.display.display_text, self.command_list_tip)
            self.display_lock(self.display.display_text, "Enter a command:")
            self.input_.get_input()
            inputs = self.input_.get_input_list()
            self.input_.flush()
            cmd_str = "".join(inputs)
            cmd: command = get(self.cmds.cmds, cmd_str)
            if cmd is not None:
                cmd.handler()
            else:
                self.logger.error(f"Cannot identify command {cmd_str}")
            self.display_lock(self.display.render())

    def display_lock(self, func, *args, **kwargs):
        lock(self._display_lock, func, *args, **kwargs)

    def add_text(self, text: str):
        self.win.add_text(text)

    def __init_channels(self):
        pass


class textbox:
    def __init__(self, cursor_icon: str = "^"):
        self._input_list = []
        self.cursor_icon = cursor_icon
        self.cursor: int = 0

    @property
    def input_list(self):
        return self._input_list[:]

    @input_list.setter
    def input_list(self, value):
        if isinstance(value, list):
            self._input_list = value[:]
        else:
            self._input_list = list(value)

    @property
    def cursor(self):
        return self._cursor

    @cursor.setter
    def cursor(self, value):
        list_len = len(self._input_list)
        self._cursor = value % (list_len + 1)
        self.is_forwards = self._cursor >= 0
        if self.is_forwards:
            self.cursor_pos = self._cursor
        else:
            self.cursor_pos = list_len + self._cursor + 1

    def home(self):
        self.cursor = 0

    def left(self):
        self.cursor -= 1

    def right(self):
        self.cursor += 1

    def end(self):
        self.cursor = -1

    @property
    def distext(self) -> str:
        cursor_pos = self.cursor_pos
        with StringIO() as s:
            cur = 0
            for char in self._input_list:
                if cur == cursor_pos:
                    s.write(self.cursor_icon)
                s.write(char)
                cur += 1
            if cur == cursor_pos:
                s.write(self.cursor_icon)

            return s.getvalue()

    def append(self, char):
        self._input_list.insert(self.cursor_pos, char)
        self.cursor += 1

    def delete(self):
        if self.cursor_pos > 0:
            del self._input_list[self.cursor_pos - 1]
            self.cursor -= 1


StorageUnit = Tuple[datetime, userid, str]


class msgstorage:
    def __init__(self, save_file: str):
        self.save_file = save_file
        self.__storage: List[StorageUnit] = []
        self.changed = False

    def store(self, timestamp: datetime, userid_: Union[userid, Any], msg: str):
        if not isinstance(userid_, userid):
            userid_ = userid(userid_)
        self.__storage.append((timestamp, userid_, msg))
        self.changed = True

    def sort(self):
        self.__storage.sort(key=lambda i: i[0])
        self.changed = False

    def __iter__(self):
        return self.__storage[:].__iter__()

    def serialize(self):
        with open(self.save_file, "w") as save:
            for unit in self.__storage:
                unit_str = (str(unit[0]), str(unit[1]), unit[2])
                saved_line = compose(unit_str, '|', end='\n')
                save.write(saved_line)

    def deserialize(self):
        self.__storage = []
        with open(self.save_file, "r") as save:
            lines = save.readlines()
            for line in lines:
                line = line.rstrip()
                items = separate(line, '|', 2, False)
                if len(items) == 3:
                    time, uid, content = items
                    time = datetime.fromisoformat(time)
                    uid = userid(uid)
                    self.__storage.append((time, uid, content))
                else:
                    continue

    def retrieve(self, start: datetime, end: datetime, number_limit: int = None,
                 reverse: bool = False) -> List[StorageUnit]:
        """

        :param start:the beginning time of message retrieval.
        :param end:the ending time of message retrieval.
        :param number_limit:the max number of message retrieval.If None,retrieves all.
        :param reverse:If true,retrieves msg starting from end datetime.Otherwise starting from start datetime.
        :return:
        """
        start = min(start, end)
        end = max(start, end)

        if self.changed:
            self.sort()
        snapshot = self.__storage[:]
        dt_snapshot = [unit[0] for unit in self.__storage]
        _, start_pos = utils.find_range(dt_snapshot, start)
        end_pos, _ = utils.find_range(dt_snapshot, end)
        if reverse:
            inrange = snapshot[start_pos:end_pos:-1]
        else:
            inrange = snapshot[start_pos:end_pos]
        if number_limit is None:
            return inrange
        else:
            return inrange[number_limit:]


class tab:
    def __init__(self):
        self.history: List[str] = []

    def add_msg(self, msg):
        self.history.append(msg)


class chat_tab(tab):
    pass


class setting_tab(tab):
    pass


class main_menu_tab(tab):
    pass


class tablist:
    def __init__(self, win: "window"):
        self.tabs: List[tab] = []
        self.cur: Optional[tab] = None
        self.win = win
        self.view_history = []
        self.max_view_history = 5

    def add(self, tab: tab):
        self.tabs.append(tab)

    def remove(self, item: Union[int, tab]):
        if isinstance(item, int):
            del self.tabs[item]
        elif isinstance(item, tab):
            self.tabs.remove(item)

    def switch(self):
        if len(self.view_history) >= 2:
            self.goto(self.view_history[-1])

    def goto(self, number: int):
        if 0 <= number < len(self.tabs):
            self.cur = self.tabs[number]
            self.add_view_history(number)

    def add_view_history(self, number: int):
        self.view_history.append(number)
        if len(self.view_history) > self.max_view_history:
            self.view_history = self.view_history[-self.max_view_history:]


class window:
    def __init__(self, displayer: output.i_display):
        self.history: List[str] = []
        self.max_display_line = 10
        self.displayer: output.i_display = displayer
        self.fill_until_max: bool = False
        self.tabli = tablist(self)

    def newtab(self):
        pass

    def display(self):
        clear_screen()
        if len(self.history) < self.max_display_line:
            displayed = self.history
            have_rest = True
        else:
            displayed = self.history[-self.max_display_line]
            have_rest = False
        for d in displayed:
            self.displayer.display_text(d, end="\n")
        if have_rest and self.fill_until_max:
            displayed_len = len(displayed)
            for i in range(self.max_display_line - displayed_len):
                self.displayer.display_text(end="\n")

    def add_text(self, text: str):
        self.history.append(text)

    def clear_all(self):
        self.history = []
