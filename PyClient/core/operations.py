import net.msgs as msgs
from core.shared import *
from net.networks import inetwork


def connect(network: inetwork, server: server_token, strict: bool = False):
    if not network.is_connected(server):
        network.connect(server, strict)


def login(network: inetwork, server: server_token, account: str, password: str):
    connect(network,server)
    user = network.get_channel("User")
    msg = msgs.authentication_req()
    msg.account = account
    msg.password = password
    user.send(server, msg)


def register(network: inetwork, server: server_token, account: str, password: str):
    connect(network,server)
    uc = network.get_channel("User")
    msg = msgs.register_request()
    msg.account = account
    msg.password = password
    uc.send(server, msg)
