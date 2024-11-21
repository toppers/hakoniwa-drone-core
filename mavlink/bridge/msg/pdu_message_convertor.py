import json
from msg.mavlink_message import MavlinkMessage
from msg.pdu_message import PduMessage

class PduMessageConvertor:
    def __init__(self, mavlink_config_path, pdu_config_path, comm_config_path):
        """
        PduMessageConvertorクラス
        :param mavlink_config_path: mavlink custom.json ファイルのパス
        :param pdu_config_path: pdu custom.json ファイルのパス
        :param comm_config_path: comm_config.json ファイルのパス
        """
        # custom.json の読み込み
        with open(mavlink_config_path, "r") as custom_file:
            self.mavlink_config = json.load(custom_file)

        with open(pdu_config_path, "r") as custom_file:
            self.pdu_config = json.load(custom_file)

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
        #print(f"robot_name: {robot_name}, msg_type: {msg_type}")
        for robot in self.pdu_config["robots"]:
            if robot["name"] == robot_name:
                for reader in robot["shm_pdu_readers"]:
                    if reader["type"] ==  msg_type:
                        return reader["channel_id"], reader["pdu_size"]
        return None

    def create_pdu(self, mavlink_message):
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
        #channel_id, pdu_size= self.get_pdu_info(robot_name, mavlink_message.msg_type)
        #if channel_id is None:
        #    raise ValueError(f"Cannot find channel ID for robot {robot_name} and message type {mavlink_message.msg_type}")

        return PduMessage(
            robot_name=robot_name,
            msg_type = mavlink_message.msg_type,
            data=mavlink_message.msg_data
        )
    def compile_pdu(self, pdu_message):
        """
        PduMessageをPDUに変換
        :param pdu_message: PduMessageオブジェクト
        :return: PDUデータ
        """

        # チャネルID と PDUサイズを取得
        channel_id, pdu_size= self.get_pdu_info(pdu_message.robot_name, pdu_message.msg_type)
        if channel_id is None:
            raise ValueError(f"Cannot find channel ID for robot {pdu_message.robot_name} and message type {pdu_message.msg_type}")

        pdu_message.channel_id = channel_id
        pdu_message.pdu_size = pdu_size
        return pdu_message
