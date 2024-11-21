import hako_pdu
import hakopy
import os

from msg.pdu_message import PduMessage

class HakoBridgePduWriter:
    def __init__(self, config_path: str):
        hako_binary_path = os.getenv('HAKO_BINARY_PATH', '/usr/local/lib/hakoniwa/hako_binary/offset')
        self.pdu_manager = hako_pdu.HakoPduManager(hako_binary_path, config_path)
        #ret = hakopy.init_for_external()
        #if ret == False:
        #    raise ValueError("Failed to initialize Hakopy")

    def write_pdu_message(self, pdu_message: PduMessage):
        """
        PduMessageデータをHakoniwa PDUに書き込む
        :param pdu_message: 書き込み対象のPduMessageオブジェクト
        """
        pdu = self.pdu_manager.get_pdu(pdu_message.robot_name, pdu_message.channel_id)
        pdu.obj = pdu_message.data
        pdu.write()
