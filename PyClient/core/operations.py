import net.msgs as msgs
from core.shared import *
from net.networks import inetwork


def connect(network: inetwork, server: server_token, strict: bool = False):
    if not network.is_connected(server):
        network.connect(server, strict)


def login(network: inetwork, server: server_token, account: str, password: str):
    connect(network, server)
    user = network.get_channel("User")
    msg = msgs.authentication_req()
    msg.account = account
    msg.password = password
    user.send(server, msg)


def register(network: inetwork, server: server_token, account: str, password: str):
    connect(network, server)
    uc = network.get_channel("User")
    msg = msgs.register_request()
    msg.account = account
    msg.password = password
    uc.send(server, msg)


def join(network: inetwork, userinfo:uentity, room_id: roomid):
    server = userinfo.server
    connect(network, server)
    uc = network.get_channel("User")
    msg = msgs.join_room_req()
    msg.account = userinfo.account
    msg.room_id = room_id
    msg.vcode = userinfo.vcode
    uc.send(server, msg)

def create_room(network: inetwork, userinfo:uentity, room_name:str):
    server = userinfo.server
    connect(network, server)
    uc = network.get_channel("User")
    msg = msgs.create_room_req()
    msg.account = userinfo.account
    msg.room_name = room_name
    msg.vcode = userinfo.vcode
    uc.send(server, msg)

def send_text(network: inetwork,user_info: uentity, room_id: roomid, text: str):
    server = userinfo.server
    connect(network, server)
    chatting = network.get_channel("Chatting")
    msg = msgs.chatting()
    msg.room_id = room_id
    msg.send_time = datetime.utcnow()
    msg.text = text
    msg.vcode = user_info.vcode
    msg.account = user_info.account
    chatting.send(server, msg)
