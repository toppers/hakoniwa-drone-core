import json
from msg.mavlink_message import MavlinkMessage
from msg.pdu_message import PduMessage

class PduMessageConvertor:
    def __init__(self, custom_config_path, comm_config_path):
        """
        PduMessageConvertorクラス
        :param custom_config_path: custom.json ファイルのパス
        :param comm_config_path: comm_config.json ファイルのパス
        """
        # custom.json の読み込み
        with open(custom_config_path, "r") as custom_file:
            self.custom_config = json.load(custom_file)

        # comm_config.json の読み込み
        with open(comm_config_path, "r") as comm_file:
            self.comm_config = json.load(comm_file)

    def get_robot_name(self, ip_addr, port):
        """
        IPアドレスとポートからロボット名を特定
        :param ip_addr: MAVLinkメッセージのIPアドレス
        :param port: MAVLinkメッセージのポート番号
        :return: ロボット名
        """
        for robot_name, robot_info in self.comm_config["vehicles"].items():
            if robot_info["ip_address"] == ip_addr and robot_info["port"] == port:
                return robot_name
        return None

    def get_pdu_info(self, robot_name, msg_type):
        """
        ロボット名とデータ型からチャネルIDを取得
        :param robot_name: ロボット名
        :param msg_type: MAVLinkメッセージのデータ型
        :return: チャネルID
        """
        for robot in self.custom_config["robots"]:
            if robot["name"] == robot_name:
                for reader in robot["shm_pdu_readers"]:
                    if reader["type"] == "hako_mavlink_msgs/Hako" + msg_type:
                        return reader["channel_id"], reader["pdu_size"]
        return None

    def convert(self, mavlink_message):
        """
        MavlinkMessageをPduMessageに変換
        :param mavlink_message: MavlinkMessageオブジェクト
        :return: PduMessageオブジェクト
        """
        # ロボット名を取得
        robot_name = self.get_robot_name(mavlink_message.ip_addr, mavlink_message.port)
        if robot_name is None:
            raise ValueError(f"Cannot identify robot for IP {mavlink_message.ip_addr} and port {mavlink_message.port}")

        # チャネルID と PDUサイズを取得
        channel_id, pdu_size= self.get_pdu_info(robot_name, mavlink_message.msg_type)
        if channel_id is None:
            raise ValueError(f"Cannot find channel ID for robot {robot_name} and message type {mavlink_message.msg_type}")

        return PduMessage(
            robot_name=robot_name,
            channel_id=channel_id,
            size=pdu_size,
            data=mavlink_message.msg_data
        )
