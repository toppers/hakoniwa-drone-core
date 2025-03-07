import math
from msg.pdu_message import PduMessage

class AHRS2PrivatePosition:
    def __init__(self, ref_lat: int, ref_lng: int, ref_alt: float,is_fixed_altitude: bool, fixed_altitude: float):
        """
        AHRS2からTwistへのコンバータ
        :param ref_lat: 基準緯度 (度)
        :param ref_lng: 基準経度 (度)
        :param ref_alt: 基準高度 (メートル)
        """
        self.ref_lat = ref_lat
        self.ref_lng = ref_lng
        self.ref_alt = ref_alt
        self.is_fixed_altitude = is_fixed_altitude
        self.fixed_altitude = fixed_altitude
        print(f"ref_lat: {ref_lat}, ref_lng: {ref_lng}, ref_alt: {ref_alt}, is_fixed_altitude: {is_fixed_altitude}, fixed_altitude: {fixed_altitude}")

class AHRS2ToTwistConvertor:
    def __init__(self):
        self.map_for_initial_position = {}
        pass
    def addInitialPosition(self, robot_name:str, ref_lat: int, ref_lng: int, ref_alt: float, is_fixed_altitude: bool, fixed_altitude: float):
        """
        AHRS2からTwistへのコンバータ
        :param ref_lat: 基準緯度 (度)
        :param ref_lng: 基準経度 (度)
        :param ref_alt: 基準高度 (メートル)
        """
        self.map_for_initial_position[robot_name] = AHRS2PrivatePosition(ref_lat, ref_lng, ref_alt, is_fixed_altitude, fixed_altitude)

    def _calculate_relative_position(self, robot_name, lat, lng, altitude):
        """
        緯度経度高度を基準点からの相対位置に変換
        :param lat: 緯度 (度 * 1E7)
        :param lng: 経度 (度 * 1E7)
        :param altitude: 高度 (メートル)
        :return: x, y, z (メートル単位での相対位置)
        """
        # 緯度経度のスケール変換 (基準値も同じスケールで扱う)
        #print(f"lat: {lat}, lng: {lng}")
        lat = lat / 1E7
        lng = lng / 1E7
        ref_lat = self.map_for_initial_position[robot_name].ref_lat / 1E7
        ref_lng = self.map_for_initial_position[robot_name].ref_lng / 1E7

        # デバッグ出力
        #print(f"lat: {lat}, lng: {lng}, altitude: {altitude}")
        #print(f"ref_lat: {ref_lat}, ref_lng: {ref_lng}")
        #print(f"delta_lat: {lat - ref_lat}, delta_lng: {lng - ref_lng}")

        # 地球の半径（平均半径）: メートル
        earth_radius = 6378137.0

        # 緯度と経度の差分 (ラジアン)
        delta_lat = math.radians(lat - ref_lat)
        delta_lng = math.radians(lng - ref_lng)
        mean_lat = math.radians((lat + ref_lat) / 2.0)

        # メートル単位での相対位置
        x = earth_radius * delta_lat                      # 緯度方向
        y = -earth_radius * delta_lng * math.cos(mean_lat)  # 経度方向
        if self.map_for_initial_position[robot_name].is_fixed_altitude:
            z = self.map_for_initial_position[robot_name].fixed_altitude
            #print(f"Fixed Altitude: {z}")
        else:
            z = altitude - self.map_for_initial_position[robot_name].ref_alt  # 高度方向

        # デバッグ出力
        #print(f"Relative Position: x={x}, y={y}, z={z}")
        return x, y, z



    def convert(self, pdu_message: PduMessage) -> PduMessage:
        """
        AHRS2をTwistに変換
        :param pdu_message: AHRS2データを含むPduMessage
        :return: Twistデータを含むPduMessage
        """
        if pdu_message.data is None:
            raise ValueError("PduMessage data is empty")

        # AHRS2データの取得
        roll = pdu_message.data.get("roll")
        pitch = pdu_message.data.get("pitch")
        yaw = pdu_message.data.get("yaw")
        #print(f"roll: {roll}, pitch: {pitch}, yaw: {yaw}")
        altitude = pdu_message.data.get("altitude")
        lat = pdu_message.data.get("lat")
        lng = pdu_message.data.get("lng")
        #print(f"lat: {lat}, lng: {lng}, altitude: {altitude}")
        if None in (roll, pitch, yaw, altitude, lat, lng):
            raise ValueError("Missing required AHRS2 fields")

        # 相対位置を計算
        x, y, z = self._calculate_relative_position(pdu_message.robot_name, lat, lng, altitude)
        #print(f"x: {x}, y: {y}, z: {z}")

        # MAVLink座標系からROS座標系への変換
        ros_roll = roll
        ros_pitch = -pitch  # ROSではピッチの符号が反転
        ros_yaw = -yaw      # ROSではヨーの符号が反転

        # 変換したTwistデータを構築
        twist_data = {
            "linear": {"x": x, "y": y, "z": z},  # 相対位置をlinearに設定
            "angular": {"x": ros_roll, "y": ros_pitch, "z": ros_yaw},
        }

        # 新しいPduMessageとしてTwistを返す
        return PduMessage(
            robot_name=pdu_message.robot_name,
            msg_type="geometry_msgs/Twist",
            data=twist_data,
        )
