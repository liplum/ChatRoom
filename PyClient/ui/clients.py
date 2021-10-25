from typing import List, Dict, Tuple, Set

import core.ioc as ioc
from core.events import event
import ui.outputs as output
from threading import RLock
from network.network import i_network, server_token, userid
from network import network
import ui.inputs as _input
from utils import get, clear_screen, lock, clock, separate, compose
import utils
from typing import Optional, Union, Any, Tuple, List, Dict, Callable
from io import StringIO
from datetime import datetime
from dataclasses import dataclass
import chars


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


class state:
    def on_en(self):
        pass

    def on_ex(self):
        pass

    def update(self):
        pass

    def on_input(self, char: chars.char):
        pass


class smachine:
    def __init__(self, state_pre: Callable[[state], None] = None, stype_pre: Callable[[type], state] = None):
        self.cur: Optional[state] = None
        self.pre: Optional[state] = None
        self.state_pre = state_pre
        self.stype_pre = stype_pre

    def enter(self, s: Union[state, type]):
        if isinstance(s, state):
            if self.state_pre is not None:
                self.state_pre(s)
        elif isinstance(s, type):
            if self.stype_pre is not None:
                s = self.stype_pre(s)
            else:
                s = s()
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

    def on_input(self, char: chars.char):
        if self.cur is not None:
            self.cur.on_input(char)


class client_state(state):
    def __init__(self, client: "client"):
        super().__init__()
        self.client: "client" = client


class cmdkey:
    def __init__(self):
        self.mappings: Set[chars.char] = set()

    def map(self, char: chars.char) -> "cmdkey":
        self.mappings.add(char)
        return self

    def demap(self, char: chars.char, rematch: bool) -> "cmdkey":
        if rematch:
            for ch in self.mappings:
                if ch == char:
                    self.mappings.remove(ch)
                    break
        else:
            self.mappings.remove(char)
        return self

    def __eq__(self, other) -> bool:
        for ch in self.mappings:
            if ch == other:
                return True
        return False


class cmd_state(client_state):

    def on_en(self):
        self.client.set_changed()

    def update(self):
        c = self.client
        dlock = c.display_lock
        dlock(c.win.display)
        c.display.display_text("Command mode:",end='\n')
        tb = c.textbox.distext
        c.display.display_text(tb)

    def on_input(self, char: chars.char):
        c = self.client
        if c.key_enter_text == char:
            c.sm.enter(text_state)
        elif True:
            c.textbox.append(chars.to_str(char))


