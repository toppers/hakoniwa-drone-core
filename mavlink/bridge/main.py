import argparse
import threading
import time
from msg.mavlink_message import MavlinkMessage
from msg.message_queue import MessageQueue
from log.log_replay import LogReplay
from comm.udp_receiver import UdpReceiver
from msg.pdu_message_convertor import PduMessageConvertor
#from hako.pdu_writer import PduWriter
from pymavlink import mavutil

from msg.conv.AHRS2_to_Twist import AHRS2ToTwistConvertor
from msg.conv.SERVO_OUTPUT_RAW_to_HakoHilActuatorControls import SERVO_OUTPUT_RAWToHakoHilActuatorControlsConvertor

def start_log_replay(log_filename, mavlink_connection, message_queue):
    """
    LogReplayのスレッドでの実行
    """
    log_replay = LogReplay(
        log_filename=log_filename,
        mavlink_connection=mavlink_connection,
        message_queue=message_queue,
        replay=True,  # タイムスタンプスリープを有効
    )
    log_replay.replay_log()

def start_udp_receiver(udp_ip, udp_port, mavlink_connection, message_queue):
    """
    UdpReceiverのスレッドでの実行
    """
    udp_receiver = UdpReceiver(
        udp_ip=udp_ip,
        udp_port=udp_port,
        mavlink_connection=mavlink_connection,
        message_queue=message_queue,
    )
    udp_receiver.start_receiving()

def parse_arguments():
    """
    コマンドライン引数を解析
    """
    parser = argparse.ArgumentParser(description="Run MAVLink processing in either log replay or UDP reception mode.")

    # 共通引数
    parser.add_argument("--mavlink-config", required=True, help="Path to the mavlink-custom.json configuration file.")
    parser.add_argument("--pdu-config", required=True, help="Path to the pdu-custom.json configuration file.")
    parser.add_argument("--comm-config", required=True, help="Path to the comm_config.json configuration file.")

    # サブコマンド
    subparsers = parser.add_subparsers(dest="mode", required=True)

    # Log replay mode
    log_parser = subparsers.add_parser("log", help="Replay a MAVLink log file.")
    log_parser.add_argument("log_file", type=str, help="Path to the MAVLink log file.")

    # UDP reception mode
    udp_parser = subparsers.add_parser("udp", help="Receive MAVLink messages over UDP.")
    udp_parser.add_argument("udp_address", type=str, help="IP and port to bind to, in the format <ip>:<port>.")

    return parser.parse_args()

def main():
    # 引数の解析
    args = parse_arguments()

    # PduMessageConvertorの作成
    convertor = PduMessageConvertor(args.mavlink_config, args.pdu_config, args.comm_config)

    # 共通設定
    message_queue = MessageQueue(max_size=100)
    message_queue.set_listened_types([
        MavlinkMessage.get_pdu_msg_type("AHRS2"), 
        MavlinkMessage.get_pdu_msg_type("SERVO_OUTPUT_RAW")]
        )  # リッスン対象を設定
    mavlink_connection = mavutil.mavlink.MAVLink(None)

    # スレッドの管理
    threads = []

    if args.mode == "log":
        log_thread = threading.Thread(
            target=start_log_replay,
            args=(args.log_file, mavlink_connection, message_queue)
        )
        threads.append(log_thread)
    elif args.mode == "udp":
        udp_ip, udp_port = args.udp_address.split(":")
        udp_thread = threading.Thread(
            target=start_udp_receiver,
            args=(udp_ip, int(udp_port), mavlink_connection, message_queue)
        )
        threads.append(udp_thread)

    # スレッドを開始
    for thread in threads:
        thread.start()

    ahrs2conv = AHRS2ToTwistConvertor(ref_lat=-353632621, ref_lng=1491652374, ref_alt=584.0899658203125)
    servo_conv = SERVO_OUTPUT_RAWToHakoHilActuatorControlsConvertor()

    # メインスレッドでキューを処理
    try:
        while True:
            if not message_queue.is_empty():
                mavlink_message = message_queue.dequeue()
                #print(f"Received message: {mavlink_message}")
                try:
                    # メッセージをPduMessageに変換
                    pdu_message = convertor.create_pdu(mavlink_message)
                    if pdu_message.msg_type == MavlinkMessage.get_pdu_msg_type("AHRS2"):
                        pdu_message = ahrs2conv.convert(pdu_message)
                        #print(f"Converted message: {pdu_message}")
                    elif pdu_message.msg_type == MavlinkMessage.get_pdu_msg_type("SERVO_OUTPUT_RAW"):
                        pdu_message = servo_conv.convert(pdu_message)
                        #print(f"Converted message: {pdu_message}")
                    pdu_message = convertor.compile_pdu(pdu_message)
                    print(f"Converted message: {pdu_message}")
                    # PDUに書き込み
                    # pdu_writer.write_pdu_message(pdu_message)
                except ValueError as e:
                    print(f"Conversion error: {e}")
            else:
                time.sleep(0.01)
    except KeyboardInterrupt:
        print("Terminating program...")
        for thread in threads:
            thread.join()

if __name__ == "__main__":
    main()
