import socket
from pymavlink import mavutil

# UDPのホストとポートを設定
UDP_IP = "0.0.0.0"  # 全てのインターフェースで受信する
UDP_PORT = 54001    # ミッションプランナーで設定したポート番号

# ソケットを作成してバインド
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Listening for UDP packets on port {UDP_PORT}...")

# MAVLink接続オブジェクトを作成
mavlink_connection = mavutil.mavlink.MAVLink(None)

# 無限ループでデータを受信して処理
while True:
    # データを受信（バッファサイズ1024バイト）
    data, addr = sock.recvfrom(1024)

    # MAVLinkのメッセージを解析
    try:
        # データをバイトごとに処理
        for byte in data:
            # `bytes([byte])` でintを1バイトのbytesに変換
            msg = mavlink_connection.parse_char(bytes([byte]))
            if msg:
                print(f"Received message from {addr}: {msg.get_type()} {msg.to_dict()}")
    except Exception as e:
        print(f"Error decoding MAVLink message: {e}")
