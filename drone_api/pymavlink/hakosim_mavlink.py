#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAVLink版 MultirotorClient
箱庭のPDU通信をpymavlinkのMAVLink通信に置き換えた実装
"""

from asyncio import timeout
from pymavlink import mavutil
import time
import math
import threading
import queue
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Tuple, Callable
from enum import Enum

class ImageType:
    Scene = "png"

@dataclass
class Vector3r:
    x: float = 0.0
    y: float = 0.0 
    z: float = 0.0

@dataclass
class Quaternionr:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    w: float = 1.0
    
    @staticmethod
    def euler_to_quaternion(roll, pitch, yaw):
        """オイラー角からクォータニオンに変換"""
        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)
        cp = math.cos(pitch * 0.5)
        sp = math.sin(pitch * 0.5)
        cr = math.cos(roll * 0.5)
        sr = math.sin(roll * 0.5)
        
        return Quaternionr(
            x=sr * cp * cy - cr * sp * sy,
            y=cr * sp * cy + sr * cp * sy,
            z=cr * cp * sy - sr * sp * cy,
            w=cr * cp * cy + sr * sp * sy
        )
    
    @staticmethod
    def quaternion_to_euler(q):
        """クォータニオンからオイラー角に変換"""
        # Roll (x軸回転)
        sinr_cosp = 2 * (q.w * q.x + q.y * q.z)
        cosr_cosp = 1 - 2 * (q.x * q.x + q.y * q.y)
        roll = math.atan2(sinr_cosp, cosr_cosp)
        
        # Pitch (y軸回転)
        sinp = 2 * (q.w * q.y - q.z * q.x)
        if abs(sinp) >= 1:
            pitch = math.copysign(math.pi / 2, sinp)
        else:
            pitch = math.asin(sinp)
        
        # Yaw (z軸回転)  
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        yaw = math.atan2(siny_cosp, cosy_cosp)
        
        return roll, pitch, yaw

@dataclass
class Pose:
    position: Vector3r
    orientation: Quaternionr

@dataclass 
class GameControllerOperation:
    """ゲームコントローラー操作データ"""
    axis: List[float] = None
    button: List[bool] = None
    
    def __post_init__(self):
        if self.axis is None:
            self.axis = [0.0] * 8
        if self.button is None:
            self.button = [False] * 16

@dataclass
class LidarData:
    """LIDARデータ"""
    point_cloud: List[Vector3r]
    time_stamp: float
    pose: Pose

class FrameConverter:
    @staticmethod
    def ros_to_ned_pos(ros_pos: Vector3r) -> Vector3r:
        """ROS(FLU)座標系の位置をNED座標系に変換"""
        return Vector3r(
            x=ros_pos.x,
            y=-ros_pos.y,
            z=-ros_pos.z
        )

    @staticmethod
    def ned_to_ros_pos(ned_pos: Vector3r) -> Vector3r:
        """NED座標系の位置をROS(FLU)座標系に変換"""
        return Vector3r(
            x=ned_pos.x,
            y=-ned_pos.y,
            z=-ned_pos.z
        )

    @staticmethod
    def ned_to_ros_orient(ned_q: Quaternionr) -> Quaternionr:
        """NED座標系のクォータニオンをROS(FLU)座標系に変換"""
        # NEDからFLUへの変換は、ロール軸周りに180度回転
        roll_180 = Quaternionr.euler_to_quaternion(math.pi, 0, 0)
        
        # クォータニオンの積で回転を合成 (q_ros = q_ned * q_rot)
        return Quaternionr(
            w = ned_q.w * roll_180.w - ned_q.x * roll_180.x - ned_q.y * roll_180.y - ned_q.z * roll_180.z,
            x = ned_q.w * roll_180.x + ned_q.x * roll_180.w + ned_q.y * roll_180.z - ned_q.z * roll_180.y,
            y = ned_q.w * roll_180.y - ned_q.x * roll_180.z + ned_q.y * roll_180.w + ned_q.z * roll_180.x,
            z = ned_q.w * roll_180.z + ned_q.x * roll_180.y - ned_q.y * roll_180.x + ned_q.z * roll_180.w
        )

    @staticmethod
    def ros_to_ned_yaw(ros_yaw_deg: float) -> float:
        """ROS座標系のヨー角をNED座標系に変換"""
        return -ros_yaw_deg


class MavlinkDrone:
    def __init__(self, name: str, connection_string: str):
        self.name = name
        self.connection_string = connection_string
        self.mavlink_connection = None
        self.enableApiControl = False
        self.arm = False
        self.target_system = 1
        self.target_component = 1
        self._message_queue = queue.Queue()
        self._running = False
        self._reader_thread = None

    def _param_id_to_str(self, pid):
        if isinstance(pid, (bytes, bytearray)):
            pid = pid.decode("utf-8", errors="ignore")
        return pid.strip("\x00")

    def _wait_for_message(self, msg_type: str, condition: Callable[[Any], bool], timeout: float) -> Optional[Any]:
        """指定されたタイプのメッセージを条件を満たすまで待機する汎用ヘルパー"""
        t0 = time.time()
        while time.time() - t0 < timeout:
            msg = self.mavlink_connection.recv_match(type=msg_type, blocking=True, timeout=1)
            if msg and condition(msg):
                return msg
        return None

    def set_param(self, name: str, value, ptype=mavutil.mavlink.MAV_PARAM_TYPE_INT32, timeout=3):
        """PARAM_SET → 同名のPARAM_VALUEエコー確認まで"""
        self.mavlink_connection.mav.param_set_send(
            self.target_system, self.target_component,
            name.encode("utf-8"), float(value), ptype
        )
        msg = self._wait_for_message(
            "PARAM_VALUE", 
            lambda m: self._param_id_to_str(m.param_id) == name, 
            timeout
        )
        if msg:
            print(f"{name} = {msg.param_value} (type={msg.param_type})")
            return True
        else:
            print(f"⚠ PARAM echo timeout: {name}")
            return False

    def wait_gps_fix(self, min_fix=3, min_sats=6, timeout=30):
        print("Waiting for GPS fix...")
        condition = lambda g: g.fix_type >= min_fix and g.satellites_visible >= min_sats
        
        # 初期メッセージ表示用
        initial_msg = self.mavlink_connection.recv_match(type="GPS_RAW_INT", blocking=True, timeout=1)
        if initial_msg:
            print(f"GPS status: fix={initial_msg.fix_type}, sats={initial_msg.satellites_visible}")
            if condition(initial_msg):
                print(f"GPS OK: fix={initial_msg.fix_type}, sats={initial_msg.satellites_visible}")
                return True

        g = self._wait_for_message("GPS_RAW_INT", condition, timeout - 1)
        if g:
            print(f"GPS OK: fix={g.fix_type}, sats={g.satellites_visible}")
            return True
        return False
    
    def wait_origin(self, timeout=30):
        """Origin確定待ち"""
        print("Waiting for HOME/Origin to be set...")
        t0 = time.time()
        last_req = 0.0
        while time.time() - t0 < timeout:
            # 数秒おきにHOME要求を送って促す
            if time.time() - last_req > 3.0:
                self.mavlink_connection.mav.command_long_send(
                    self.target_system, self.target_component,
                    mavutil.mavlink.MAV_CMD_GET_HOME_POSITION, 0,
                    0,0,0,0,0,0,0
                )
                last_req = time.time()

            msg = self.mavlink_connection.recv_match(type=["HOME_POSITION", "GPS_GLOBAL_ORIGIN", "STATUSTEXT"], blocking=True, timeout=1)
            if not msg:
                continue
            
            t = msg.get_type()
            if t == "HOME_POSITION":
                print("Origin: HOME_POSITION received")
                return True
            if t == "GPS_GLOBAL_ORIGIN":
                print("Origin: GPS_GLOBAL_ORIGIN received")
                return True
            if t == "STATUSTEXT":
                txt = getattr(msg, "text", "") or ""
                print(f"STATUSTEXT: {txt}")
                if "origin set" in txt.lower():
                    print(f"Origin via STATUSTEXT: {txt}")
                    return True
        return False

    def mode_mapping_value(self, mode_name: str) -> int | None:
        mapping = self.mavlink_connection.mode_mapping() or {}
        return mapping.get(mode_name)

    def wait_mode(self, target_mode: str, timeout=10):
        want = self.mode_mapping_value(target_mode)
        if want is None:
            print(f"Unknown mode: {target_mode}")
            return False
        
        print(f"Waiting for mode {target_mode} (value={want})...")
        condition = lambda hb: hb.custom_mode == want
        
        # 初期メッセージ表示用
        initial_hb = self.mavlink_connection.recv_match(type="HEARTBEAT", blocking=True, timeout=1)
        if initial_hb:
            print(f"Current mode: {initial_hb.custom_mode} (want: {want})")
            if condition(initial_hb):
                return True

        hb = self._wait_for_message("HEARTBEAT", condition, timeout - 1)
        return hb is not None

    def is_armed(self, timeout=2):
        hb = self._wait_for_message("HEARTBEAT", lambda m: True, timeout)
        if hb:
            armed = bool(hb.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
            print(f"Armed status: {armed} (base_mode={hb.base_mode})")
            return armed
        return False

    def pump_status_text(self, duration=2.0, non_block_time=0.1):
        t0 = time.time()
        while time.time() - t0 < duration:
            st = self.mavlink_connection.recv_match(type="STATUSTEXT", blocking=False)
            if st:
                print(f"[STATUSTEXT] sev={st.severity} text={getattr(st, 'text', '')}")
            time.sleep(non_block_time)

    def get_arming_check_status(self):
        """現在のarming checkの状態を確認"""
        print("Checking current arming status...")
        
        # SYS_STATUSメッセージで詳細な状態を確認
        sys_status = self.mavlink_connection.recv_match(type="SYS_STATUS", blocking=True, timeout=3)
        if sys_status:
            print(f"SYS_STATUS: onboard_control_sensors_health={sys_status.onboard_control_sensors_health}")
        
        # EKF_STATUS_REPORTでEKFの状態を確認
        ekf = self.mavlink_connection.recv_match(type="EKF_STATUS_REPORT", blocking=True, timeout=3)
        if ekf:
            print(f"EKF flags: {ekf.flags}")
        
        # VIBRATIONでバイブレーション状態確認
        vib = self.mavlink_connection.recv_match(type="VIBRATION", blocking=True, timeout=3)
        if vib:
            print(f"Vibration: X={vib.vibration_x}, Y={vib.vibration_y}, Z={vib.vibration_z}")


    def connect(self):
        """MAVLink接続を確立"""
        try:
            self.mavlink_connection = mavutil.mavlink_connection(
                self.connection_string,
                source_system=255,
                source_component=190
            )
            self.mavlink_connection.wait_heartbeat()
            self.target_system = self.mavlink_connection.target_system
            self.target_component = self.mavlink_connection.target_component
            print(f"HB from sys {self.target_system} comp {self.target_component}")


            print(f"Connected to {self.name}: sys={self.target_system}, comp={self.target_component}")


            # ===== 1) SITL向け: より積極的なセーフティ緩和 =====
            print("=== Setting Parameters ===")
            # ARMING_CHECKを完全に無効化
            self.set_param("ARMING_CHECK", 0, mavutil.mavlink.MAV_PARAM_TYPE_INT32)

            # その他のSITL用パラメータ
            self.set_param("SIM_SPEEDUP", 1, mavutil.mavlink.MAV_PARAM_TYPE_REAL32)
            self.set_param("SCHED_LOOP_RATE", 50, mavutil.mavlink.MAV_PARAM_TYPE_INT32)  # 180は高すぎかも

            # GPSとEKF関連の緩和
            self.set_param("GPS_TYPE", 1, mavutil.mavlink.MAV_PARAM_TYPE_INT8)
            self.set_param("EK2_ENABLE", 0, mavutil.mavlink.MAV_PARAM_TYPE_INT8)  # EKF2無効
            self.set_param("EK3_ENABLE", 1, mavutil.mavlink.MAV_PARAM_TYPE_INT8)  # EKF3有効
            self.set_param("AHRS_EKF_TYPE", 3, mavutil.mavlink.MAV_PARAM_TYPE_INT8)  # EKF3使用

            # バッテリー関連の緩和（SITL用）
            self.set_param("BATT_MONITOR", 4, mavutil.mavlink.MAV_PARAM_TYPE_INT8)  # シミュレーション
            self.set_param("FS_BATT_ENABLE", 0, mavutil.mavlink.MAV_PARAM_TYPE_INT8)  # バッテリーフェールセーフ無効

            # ===== 2) 再起動なしで進める（まず試す） =====
            print("=== Skipping reboot for now ===")
            time.sleep(2.0)  # パラメータ反映待ち
            return True
            
        except Exception as e:
            print(f"Failed to connect to {self.name}: {e}")
            return False
    
    def disconnect(self):
        """接続を切断"""
        self._running = False
        if self._reader_thread:
            self._reader_thread.join(timeout=1.0)
        if self.mavlink_connection:
            self.mavlink_connection.close()
    
    def _message_reader(self):
        """バックグラウンドでメッセージを受信"""
        while self._running:
            try:
                msg = self.mavlink_connection.recv_match(blocking=True, timeout=0.1)
                if msg:
                    self._message_queue.put(msg)
            except Exception as e:
                if self._running:
                    print(f"Message reader error for {self.name}: {e}")
                break

    def set_mode(self, mode: str) -> bool:
        """飛行モードを設定"""
        try:
            self.mavlink_connection.set_mode_apm(mode)
            print(f"Set mode {mode} for {self.name}")
            return True
        except Exception as e:
            print(f"Failed to set mode {mode} for {self.name}: {e}")
            return False

    def wait_for_command_ack(self, command: int, timeout: float = 5.0) -> 'mavutil.mavlink.MAVLink_command_ack_message | None':
        """特定のコマンドに対するCOMMAND_ACKを待機する"""
        ack = self._wait_for_message(
            msg_type='COMMAND_ACK',
            condition=lambda msg: getattr(msg, 'command', None) == command,
            timeout=timeout
        )
        if ack:
            print(f"ACK received: command={ack.command}, result={ack.result}")
        else:
            print(f"ACK timeout for command {command}")
        return ack

    def get_vehicle_pose(self) -> Optional[Pose]:
        """車両の姿勢を取得"""
        if not self.mavlink_connection:
            return None
        
        try:
            # ATTITUDE メッセージを取得
            msg = self.mavlink_connection.recv_match(type='ATTITUDE', blocking=True, timeout=1.0)
            if not msg:
                return None
            
            # LOCAL_POSITION_NED メッセージを取得  
            pos_msg = self.mavlink_connection.recv_match(type='LOCAL_POSITION_NED', blocking=True, timeout=1.0)
            if not pos_msg:
                return None
            
            # 位置情報
            position = Vector3r(pos_msg.x, pos_msg.y, pos_msg.z)
            
            # 姿勢情報（オイラー角からクォータニオンに変換）
            orientation = Quaternionr.euler_to_quaternion(msg.roll, msg.pitch, msg.yaw)
            
            return Pose(position, orientation)
            
        except Exception as e:
            print(f"Failed to get pose for {self.name}: {e}")
            return None

    def takeoff(self, height: float) -> bool:
        """離陸コマンドを送信"""
        if not self.mavlink_connection:
            return False
        try:
            self.mavlink_connection.mav.command_long_send(
                self.target_system, self.target_component,
                mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
                0, 0, 0, 0, 0, 0, 0, float(height)
            )
            print("takeoff request sent")
            ack = self.wait_for_command_ack(mavutil.mavlink.MAV_CMD_NAV_TAKEOFF)
            if ack and ack.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
                print("DONE")
                return True
            else:
                print("Takeoff command not acknowledged")
                return False
        except Exception as e:
            print(f"Takeoff failed for {self.name}: {e}")
            return False

    def land(self) -> bool:
        """着陸コマンドを送信"""
        if not self.mavlink_connection:
            return False
        try:
            self.mavlink_connection.mav.command_long_send(
                self.target_system, self.target_component,
                mavutil.mavlink.MAV_CMD_NAV_LAND,
                0, 0, 0, 0, 0, 0, 0, 0
            )
            print("land request sent")
            ack = self.wait_for_command_ack(mavutil.mavlink.MAV_CMD_NAV_LAND)
            if ack and ack.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
                print("DONE")
                return True
            else:
                print("Land command not acknowledged")
                return False
        except Exception as e:
            print(f"Land failed for {self.name}: {e}")
            return False

    def move_to_position(self, x: float, y: float, z: float, yaw_deg: float) -> bool:
        """位置移動コマンドを送信"""
        if not self.mavlink_connection:
            return False
        try:
            self.mavlink_connection.mav.set_position_target_local_ned_send(
                0,  # time_boot_ms
                self.target_system, self.target_component,
                mavutil.mavlink.MAV_FRAME_LOCAL_NED,
                0b0000111111111000,  # type_mask (position enabled)
                x, y, z,  # position
                0, 0, 0,  # velocity
                0, 0, 0,  # acceleration  
                math.radians(yaw_deg), 0  # yaw, yaw_rate
            )
            print("move request sent")
            return True
        except Exception as e:
            print(f"Move failed for {self.name}: {e}")
            return False

    def set_home_manually(self):
        """手動でHOMEを設定してみる"""
        if not self.mavlink_connection:
            return
        print("Trying to set HOME manually...")
        self.mavlink_connection.mav.command_long_send(
            self.target_system, self.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_HOME, 0,
            1,  # use current location
            0,0,0,0,0,0
        )
        time.sleep(2.0)

    def arm_and_verify(self):
        """複数の方法でARMを試行し、成功したか確認する"""
        if not self.mavlink_connection:
            return False
        
        if self.is_armed():
            print("✓ Already armed")
            return True

        print("=== Attempting to ARM ===")
        
        # 方法1: 基本的なARM
        print("ARM attempt 1: Basic ARM")
        self.mavlink_connection.mav.command_long_send(
            self.target_system, self.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0, 1, 0, 0,0,0,0,0
        )
        ack = self.wait_for_command_ack(mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, timeout=5)
        if ack and ack.result != mavutil.mavlink.MAV_RESULT_ACCEPTED:
            print("ARM rejected, checking status...")
            self.pump_status_text(3.0)
        time.sleep(2.0)
        if self.is_armed():
            print("✓ Successfully ARMED!")
            return True

        # 方法2: 強制ARM (param2=21196)
        print("ARM attempt 2: Force ARM with magic number")
        self.mavlink_connection.mav.command_long_send(
            self.target_system, self.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0, 1, 21196, 0,0,0,0,0
        )
        ack = self.wait_for_command_ack(mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, timeout=5)
        if ack:
            print(f"Force ARM ACK: result={ack.result}")
        time.sleep(2.0)
        if self.is_armed():
            print("✓ Successfully ARMED!")
            return True

        # 方法3: MAVLINKメッセージでのARM
        print("ARM attempt 3: SET_MODE with armed flag")
        mode_val = self.mode_mapping_value("GUIDED") or 4
        self.mavlink_connection.mav.set_mode_send(
            self.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED | mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED,
            mode_val
        )
        time.sleep(2.0)

        # 最終確認
        if self.is_armed(timeout=5):
            print("✓ Successfully ARMED!")
            return True
        else:
            print("✗ ARM failed - checking final status...")
            self.pump_status_text(5.0)
            self.check_arming_parameters()
            return False

    def check_arming_parameters(self):
        """Arming checkに関連するパラメータを確認"""
        if not self.mavlink_connection:
            return
        print("Requesting parameter list...")
        self.mavlink_connection.mav.param_request_list_send(self.target_system, self.target_component)
        time.sleep(2.0)
        
        # いくつかの重要なパラメータを確認
        for param in ["ARMING_CHECK", "GPS_TYPE", "EK3_ENABLE"]:
            self.mavlink_connection.mav.param_request_read_send(
                self.target_system, self.target_component,
                param.encode("utf-8"), -1
            )
            time.sleep(0.5)
        self.pump_status_text(3.0)

    def disarm(self) -> bool:
        """DISARMコマンドを送信"""
        if not self.mavlink_connection:
            return False
        print("=== Attempting to DISARM ===")
        self.mavlink_connection.mav.command_long_send(
            self.target_system, self.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0, 0, 0, 0,0,0,0,0
        )
        ack = self.wait_for_command_ack(mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, timeout=5)
        if ack and ack.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
            self.arm = False
            print("✓ Successfully DISARMED")
            return True
        print("✗ DISARM failed")
        return False

class MultirotorClient:
    def __init__(self, config_path: str = None, default_drone_name: str = None):
        """
        MAVLink版MultirotorClient初期化
        
        Args:
            config_path: 使用しない（互換性のため残す）
            default_drone_name: デフォルトドローン名
        """
        self.vehicles: Dict[str, MavlinkDrone] = {}
        self.default_drone_name = default_drone_name
        self._connected = False
        self.converter = FrameConverter()
        
        # デフォルト設定
        if default_drone_name is None:
            self.default_drone_name = "drone1"
    
    def add_vehicle(self, name: str, connection_string: str):
        """車両を追加"""
        self.vehicles[name] = MavlinkDrone(name, connection_string)
        if self.default_drone_name is None:
            self.default_drone_name = name
        print(f"Added vehicle: {name} with connection: {connection_string}")
    
    def confirmConnection(self) -> bool:
        """全車両への接続を確認・確立"""
        if not self.vehicles:
            print("No vehicles configured. Use add_vehicle() first.")
            return False
            
        success = True
        for vehicle in self.vehicles.values():
            if not vehicle.connect():
                success = False
            vehicle.get_arming_check_status()
            vehicle.pump_status_text(3.0)

        self._connected = success


        return success
    
    def disconnect_all(self):
        """全車両の接続を切断"""
        for vehicle in self.vehicles.values():
            vehicle.disconnect()
        self._connected = False
    
    def run_nowait(self):
        """非同期実行（互換性のため）"""
        # MAVLink版では特に処理しない
        pass
    
    def sleep(self, seconds: float) -> bool:
        """指定時間待機"""
        if seconds > 0:
            time.sleep(seconds)
            return True
        else:
            print("ERROR: sleep seconds must be greater than 0")
            return False
    
    def get_vehicle_name(self, vehicle_name: Optional[str]) -> Optional[str]:
        """車両名を取得（デフォルト車両の処理含む）"""
        if vehicle_name is None:
            return self.default_drone_name
        if vehicle_name in self.vehicles:
            return vehicle_name
        else:
            print(f"Vehicle '{vehicle_name}' not found.")
            return None
    
    def _get_vehicle(self, vehicle_name: Optional[str]) -> Optional[MavlinkDrone]:
        """車両オブジェクトを取得"""
        name = self.get_vehicle_name(vehicle_name)
        return self.vehicles.get(name) if name else None
    
    def enableApiControl(self, enable: bool, vehicle_name: Optional[str] = None):
        """API制御を有効化"""
        vehicle = self._get_vehicle(vehicle_name)
        if vehicle:
            vehicle.enableApiControl = enable
            # GUIDEDモードに設定
            if enable:
                vehicle.set_mode("GUIDED")
    
    def armDisarm(self, arm: bool, vehicle_name: Optional[str] = None):
        """ARM/DISARM"""
        vehicle = self._get_vehicle(vehicle_name)
        if not vehicle:
            return False

        if not arm:
            return vehicle.disarm()

        try:
            # ===== 3) GPS fix / Origin 待ち =====
            if not vehicle.wait_gps_fix(min_fix=2, min_sats=4, timeout=45):  # 条件緩和
                print("⚠ GPS not ready, but continuing...")

            if not vehicle.wait_origin(timeout=30):
                print("⚠ Origin not confirmed, but continuing...")
                vehicle.set_home_manually()

            # ===== 4) まずSTABILIZEモードにしてからGUIDEDへ =====
            print("=== Setting Mode to STABILIZE first ===")
            vehicle.set_mode("STABILIZE")
            time.sleep(2.0)

            print("=== Setting Mode to GUIDED ===")
            vehicle.set_mode("GUIDED")
            if not vehicle.wait_mode("GUIDED", timeout=8):
                print("⚠ Failed to enter GUIDED, trying LOITER...")
                vehicle.set_mode("LOITER")
                if not vehicle.wait_mode("LOITER", timeout=8):
                    print("⚠ Failed to enter LOITER, continuing anyway...")

            # ===== 5) ARM前の最終チェック =====
            print("=== Pre-ARM Status Check ===")
            vehicle.get_arming_check_status()
            vehicle.pump_status_text(2.0)

            # ===== 6) ARM試行 =====
            if vehicle.arm_and_verify():
                vehicle.arm = True
                return True
            else:
                return False
            
        except Exception as e:
            print(f"Failed to arm {vehicle.name}: {e}")
            return False
    
    def takeoff(self, height: float, vehicle_name: Optional[str] = None, timeout_sec: float = -1) -> bool:
        """離陸して指定高度に到達するまで待機"""
        vehicle = self._get_vehicle(vehicle_name)
        if not vehicle:
            return False
        
        try:
            print(f"INFO: takeoff: height={height}")
            
            # ARM確認
            if not vehicle.arm:
                if not self.armDisarm(True, vehicle_name):
                    print("Failed to arm before takeoff")
                    return False
                time.sleep(2.0)
            
            # GUIDED モードに設定
            vehicle.set_mode("GUIDED")
            time.sleep(1.0)
            
            if not vehicle.takeoff(height):
                return False

            # 高度到達待機
            if timeout_sec > 0:
                print(f"Waiting to reach altitude of {height}m...")
                start_time = time.time()
                while time.time() - start_time < timeout_sec:
                    current_pose = self.simGetVehiclePose(vehicle_name)
                    if current_pose:
                        current_altitude = current_pose.position.z
                        print(f"Current altitude: {current_altitude:.2f}m")
                        # 目標高度の95%に達したら成功とみなす
                        if current_altitude >= height * 0.95:
                            print(f"Reached target altitude of {height}m.")
                            return True
                    time.sleep(1)
                print(f"Takeoff timeout: Failed to reach {height}m within {timeout_sec}s.")
                return False
            
            return True # timeout_secが指定されなければコマンド送信だけで成功とする
                
        except Exception as e:
            print(f"Takeoff failed for {vehicle.name}: {e}")
            return False
    
    def moveToPosition(self, x: float, y: float, z: float, speed: float, 
                      yaw_deg: Optional[float] = None, timeout_sec: float = -1, 
                      vehicle_name: Optional[str] = None) -> bool:
        """ROS座標系で指定された位置へ移動"""
        vehicle = self._get_vehicle(vehicle_name)
        if not vehicle:
            return False
        
        try:
            # ROS(FLU) to NED変換
            ros_pos = Vector3r(x, y, z)
            ned_pos = self.converter.ros_to_ned_pos(ros_pos)

            if yaw_deg is None:
                # _get_yaw_degreeはROS座標系のヨーを返すので、NEDに変換
                ned_yaw_deg = self.converter.ros_to_ned_yaw(self._get_yaw_degree(vehicle_name))
            else:
                ned_yaw_deg = self.converter.ros_to_ned_yaw(yaw_deg)

            print(f"INFO: moveToPosition(ROS): x={x}, y={y}, z={z}, yaw={yaw_deg}")
            print(f"INFO: moveToPosition(NED): x={ned_pos.x}, y={ned_pos.y}, z={ned_pos.z}, yaw={ned_yaw_deg}")
            
            if not vehicle.move_to_position(ned_pos.x, ned_pos.y, ned_pos.z, ned_yaw_deg):
                return False

            # 目標位置到達待機（簡易実装）
            if timeout_sec > 0:
                start_time = time.time()
                while time.time() - start_time < timeout_sec:
                    current_pose = self.simGetVehiclePose(vehicle_name)
                    if current_pose:
                        distance = math.sqrt(
                            (current_pose.position.x - x)**2 +
                            (current_pose.position.y - y)**2 +
                            (current_pose.position.z - z)**2
                        )
                        if distance < 1.0:  # 1m以内で到達とみなす
                            print("DONE")
                            return True
                    time.sleep(0.5)
                print("Move timeout")
                return False
            else:
                print("DONE")
                return True
                
        except Exception as e:
            print(f"Move failed for {vehicle.name}: {e}")
            return False
    
    def moveToPositionUnityFrame(self, x: float, y: float, z: float, speed: float,
                               yaw_deg: Optional[float] = None, timeout_sec: float = -1,
                               vehicle_name: Optional[str] = None) -> bool:
        """Unity座標系での位置移動"""
        # Unity(X=右, Y=上, Z=前)からROS(X=前, Y=左, Z=上)に変換
        ros_x = z
        ros_y = -x
        ros_z = y
        # UnityのYawは時計回りが正、ROSのYawは反時計回りが正
        ros_yaw_deg = -yaw_deg if yaw_deg is not None else None
        
        return self.moveToPosition(ros_x, ros_y, ros_z, speed, ros_yaw_deg, timeout_sec, vehicle_name)
    
    def land(self, vehicle_name: Optional[str] = None) -> bool:
        """着陸"""
        vehicle = self._get_vehicle(vehicle_name)
        if not vehicle:
            return False
        
        try:
            print("INFO: Landing")
            return vehicle.land()
        except Exception as e:
            print(f"Land failed for {vehicle.name}: {e}")
            return False
    
    def simGetVehiclePose(self, vehicle_name: Optional[str] = None) -> Optional[Pose]:
        """車両の姿勢をROS座標系で取得"""
        vehicle = self._get_vehicle(vehicle_name)
        if not vehicle:
            return None

        ned_pose = vehicle.get_vehicle_pose()
        if not ned_pose:
            return None

        # NEDからROS(FLU)への変換
        ros_pos = self.converter.ned_to_ros_pos(ned_pose.position)
        ros_q = self.converter.ned_to_ros_orient(ned_pose.orientation)

        return Pose(position=ros_pos, orientation=ros_q)
    
    def simGetVehiclePoseUnityFrame(self, vehicle_name: Optional[str] = None) -> Optional[Pose]:
        """Unity座標系での車両姿勢を取得（ROS座標系からUnity座標系に変換）"""
        pose = self.simGetVehiclePose(vehicle_name)  # まずROS座標系で取得
        if not pose:
            return None
        
        # ROS座標系からUnity座標系に変換
        # ROS:   X=前, Y=左, Z=上
        # Unity: X=右, Y=上, Z=前
        unity_pos = Vector3r(
            -pose.position.y,  # ROS Y(左) → Unity X(右) 符号反転
            pose.position.z,   # ROS Z(上) → Unity Y(上)
            pose.position.x    # ROS X(前) → Unity Z(前)
        )
        
        # 姿勢もROS→Unity座標系変換
        roll, pitch, yaw = Quaternionr.quaternion_to_euler(pose.orientation)
        unity_orientation = Quaternionr.euler_to_quaternion(
            pitch,  # ROS pitch → Unity roll
            -yaw,   # ROS yaw → Unity pitch (符号反転)
            -roll   # ROS roll → Unity yaw (符号反転)
        )
        
        print(f"ROS({pose.position.x:.2f}, {pose.position.y:.2f}, {pose.position.z:.2f}) -> Unity({unity_pos.x:.2f}, {unity_pos.y:.2f}, {unity_pos.z:.2f})")
        
        return Pose(unity_pos, unity_orientation)
    
    def _get_yaw_degree(self, vehicle_name: Optional[str] = None) -> float:
        """現在のヨー角度を取得"""
        pose = self.simGetVehiclePose(vehicle_name)
        if not pose:
            return 0.0
        
        _, _, yaw = Quaternionr.quaternion_to_euler(pose.orientation)
        return math.degrees(yaw)
    
    def simGetImage(self, camera_id: int, image_type: str, vehicle_name: Optional[str] = None) -> Optional[bytes]:
        """カメラ画像を取得（プレースホルダー実装）"""
        print(f"INFO: simGetImage not implemented for MAVLink version")
        return None
    
    def simSetCameraOrientation(self, camera_id: int, degree: float, vehicle_name: Optional[str] = None) -> bool:
        """カメラ向きを設定（プレースホルダー実装）"""
        raise NotImplementedError("Camera orientation control not implemented in MAVLink version")
    
    def getLidarData(self, return_point_cloud: bool = False, vehicle_name: Optional[str] = None) -> Optional[LidarData]:
        """LIDARデータを取得（プレースホルダー実装）"""
        print(f"INFO: getLidarData not implemented for MAVLink version")
        return None
    
    def getGameJoystickData(self, vehicle_name: Optional[str] = None) -> Optional[GameControllerOperation]:
        """ゲームコントローラーデータを取得（プレースホルダー実装）"""
        print(f"INFO: getGameJoystickData not implemented for MAVLink version")
        return GameControllerOperation()
    
    def putGameJoystickData(self, data: GameControllerOperation, vehicle_name: Optional[str] = None) -> bool:
        """ゲームコントローラーデータを送信（プレースホルダー実装）"""
        print(f"INFO: putGameJoystickData not implemented for MAVLink version")
        return False
    
    def grab_baggage(self, grab: bool, timeout_sec: float = -1, vehicle_name: Optional[str] = None) -> bool:
        """荷物を掴む/離す（プレースホルダー実装）"""
        raise NotImplementedError("Gripper control not implemented in MAVLink version")


# 使用例
if __name__ == "__main__":
    print("=== Initial Status Check ===")

    # MAVLink版クライアント作成
    client = MultirotorClient()
    
    # 車両追加（複数可能）
    client.add_vehicle("drone1", "udp:127.0.0.1:14550")  # SITL接続例
    # client.add_vehicle("drone2", "udp:127.0.0.1:14551")  # 複数機体
    
    # 接続確立
    if not client.confirmConnection():
        print("Failed to connect to vehicles")
        exit(1)
    
    try:
        # API制御有効化
        client.enableApiControl(True)
        time.sleep(1.0)
        
        # ARM
        client.armDisarm(True)
        time.sleep(2.0)
        
        # 離陸
        if client.takeoff(10.0, timeout_sec=30):
            print("Takeoff successful")

            time.sleep(5.0)
            
            # 移動
            if client.moveToPosition(10.0, 0.0, 10.0, 5.0, timeout_sec=30):
                print("Move successful")
                
                # 着陸
                if client.land():
                    print("Landing successful")
        
    except KeyboardInterrupt:
        print("Interrupted by user")
    
    finally:
        # 接続切断
        client.disconnect_all()
        print("Disconnected from all vehicles")