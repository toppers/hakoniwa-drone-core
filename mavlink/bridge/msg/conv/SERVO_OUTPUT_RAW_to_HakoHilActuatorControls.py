from msg.pdu_message import PduMessage

class SERVO_OUTPUT_RAWToHakoHilActuatorControlsConvertor:
    def __init__(self):
        """
        SERVO_OUTPUT_RAWからHakoHilActuatorControlsへのコンバータ
        """
        pass  # 必要なら初期化処理を追加

    def get_duty(self, pwm: float):
        if pwm < 1000.0:
            return 0
        else:
            return (pwm - 1000.0) / 1000.0

    def convert(self, pdu_message: PduMessage) -> PduMessage:
        """
        HakoSERVO_OUTPUT_RAWをHakoHilActuatorControlsに変換
        :param pdu_message: HakoSERVO_OUTPUT_RAWデータを含むPduMessage
        :return: HakoHilActuatorControlsデータを含むPduMessage
        """
        if pdu_message.data is None:
            raise ValueError("PduMessage data is empty")

        # HakoSERVO_OUTPUT_RAWデータの取得
        time_usec = pdu_message.data.get("time_usec")
        port = pdu_message.data.get("port")
        servo_values = [
            pdu_message.data.get(f"servo{i}_raw") for i in range(1, 9)
        ]

        if None in servo_values or time_usec is None or port is None:
            raise ValueError("Missing required HakoSERVO_OUTPUT_RAW fields")

        # HakoHilActuatorControlsへの変換
        controls = [ self.get_duty(value) if value is not None else 0.0 for value in servo_values]
        controls.extend([0.0] * (16 - len(controls)))  # 配列を16要素に拡張

        hako_hil_data = {
            "time_usec": time_usec,
            "controls": controls,
            "mode": port,  # モードとしてポート番号を使用
            "flags": 0,    # フラグは未使用 (必要なら設定)
        }

        # 新しいPduMessageとしてHakoHilActuatorControlsを返す
        return PduMessage(
            robot_name=pdu_message.robot_name,
            channel_id=pdu_message.channel_id,
            size = 112,
            data=hako_hil_data,
        )
