from core.event import event
from ui.client import client
from ui import output
from socket import socket, AF_INET, SOCK_STREAM
import sys
import threading
from threading import Lock, Thread
import time
import os
from ui.client import client


def main():
    _client = client()

    _client.init_connect(("127.0.0.1", 5000))
    _client.connect()
    _client.start()

    def cmd_input():
        while True:
            res = input("Enter:")
            if res == "#":
                break
            print(res)

    _cmd_input = Thread(target=cmd_input)
    _cmd_input.start()


if __name__ == '__main__':
    main()
    print()
