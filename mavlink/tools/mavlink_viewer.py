import socket
import sys
import time
from pymavlink import mavutil


class MavlinkHandler:
    def __init__(self, log_filename="mavlink-log.bin", udp_ip="0.0.0.0", udp_port=54001, replay=False):
        self.log_filename = log_filename
        self.udp_ip = udp_ip
        self.udp_port = udp_port
        self.sock = None
        self.mavlink_connection = mavutil.mavlink.MAVLink(None)
        self.replay = replay  # ログリプレイ時のタイムスタンプスリープ機能

    def vehicle_position_callback(self, msg_type, dict_data):
        if msg_type == "AHRS2":
            print(f"Drone position: lat={dict_data['lat']}, lng={dict_data['lng']}, alt={dict_data['altitude']}")
            print(f"Drone attitude: roll={dict_data['roll']}, pitch={dict_data['pitch']}, yaw={dict_data['yaw']}")

    def vehicle_servo_callback(self, msg_type, dict_data):
        if msg_type == "SERVO_OUTPUT_RAW":
            print(f"Servo output: servo1={dict_data['servo1_raw']}, servo2={dict_data['servo2_raw']}")

    def save_binary_data(self, data, mode="ab"):
        """バイナリデータをログファイルに保存"""
        with open(self.log_filename, mode) as log_file:
            log_file.write(data)

    def parse_log_file(self):
        """ログファイルを解析"""
        print(f"Parsing log file: {self.log_filename}")
        try:
            with open(self.log_filename, "rb") as log_file:
                prev_timestamp = None  # 前回のタイムスタンプを保存
                while byte := log_file.read(1):  # 1バイトずつ読み取る
                    msg = self.mavlink_connection.parse_char(byte)
                    if msg:
                        # タイムスタンプ処理
                        if self.replay and hasattr(msg, 'time_usec'):
                            current_timestamp = msg.time_usec / 1e6  # マイクロ秒から秒に変換
                            if prev_timestamp is not None:
                                sleep_time = current_timestamp - prev_timestamp
                                if sleep_time > 0:
                                    time.sleep(sleep_time)
                            prev_timestamp = current_timestamp
                        # メッセージ処理
                        self.vehicle_position_callback(msg.get_type(), msg.to_dict())
                        self.vehicle_servo_callback(msg.get_type(), msg.to_dict())
        except FileNotFoundError:
            print(f"Log file {self.log_filename} not found.")
        except Exception as e:
            print(f"Error parsing log file: {e}")

    def receive_udp(self):
        """UDPパケットを受信して処理"""
        # ソケットを作成してバインド
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.udp_ip, self.udp_port))
        print(f"Listening for UDP packets on port {self.udp_port}...")

        # ログファイルを初期化（ロギングモードの場合）
        self.save_binary_data(b"", mode="wb")

        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                # ログに保存
                self.save_binary_data(data)
                # MAVLinkメッセージを解析
                for byte in data:
                    msg = self.mavlink_connection.parse_char(bytes([byte]))
                    if msg:
                        self.vehicle_position_callback(msg.get_type(), msg.to_dict())
                        self.vehicle_servo_callback(msg.get_type(), msg.to_dict())
            except Exception as e:
                print(f"Error decoding MAVLink message: {e}")


def print_usage():
    """Usageを表示"""
    usage = """
Usage:
    python script_name.py                Start in UDP logging mode and save data to mavlink-log.bin.
    python script_name.py <log_file>    Parse and display messages from an existing binary log file.
    python script_name.py <log_file> --replay
                                        Replay log file with timing based on message timestamps.
Options:
    --help                              Display this help message.
"""
    print(usage)


def main():
    # 引数によるモード判定
    if len(sys.argv) > 1:
        if sys.argv[1] in ["--help", "-h"]:
            print_usage()
        else:
            # ログファイル解析モード
            log_filename = sys.argv[1]
            replay_mode = "--replay" in sys.argv
            handler = MavlinkHandler(log_filename=log_filename, replay=replay_mode)
            handler.parse_log_file()
    else:
        # UDPロギングモード
        handler = MavlinkHandler()
        handler.receive_udp()


if __name__ == "__main__":
    main()
