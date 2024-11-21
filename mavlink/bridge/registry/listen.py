from msg.mavlink_message import MavlinkMessage

class ListenMessageRegistry:
    def __init__(self):
        self.msgs = []

    def register(self, msg_type):
        self.msgs.append(msg_type)


def setup_listen_msgs():

    registry = ListenMessageRegistry()

    registry.register(MavlinkMessage.get_pdu_msg_type("AHRS2"))
    registry.register(MavlinkMessage.get_pdu_msg_type("SERVO_OUTPUT_RAW"))

    return registry
