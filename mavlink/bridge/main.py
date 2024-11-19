import argparse
import threading
import time
from msg.message_queue import MessageQueue
from log.log_replay import LogReplay
from comm.udp_receiver import UdpReceiver
from pymavlink import mavutil

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

    # 共通設定
    message_queue = MessageQueue(max_size=100)
    message_queue.set_listened_types(["GLOBAL_POSITION_INT", "AHRS2", "ATTITUDE"])  # リッスン対象を設定
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

    # メインスレッドでキューを処理
    try:
        while True:
            if not message_queue.is_empty():
                message = message_queue.dequeue()
                print(f"Processed message: {message}")
            else:
                time.sleep(1)
    except KeyboardInterrupt:
        print("Terminating program...")
        for thread in threads:
            thread.join()

if __name__ == "__main__":
    main()
