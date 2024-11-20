class PduMessage:
    def __init__(self, robot_name, channel_id, size, data):
        """
        PduMessageクラス
        :param robot_name: ロボット名
        :param channel_id: チャネルID
        :param size: PDUサイズ
        :param data: メッセージデータ（辞書形式）
        """
        self.robot_name = robot_name
        self.channel_id = channel_id
        self.pdu_size = size
        self.data = data

    def __repr__(self):
        """
        メッセージの文字列表現を返す
        """
        return (
            f"<PduMessage robot_name={self.robot_name}, "
            f"channel_id={self.channel_id}, pdu_size={self.pdu_size}, data={self.data}>"
        )
