import asyncio
import hakopy
import threading
import json
import time

def write_pdu_message(pdu_message):
    """
    PduMessageデータをHakoniwa PDUに書き込む
    :param pdu_message: 書き込み対象のPduMessageオブジェクト
    """
    robot_name = pdu_message.robot_name
    channel_id = pdu_message.channel_id
    pdu_data = pdu_message.data
    pdu_size = len(pdu_data)  # データサイズを取得

    # Hakoniwa PDUに書き込み
    ret = hakopy.pdu_write(robot_name, channel_id, pdu_data, pdu_size)
    if not ret:
        print(f"ERROR: Failed to write PDU data for robot={robot_name}, channel_id={channel_id}")
    else:
        print(f"INFO: Successfully wrote PDU data for robot={robot_name}, channel_id={channel_id}")
