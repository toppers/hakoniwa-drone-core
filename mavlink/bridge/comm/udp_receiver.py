import socket
from msg.message_queue import MessageQueue
from msg.mavlink_message import MavlinkMessage
from pymavlink import mavutil


class UdpReceiver:
    def __init__(self, udp_ip, udp_port, mavlink_connection, message_queue):
        """
        UdpReceiverクラス
        :param udp_ip: バインドするIPアドレス
        :param udp_port: バインドするポート番号
        :param mavlink_connection: pymavlink の接続オブジェクト
        :param message_queue: メッセージキューオブジェクト
        """
        self.udp_ip = udp_ip
        self.udp_port = udp_port
        self.sock = None
        self.mavlink_connection = mavlink_connection
        self.message_queue = message_queue

    def start_receiving(self):
        """
        UDPパケットを受信し、メッセージキューに追加
        """
        # ソケットを作成してバインド
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.udp_ip, self.udp_port))
        print(f"Listening for UDP packets on {self.udp_ip}:{self.udp_port}...")

        try:
            while True:
                data, addr = self.sock.recvfrom(1024)  # UDPパケットを受信
                ip_addr, port = addr
                #print(f"Received {len(data)} bytes from {ip_addr}:{port}")
                # MAVLinkメッセージを解析
                for byte in data:
                    msg = self.mavlink_connection.parse_char(bytes([byte]))
                    if msg:
                        # メッセージをキューに追加
                        message = MavlinkMessage(
                            ip_addr=ip_addr,
                            port=self.udp_port,
                            msg_type=msg.get_type(),
                            msg_data=msg.to_dict(),
                        )
                        self.message_queue.enqueue(message)

        except Exception as e:
            print(f"Error receiving UDP packets: {e}")
        finally:
            self.sock.close()
            print("UDP receiver stopped.")
