class PduMessage:
    def __init__(self, robot_name, channel_id, data):
        """
        PduMessageクラス
        :param robot_name: ロボット名
        :param channel_id: チャネルID
        :param data: メッセージデータ（辞書形式）
        """
        self.robot_name = robot_name
        self.channel_id = channel_id
        self.data = data

    def __repr__(self):
        """
        メッセージの文字列表現を返す
        """
        return (
            f"<PduMessage robot_name={self.robot_name}, "
            f"channel_id={self.channel_id}, data={self.data}>"
        )
