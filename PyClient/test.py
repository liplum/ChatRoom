import xautofill
from ui.controls import textbox
from utils import *
from core import converts

from ui.clients import *
from chars import *

import time
import calendar
from datetime import datetime, timezone
import platform
import traceback
import dictries
import sys
import autofill

system_type = platform.system()

if system_type == "Windows":
    import msvcrt
elif system_type == "Linux":
    import select
    import tty
    import termios


def win_test():
    # test_input()
    # cmd_input()
    # test_str()
    # test_textbox()
    # test_char()
    # test_fill()
    # test_decode_str()
    # cls_static()
    # utc()
    # eof_test()
    # test_dictrie()
    # test_dictrie2()
    test_autofill()


def linux_test():
    # nb_linux()
    # linux_nb()
    test_dictrie2()


def test():
    pass


if system_type == "Windows":
    test = win_test
elif system_type == "Linux":
    test = linux_test


def test_autofill():
    p = autofill.prompt()
    # p = xautofill.autoprompt()
    p.add("apple").add("animation").add("animadvert").add("abuse").add("authority").add("abort")
    p.add("append").add("ant").add("aunt").add("but").add("boy").add("butter").add("ok")
    p.add("onion").add("log").add("father").add("tea").add("tree").add("dictionary")
    p.add("trie")

    # print(dictries.get_partial_start_with(p.tree.root, "a", 4))

    def get_or_zero(dic, key) -> int:
        if key in dic:
            return dic[key]
        else:
            return 0

    while True:
        print("---------------------")
        if isinstance(p, xautofill.autoprompt):
            print(f'max : {p.max_candidate}')
        prefix = input("Enter prefix:")
        if prefix == "#":
            break
        candidates = p.autofill(prefix)
        if len(candidates) == 0:
            print("No candidate.")
            continue
        for i, can in enumerate(candidates):
            text = utils.fillto(f"[{i + 1}]:{can}", " ", 30)
            hotlevel = f"hot:{get_or_zero(p.hotwords, can)}"
            print(f"{text}{hotlevel}")
        try:
            number = int(input("Enter number:").strip())
        except:
            print("Input Error!")
            continue
        index = number - 1
        if 0 <= index < len(candidates):
            selected = candidates[index]
            p.apply(selected)
            print(f"You select {selected}.")
        else:
            print("Input Error!")


def test_dictrie2():
    tree = dictries.dictrie()
    tree.insert_word("animal")
    tree.insert_word("animation")
    tree.insert_word("animadvert")
    tree.insert_word("abuse")
    tree.insert_word("audio")
    tree.insert_word("ant")
    tree.insert_word("but")
    tree.insert_word("butter")
    tree.insert_word("ok")
    tree.insert_word("onion")
    tree.insert_word("tea")
    tree.insert_word("tree")
    tree.insert_word("trie")
    tree.insert_word("dictionary")
    print(str(tree))
    print(str(tree.word_count))

    node_animadvert = tree['a']['n']['i']['m']['a']['d']['v']['e']['r']['t']

    n5_1 = tree.root['a']['n']['i']['m']
    arg1 = get_at(sys.argv, 1)
    if arg1:
        print(tree.get_all_start_with(arg1))

    starter = "an"
    print(f'Start with "{starter}" in tree = {tree.get_all_start_with(starter)}')
    dictries.insert_word(tree.root, "key")
    ###############
    test = "key"
    print(f'Tree has "{test}" = {tree.has(test)}')
    ###############
    test = "but"
    print(f'Delete "but" = {tree.remove_word("but")}')
    print(f'Tree has "{test}" = {tree.has(test)}')
    ###############
    test = "butter"
    print(f'Tree has "{test}" = {tree.has(test)}')
    ###############
    print(f'"ani"\'s subnodes = {dictries.get_subnodes_str(tree["a"]["n"]["i"])}')
    ###############
    print(f'root\'s subnodes = {dictries.get_subnodes_str(tree.root)}')
    ###############
    print(f'root\'s subnodes count = {dictries.get_subnode_count(tree.root)}')
    ###############
    # print(tree.get_all_start_with("anim"))
    print(str(tree.word_count))

    """
    print(node_animadvert)
    last_branch_of_node_animadvert = dictries.get_last_branch_node(node_animadvert)
    print(last_branch_of_node_animadvert)

    res = tree.get_all_start_with("an")

    print(res)

    print(f'Tree has "ant" = {tree.has("ant")}')
    print(f'Tree has "an" = {tree.has("an")}')
    print(f'Tree has prefix "an" = {tree.has_start_with("an")}')
    print(f'Tree has "but" = {tree.has("but")}')
    print(f'Tree has "butter" = {tree.has("butter")}')
    print()
    print(tree)
    print(f'Delete "bu" = {tree.remove_word("bu")}')
    print(f'Delete "but" = {tree.remove_word("but")}')
    print(tree)
    print(f'Delete "butter" = {tree.remove_word("butter")}')
    print(tree)
    """


