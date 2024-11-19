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

def vehicle_position_callback(msg_type, dict_data):
    if msg_type == "AHRS2":
        print(f"Drone position: lat={dict_data['lat']}, lng={dict_data['lng']}, alt={dict_data['altitude']}")
        print(f"Drone attitude: roll={dict_data['roll']}, pitch={dict_data['pitch']}, yaw={dict_data['yaw']}")

def vehicle_servo_callback(msg_type, dict_data):
    if msg_type == "SERVO_OUTPUT_RAW":
        print(f"Servo output: servo1={dict_data['servo1_raw']}, servo2={dict_data['servo2_raw']}")

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
                #print(f"Received message from {addr}: {msg.get_type()} {msg.to_dict()}")
                vehicle_position_callback(msg.get_type(), msg.to_dict())
                vehicle_servo_callback(msg.get_type(), msg.to_dict())
    except Exception as e:
        print(f"Error decoding MAVLink message: {e}")
