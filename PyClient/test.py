import msvcrt
import sys
import utils

from ui.nonblock import is_key
from ui.client import *
from chars import *

import time
import calendar
from datetime import datetime, timezone
from io import StringIO


def test_input():
    while True:
        if msvcrt.kbhit():
            ch = msvcrt.getwch()
            print(f"{ch} is {ord(ch)}")


# test_input()

def test_textbox():
    tb = textbox()
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


# test_textbox()


def cmd_input():
    tb = textbox()
    tb.input_list = "apple"
    while True:
        utils.clear_screen()
        print(tb.distext)
        print(tb.cursor_pos)
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
            elif ch_number == char_delete:
                tb.delete()
            else:
                tb.append(ch)


# cmd_input()


def test_char():
    c_2 = printable('2')
    print(f"c_2 equals char_2 ? :{c_2 == char_2}")
    print(f'c_2 equals string "2" ? :{c_2 == "2"}')
    print(f'c_2 equals int 50 ? :{c_2 == 50}')
    print(f"c_2 equals char_c ? :{c_2 == char_c}")
    print(f"c_2 equals string '<space>' ? :{c_2 == char_space}")
    print(f"c_2 equals string '我' ? :{c_2 == '我'}")
    print(f'c_2 equals int 49 ? :{c_2 == 49}')


# test_char()

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
    utc_now_converted = local_to_utc(now)
    utc_now_converted_secs = calendar.timegm(utc_now_converted)
    print(f"local:{now}")
    print(f"local sec:{now_secs}")
    print(f"utc:{utc_now_converted}")
    print(f"utc sec:{utc_now_converted_secs}")
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


# test_str()

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

print([].pop(0))
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