def test_dictrie():
    tree = dictries.dictrie()
    tree.insert_word("ap ple")
    tree.insert_word("animal")
    tree.insert_word("banana")
    tree.insert_word("baby")
    tree.insert_word("but")
    tree.insert_word("butter")
    print(tree)
    print(f'Tree has "ap ple" = {tree.has("ap ple")}')
    print(f'Tree has "baby" = {tree.has("baby")}')
    print(f'Tree has "bar" = {tree.has("bar")}')
    print(f'Tree has "ba" = {tree.has("ba")}')
    print(f'Tree has "but" = {tree.has("but")}')
    print(f'Tree has "butter" = {tree.has("butter")}')
    print(f'Tree has start with "ap p" = {tree.has_start_with("ap p")}')
    print(f'Tree has start with "baby" = {tree.has_start_with("baby")}')
    print(f'Tree has start with "bar" = {tree.has_start_with("bar")}')
    print(f'Tree has start with "ba" = {tree.has_start_with("ba")}')
    print(f'Tree has start with "b" = {tree.has_start_with("b")}')

    print(f'Delete "b" = {tree.remove_word("b")}')
    print(f'Delete "bu" = {tree.remove_word("bu")}')
    print(f'Delete "bananana" = {tree.remove_word("bananana")}')
    print(f'Delete "banana" = {tree.remove_word("banana")}')
    print(tree)
    print(f'Delete prefix "bu" = {tree.remove_start_with("bu")}')
    print(tree)
    print(f'Delete prefix "a" = {tree.remove_start_with("a")}')
    print(tree)


def eof_test():
    try:
        res = input()
        print(res)
    except EOFError:
        print("EOF!!!")
    res = input()
    print(res)


def cls_static():
    class a:
        t = 10

        def __init__(self):
            self.t = 9

    class b:
        t = 10

        def __init__(self):
            self.t = 9

    _a = a()
    print(_a.t)
    print(type(_a).t)


def test_decode_str():
    bs = b'Abc'
    res1 = converts.read_str(bs, False)
    print(compose(bs))
    print(res1)


def test_fill():
    s1 = fill("Abc", "-*-", 10, 22)
    s2 = fill("Abc", "-*-", 10, 21)
    s3 = fillto("Abc", "-*-", 22)
    s4 = fillto("Abc", "-*-", 21)
    s5 = fillto("Command mode:", "-/-", 50)

    print(f"fill [{len(s1)}] {s1}")
    print(f"fill [{len(s2)}] {s2}")
    print(f"fillby [{len(s3)}] {s3}")
    print(f"fillby [{len(s4)}] {s4}")
    print(f"fillby [{len(s5)}] {s5}")


def nb_linux():
    def is_input():
        return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())

        while True:
            while is_input():
                c = sys.stdin.read(1)
                """if c == '\x1b':  # x1b is ESC
                    break"""
                print(f"{c} {type(c)} {len(c)} {ord(c[0])}")
                readable = sys.stdin.readable()
                print(readable)
                if not readable:
                    break

    except:
        traceback.print_exc()
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


def linux_nb():
    def getchar():
        fd = sys.stdin.fileno()
        attr = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSANOW, attr)

    EOT = '\x04'  # CTRL+D
    ESC = '\x1b'
    CSI = '['

    line = ''

    while True:
        c = getchar()
        if c == EOT:
            print('exit')
            break
        elif c == ESC:
            if getchar() == CSI:
                x = getchar()
                if x == 'A':
                    print('UP')
                elif x == 'B':
                    print('DOWN')
        elif c == '\r':
            print([line])
            line = ''
        else:
            line += c


def test_input():
    while True:
        if msvcrt.kbhit():
            ch = msvcrt.getwch()
            ch_number = ord(ch)
            if ch_number == f_keycode_1 or ch_number == control_keycode_1:
                ch_2 = msvcrt.getwch()
                ch_2_number = ord(ch_2)
                print(f"control char is {ch_number}+{ch_2_number}")
            else:
                print(f"{ch} is {ch_number}")


def test_textbox():
    tb = textbox()
    tb.on_cursor_move.add(cursor_changed)
    tb.input_list = "apple"
    print("\nmove left\n")
    for i in range(10):
        tb.left()
        print(tb.distext)
    print("\nappend\n")
    for i in range(5):
        tb.append("1")
        print(tb.distext)
    print("\nmove left\n")
    tb.left()
    print(tb.distext)
    tb.left()
    print(tb.distext)
    print("\ndelete\n")
    for i in range(10):
        tb.delete()
        print(tb.distext)

    print("\nmove right\n")
    tb.right()
    print(tb.distext)
    tb.right()
    print(tb.distext)
    tb.right()
    print(tb.distext)

    print("\ndelete\n")
    for i in range(3):
        tb.delete()
        print(tb.distext)


