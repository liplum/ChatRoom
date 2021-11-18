import net.msgs as msgs
from core.shared import *
from net.networks import i_network

def connect(network: i_network, server: server_token):
    if not network.is_connected(server):
        network.connect(server)

def login(network: i_network, server: server_token, account: str, password: str):
    user = network.get_channel("User")
    msg = msgs.authentication_req()
    msg.account = account
    msg.password = password
    user.send(server, msg)
