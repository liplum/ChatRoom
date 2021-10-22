import msvcrt
import sys
import utils

from ui.nonblock import is_key
from ui.client import textbox
from chars import *

import time
import calendar
from datetime import datetime, timezone

tb = textbox()
tb.update("apple")


def test_textbox():
    for i in range(20):
        tb.left()
        print(tb.get())


# test_textbox()


def cmd_input():
    while True:
        utils.clear_screen()
        print(tb.get())
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
                    # print("Left")
                elif ch_full == char_right:
                    tb.right()
                    # print("Right")
            elif ch_number == f_keycode_1:
                ch_full = f(ord(msvcrt.getwch()))
                print(ch_full.keycode_2)


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
    now = datetime.now().utctimetuple()
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


utc()

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