class text_state(client_state):

    def on_en(self):
        self.client.set_changed()

    def update(self):
        c = self.client
        dlock = c.display_lock
        dlock(c.win.display)
        c.display.display_text("Text mode:",end='\n')
        tb = c.textbox.distext
        c.display.display_text(tb)

    def on_input(self, char: chars.char):
        c = self.client
        if c.key_quit_text == char:
            c.sm.enter(cmd_state)
        elif True:
            c.textbox.append(chars.to_str(char))


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
        self._changed = False

    def init(self) -> None:
        self.container.register_singleton(output.i_logger, output.cmd_logger)
        self.container.register_singleton(output.i_display, output.cmd_display)
        self.network: network.network = network.network(self)
        self.container.register_instance(i_network, self.network)
        self.on_service_register(self.container)

        self.inpt: _input.i_input = self.container.resolve(_input.i_input)
        self.logger: output.i_logger = self.container.resolve(output.i_logger)
        self.logger.logfile = self.log_file
        self.display: output.i_display = self.container.resolve(output.i_display)
        self.win = window(self.display)
        self.win.fill_until_max = True
        self.gen_cmds()

        def set_client(state: state) -> None:
            state.client = self

        def gen_state(statetype: type) -> state:
            if issubclass(statetype, client_state):
                return statetype(self)
            else:
                return statetype()

        self.sm = smachine(state_pre=set_client, stype_pre=gen_state)

        self.textbox = textbox()

        self.textbox.on_append.add(lambda b, p, c: self.set_changed())
        self.textbox.on_delete.add(lambda b, p, c: self.set_changed())
        self.textbox.on_cursor_move.add(lambda b, f, c: self.set_changed())

        self.key_quit_text = cmdkey().map(chars.char_esc)
        self.key_enter_text = cmdkey().map(chars.char_t)

        def on_input(nbinput, char):
            ch = nbinput.consume_char()
            if ch is char:
                self.sm.on_input(ch)
            else:
                self.logger.error(f"Input event provides a wrong char '{ch} -> {char}'.")

        self.inpt.on_input.add(on_input)

    @property
    def need_update(self):
        return self._changed

    def set_changed(self):
        self._changed = True

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
        i = self.inpt
        i.initialize()
        dlock = self.display_lock
        sm = self.sm
        sm.enter(cmd_state)
        while self.running:
            self.inpt.get_input()
            # self.tps.delay()
            if not self.need_update:
                continue
            # The following is to need update
            sm.update()
            # dlock(self.display.display_text, self.command_list_tip)
            # dlock(self.display.display_text, "Enter a command:")
            inputs = i.input_list
            cmd_str = utils.compose(inputs)
            dlock(self.display.display_text, cmd_str)
            self.display.render()
            """ cmd: command = get(self.cmds.cmds, cmd_str)
            if cmd is not None:
                cmd.handler()
            else:
                self.logger.error(f"Cannot identify command {cmd_str}")
            self.display_lock(self.display.render())"""

    def display_lock(self, func, *args, **kwargs):
        lock(self._display_lock, func, *args, **kwargs)

    def add_text(self, text: str):
        self.win.add_text(text)

    def __init_channels(self):
        pass


@dataclass
class render_content:
    string: str


class textbox:
    def __init__(self, cursor_icon: str = "^"):
        self._input_list = []
        self.cursor_icon = cursor_icon
        self._cursor: int = 0
        self.cursor_pos: int = 0
        self._on_cursor_move = event()
        self._on_append = event()
        self._on_delete = event()
        self._on_gen_distext = event()

    @property
    def on_gen_distext(self) -> event:
        """
        Para 1:textbox object


        Para 2:the final string which will be displayed soon(render_content.string)

        :return: event(textbox,render_content)
        """
        return self._on_gen_distext

    @property
    def on_cursor_move(self) -> event:
        """
        Para 1:textbox object


        Para 2:former cursor position


        Para 3:current cursor position

        :return: event(textbox,int,int)
        """
        return self._on_cursor_move

    @property
    def on_append(self) -> event:
        """
        Para 1:textbox object


        Para 2:cursor position


        Para 3:char appended

        :return: event(textbox,int,str)
        """
        return self._on_append

    @property
    def on_delete(self) -> event:
        """
        Para 1:textbox object


        Para 2:cursor position


        Para 3:char deleted

        :return: event(textbox,int,str)
        """
        return self._on_delete

    @property
    def input_list(self):
        return self._input_list[:]

    @input_list.setter
    def input_list(self, value):
        if isinstance(value, list):
            self._input_list = value[:]
        else:
            self._input_list = list(value)

    def clear(self):
        self._input_list = []

    @property
    def cursor(self):
        return self._cursor

    @cursor.setter
    def cursor(self, value):
        list_len = len(self._input_list)
        former = self._cursor
        self._cursor = value % (list_len + 1)
        self.is_forwards = self._cursor >= 0
        if self.is_forwards:
            self.cursor_pos = self._cursor
        else:
            self.cursor_pos = list_len + self._cursor + 1
        self.on_cursor_move(self, former, self._cursor)

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

            res = s.getvalue()
            dis = render_content(res)
            self.on_gen_distext(self, dis)
            return dis.string

    def append(self, char):
        self._input_list.insert(self.cursor_pos, char)
        self.on_append(self, self.cursor, char)
        self.cursor += 1

    def delete(self):
        if self.cursor_pos > 0:
            ch = self._input_list.pop(self.cursor_pos - 1)
            self.on_delete(self, self.cursor, ch)
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
