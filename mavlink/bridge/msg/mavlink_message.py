class MavlinkMessage:
    def __init__(self, ip_addr, port, msg_type, msg_data):
        """
        MavlinkMessageオブジェクト
        :param ip_addr: 送信元または受信先のIPアドレス
        :param port: 送信元または受信先のポート番号
        :param msg_type: メッセージタイプ（例: "GLOBAL_POSITION_INT", "AHRS2"）
        :param msg_data: メッセージデータ（辞書形式）
        """
        self.ip_addr = ip_addr
        self.port = port
        self.msg_type = MavlinkMessage.get_pdu_msg_type(msg_type)
        self.msg_data = msg_data

    @staticmethod
    def get_pdu_msg_type(msg_type):
        """
        メッセージからメッセージタイプを取得
        :param msg_type: pymavlinkのメッセージオブジェクト
        :return: メッセージタイプ
        """
        return "hako_mavlink_msgs/Hako" + msg_type

    def to_dict(self):
        """
        メッセージを辞書形式で返す
        :return: メッセージ内容を含む辞書
        """
        return {
            "ip_addr": self.ip_addr,
            "port": self.port,
            "msg_type": self.msg_type,
            "msg_data": self.msg_data,
        }

    def is_valid(self):
        """
        メッセージの妥当性をチェック
        :return: メッセージが妥当であればTrue、そうでなければFalse
        """
        # 必須フィールドが揃っているか確認
        return (
            self.ip_addr is not None
            and self.port is not None
            and self.msg_type is not None
            and isinstance(self.msg_data, dict)
        )

    def __repr__(self):
        """
        メッセージの文字列表現を返す
        """
        return (
            f"<MavlinkMessage ip_addr={self.ip_addr}, port={self.port}, "
            f"type={self.msg_type}, data={self.msg_data}>"
        )

    def __eq__(self, other):
        """
        メッセージの等価性を比較
        :param other: 比較対象のMavlinkMessageオブジェクト
        :return: メッセージが等価であればTrue、そうでなければFalse
        """
        if not isinstance(other, MavlinkMessage):
            return False
        return (
            self.ip_addr == other.ip_addr
            and self.port == other.port
            and self.msg_type == other.msg_type
            and self.msg_data == other.msg_data
        )
