import msvcrt
import sys
import utils

from ui.nonblock import is_key
from ui.client import textbox

tb = textbox()
tb.update("apple")


def test_textbox():
    for i in range(20):
        tb.left()
        print(tb.get())


#test_textbox()


def cmd_input():
    while True:
        utils.clear_screen()
        print(tb.get())
        if msvcrt.kbhit():
            number = ord(msvcrt.getwch())
            if number == 27:
                sys.exit()
            elif number == 224:
                key2 = ord(msvcrt.getwch())
                if key2 == 80:
                    print("Down")
                elif key2 == 72:
                    print("Up")
                elif key2 == 75:
                    tb.left()
                    # print("Left")
                elif key2 == 77:
                    tb.right()
                    # print("Right")

#cmd_input()

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
