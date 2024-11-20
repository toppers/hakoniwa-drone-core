import time
from pymavlink import mavutil
from msg.message_queue import MessageQueue  # 先ほど作成したMessageQueueをインポート
from msg.mavlink_message import MavlinkMessage  # MavlinkMessageをインポート

class LogReplay:
    def __init__(self, log_filename, mavlink_connection, message_queue, replay=True):
        """
        LogReplayクラス
        :param log_filename: 再生するログファイル名
        :param mavlink_connection: pymavlink の接続オブジェクト
        :param message_queue: メッセージキューオブジェクト
        :param replay: タイムスタンプスリープを有効にするか
        """
        self.log_filename = log_filename
        self.mavlink_connection = mavlink_connection
        self.message_queue = message_queue
        self.replay = replay

    def replay_log(self):
        """
        ログを再生し、メッセージキューに追加する
        """
        print(f"Replaying log file: {self.log_filename}")
        try:
            with open(self.log_filename, "rb") as log_file:
                prev_timestamp = None

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

                        # メッセージをキューに追加
                        message = MavlinkMessage(
                            ip_addr="127.0.0.1",  # ログ再生では固定値
                            port=0,              # ログ再生ではポート番号は不要
                            msg_type=msg.get_type(),
                            msg_data=msg.to_dict(),
                        )
                        self.message_queue.enqueue(message)
        except FileNotFoundError:
            print(f"Log file {self.log_filename} not found.")
        except Exception as e:
            print(f"Error replaying log file: {e}")
