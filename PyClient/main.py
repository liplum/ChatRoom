from core.event import event
from ui.client import client
from ui import output
from socket import socket, AF_INET, SOCK_STREAM
from core import convert

sk = socket(AF_INET, SOCK_STREAM)
sk.connect(("127.0.0.1", 5000))

while True:
    data = sk.recv(1024)
    data_length = convert.read_int(data[0:4])
    string = convert.read_str(data[4:4 + data_length])
    print(string)
    print("end")
