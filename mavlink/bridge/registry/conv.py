from msg.mavlink_message import MavlinkMessage
from msg.conv.AHRS2_to_Twist import AHRS2ToTwistConvertor
from msg.conv.SERVO_OUTPUT_RAW_to_HakoHilActuatorControls import SERVO_OUTPUT_RAWToHakoHilActuatorControlsConvertor

class ConverterRegistry:
    def __init__(self):
        self._converters = {}

    def register(self, msg_type, converter):
        """
        コンバータをメッセージタイプに関連付けて登録
        :param msg_type: MAVLinkメッセージタイプ (例: "AHRS2")
        :param converter: コンバータインスタンス
        """
        self._converters[msg_type] = converter

    def get_converter(self, msg_type):
        """
        指定したメッセージタイプに対応するコンバータを取得
        :param msg_type: MAVLinkメッセージタイプ
        :return: コンバータインスタンス (該当なしの場合はNone)
        """
        return self._converters.get(msg_type)


def setup_converters():
    """
    コンバータを初期化して登録
    :return: ConverterRegistry インスタンス
    """
    registry = ConverterRegistry()

    # AHRS2 → Twist変換コンバータ
    registry.register(
        MavlinkMessage.get_pdu_msg_type("AHRS2"),
        AHRS2ToTwistConvertor(ref_lat=-353632621, ref_lng=1491652374, ref_alt=584.0899658203125)
    )

    # SERVO_OUTPUT_RAW → HakoHilActuatorControls変換コンバータ
    registry.register(
        MavlinkMessage.get_pdu_msg_type("SERVO_OUTPUT_RAW"),
        SERVO_OUTPUT_RAWToHakoHilActuatorControlsConvertor()
    )

    return registry
