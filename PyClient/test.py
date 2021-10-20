#import msvcrt
import sys
#3from ui.nonblock import is_key
"""
while True:
    if msvcrt.kbhit():
        c: str = msvcrt.getwch()
        if is_key(c[0], b'\x1b'):
            sys.exit()
        else:
            print(c)

"""

class a:
    def __init__(self,arg=1):
        self.arg=arg

class b(a):
    """
        def __init__(self):
            super().__init__()
    """
    def test(self):
        print(self.arg)

_b=b()
_b.test()