def cmd_input():
    tb = textbox()
    tb.input_list = "apple"
    while True:
        utils.clear_screen()
        print(tb.distext)
        print(tb._cursor)
        if msvcrt.kbhit():
            ch = msvcrt.getwch()
            ch_number = ord(ch)
            if char_esc == ch:
                sys.exit()
            elif ch_number == control_keycode_1:
                ch_full = control(ord(msvcrt.getwch()))
                if ch_full == char_down:
                    print("Down")
                elif ch_full == char_up:
                    print("Up")
                elif ch_full == char_left:
                    tb.left()
                elif ch_full == char_right:
                    tb.right()
            elif ch_number == f_keycode_1:
                ch_full = f(ord(msvcrt.getwch()))
                print(ch_full.keycode_2)
            elif ch_number == char_backspace:
                tb.delete()
            else:
                tb.append(ch)


def test_char():
    c_2 = printable('2')
    print(f"c_2 equals char_2 ? :{c_2 == char_2}")
    print(f'c_2 equals string "2" ? :{c_2 == "2"}')
    print(f'c_2 equals int 50 ? :{c_2 == 50}')
    print(f"c_2 equals char_c ? :{c_2 == char_c}")
    print(f"c_2 equals string '<space>' ? :{c_2 == char_space}")
    print(f"c_2 equals string '我' ? :{c_2 == '我'}")
    print(f'c_2 equals int 49 ? :{c_2 == 49}')


def local_to_utc(t):
    secs = time.mktime(t)
    return time.gmtime(secs)


def utc_to_local(t):
    secs = calendar.timegm(t)
    return time.localtime(secs)


def utc():
    now_dt = datetime.now()
    now = now_dt.utctimetuple()
    now_secs = calendar.timegm(now)
    utc_now = datetime.utcnow()
    utc_now_converted = local_to_utc(now)
    utc_now_converted_secs = calendar.timegm(utc_now_converted)
    print(f"local:{now_dt}")
    print(f"local:{now}")
    print(f"local sec:{now_secs}")
    print(f"utc:{utc_now}")
    print(f"utc(converted):{utc_now_converted}")
    print(f"utc sec(converted):{utc_now_converted_secs}")
    print()
    back_utc = datetime.fromtimestamp(utc_now_converted_secs, tz=timezone.utc)
    back_local = datetime.fromtimestamp(utc_now_converted_secs)
    print(f"back to local:{back_local}")
    print(f"back to utc:{back_utc}")
    now_iso = now_dt.isoformat()
    print(f"to iso:{now_iso}")
    back_iso = datetime.fromisoformat(now_iso)
    print(f"from iso:{back_iso}")
    print(f"re-back iso:{back_iso.isoformat()}")
    print(f"utc to iso:{back_local.isoformat()}")


# utc()


def test_str():
    print(utils.separate("apple|banana|orange|peach||||", '|', number=2, allow_emptychar=False))
    print(utils.compose(["abc", {}, [], set(), '12333'], connector=","))


def printall(li):
    for item in li:
        print(compose(item))


def test_msgstorage():
    st = msgstorage("record.rec")
    st.deserialize()
    st.sort()
    print("all")
    printall(st)
    print()
    st.serialize()
    start = datetime(2021, 10, 1)
    end = datetime(2021, 11, 1)
    print(str(start))
    print(str(end))
    d2021_10_1_to_2021_11_1 = st.retrieve(start, end)
    print()
    print("2021/10/1 to 2021/11/1 is following:")
    printall(d2021_10_1_to_2021_11_1)


# test_msgstorage()

def test_find():
    li = [1, 10, 18, 30, 75, 126]
    res = utils.find_range(li, 10)
    print(compose(res))


# test_find()

def test_insert():
    li = [1, 2, 3]
    li.insert(3, 4)
    print(li)


# test_insert()

def test_dataclass():
    from dataclasses import dataclass

    @dataclass
    class d:
        string: str = ""

    a = d("abc")
    a.string = "bcd"
    print(a.string)


# test_dataclass()

def test_set():
    s = set()
    s.add(2)
    s.add(5)
    s.add(7)
    s.add(11)
    print(compose(s))
    for i in s:
        if i == 5:
            s.remove(5)
            break
    print(compose(s))


# test_set()

def test_color_cmd():
    text = "_______-------------++++++++++++========="
    print(f"\033[0;34;40m{text}\033[0m")


# test_color_cmd()

test()
"""
while True:
    c = ""
    if msvcrt.kbhit() > 0:
        c += msvcrt.getwch()
        c += msvcrt.getwch()

    if is_key(c, b'\x1b'):
        sys.exit()
    elif c != "":
        print(f"char is {c} and {c.encode()}")
""""""
while True:
    number = ord(msvcrt.getwch())
    if number == 27:
        sys.exit()
    elif number == 224:
        key2 = ord(msvcrt.getwch())
        if key2 == 80:
            print("Down")
        elif key2 == 72:
            print("Up")

    elif number == 0:
        key2 = ord(msvcrt.getwch())
        if key2 == 59:
            print("F1")
    else:
        print(number)
"""
"""
while True:
    if msvcrt.kbhit():
        c: str = msvcrt.getwch()
        if is_key(c[0], b'\x1b'):
            sys.exit()
        else:
            print(c)

"""
