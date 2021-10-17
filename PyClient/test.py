from network.network import channel

c = channel("test name")


def handle(msg, context):
    pass


class msg:
    MessageID = "MSG"
    pass


c.register(msg_type=msg, msg_id="Abc")

import json

j = '{ \
    "test":"01"\
  }'

jobj = json.loads(j)

print(type(jobj))

print()
