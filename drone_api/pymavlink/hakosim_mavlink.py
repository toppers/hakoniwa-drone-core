#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAVLink版 MultirotorClient
箱庭のPDU通信をpymavlinkのMAVLink通信に置き換えた実装
"""

from pymavlink import mavutil
from collections import deque
import math, time
import time
import math
import queue
from typing import Optional, Dict, Any, List, Tuple, Callable
from enum import Enum
from hakoniwa_pdu.apps.drone.hakosim import MultirotorClient as HakoniwaSensorClient
from hakoniwa_pdu.apps.drone.hakosim import ImageType
from hakoniwa_pdu.apps.drone.hakosim_types import Pose, Quaternionr, Vector3r
from hakoniwa_pdu.apps.drone.hakosim_lidar import LidarData
from hakoniwa_pdu.pdu_msgs.hako_msgs.pdu_pytype_GameControllerOperation import GameControllerOperation


class FrameConverter:
    @staticmethod
    def ros_to_ned_pos(ros_pos: Vector3r) -> Vector3r:
        """ROS(FLU)座標系の位置をNED座標系に変換"""
        return Vector3r(
            x_val=ros_pos.x_val,
            y_val=-ros_pos.y_val,
            z_val=-ros_pos.z_val
        )

    @staticmethod
    def ned_to_ros_pos(ned_pos: Vector3r) -> Vector3r:
        """NED座標系の位置をROS(FLU)座標系に変換"""
        return Vector3r(
            x_val=ned_pos.x_val,
            y_val=-ned_pos.y_val,
            z_val=-ned_pos.z_val
        )

    @staticmethod
    def ned_to_ros_orient(ned_q: Quaternionr) -> Quaternionr:
        """NED座標系のクォータニオンをROS(FLU)座標系に変換"""
        # NEDからFLUへの変換は、ロール軸周りに180度回転
        roll_180 = Quaternionr.euler_to_quaternion(math.pi, 0, 0)
        
        # クォータニオンの積で回転を合成 (q_ros = q_ned * q_rot)
        return Quaternionr(
            w_val = ned_q.w_val * roll_180.w_val - ned_q.x_val * roll_180.x_val - ned_q.y_val * roll_180.y_val - ned_q.z_val * roll_180.z_val,
            x_val = ned_q.w_val * roll_180.x_val + ned_q.x_val * roll_180.w_val - ned_q.y_val * roll_180.z_val + ned_q.z_val * roll_180.y_val,
            y_val = ned_q.w_val * roll_180.y_val - ned_q.x_val * roll_180.z_val + ned_q.y_val * roll_180.w_val - ned_q.z_val * roll_180.x_val,
            z_val = ned_q.w_val * roll_180.z_val + ned_q.x_val * roll_180.y_val - ned_q.y_val * roll_180.x_val + ned_q.z_val * roll_180.w_val
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

class MavlinkMultirotorClient:
    def __init__(self, default_drone_name: str = None, sensor_client: HakoniwaSensorClient = None):
        """
        MAVLink版MultirotorClient初期化
        
        Args:
            default_drone_name: デフォルトドローン名
        """
        self.vehicles: Dict[str, MavlinkDrone] = {}
        self.default_drone_name = default_drone_name
        self._connected = False
        self.converter = FrameConverter()
        
        # デフォルト設定
        if default_drone_name is None:
            self.default_drone_name = "drone1"

        # Hakoniwaセンサー取得用のクライアントを初期化
        self.sensor_client = sensor_client

    
    def add_vehicle(self, name: str, connection_string: str):
        """車両を追加"""
        self.vehicles[name] = MavlinkDrone(name, connection_string)
        if self.default_drone_name is None:
            self.default_drone_name = name
        print(f"Added vehicle: {name} with connection: {connection_string}")
    
    def confirmConnection(self) -> bool:
        """全車両への接続を確認・確立"""
        # MAVLinkコントローラーへの接続
        if not self.vehicles:
            print("No vehicles configured. Use add_vehicle() first.")
            return False
            
        print("Connecting to MAVLink...")
        controller_ok = True
        for vehicle in self.vehicles.values():
            if not vehicle.connect():
                controller_ok = False
            vehicle.get_arming_check_status()
            vehicle.pump_status_text(3.0)

        # Hakoniwaセンサー用クライアントへの接続
        if self.sensor_client is not None:
            print("Connecting to Hakoniwa PDU for sensors...")
            sensor_ok = self.sensor_client.confirmConnection()
            self._connected = controller_ok and sensor_ok
        else:
            self._connected = controller_ok
        return self._connected
    
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
            print(f"Waiting to reach altitude of {height}m...")
            start_time = time.time()
            while True:
                current_pose = self.simGetVehiclePose(vehicle_name)
                if current_pose:
                    current_altitude = current_pose.position.z_val
                    print(f"Current altitude: {current_altitude:.2f}m")
                    # 目標高度の95%に達したら成功とみなす
                    if current_altitude >= height * 0.95:
                        print(f"Reached target altitude of {height}m.")
                        return True
                time.sleep(1)
                if timeout_sec > 0 and time.time() - start_time > timeout_sec:
                    print(f"Takeoff timeout: Failed to reach {height}m within {timeout_sec}s.")
                    return False
        except Exception as e:
            print(f"Takeoff failed for {vehicle.name}: {e}")
            return False
    
    def _yaw_wrap_deg(self, d):
        d = (d + 180.0) % 360.0 - 180.0
        return d

    def _dist3(self, a, b):
        return math.sqrt((a[0]-b[0])**2+(a[1]-b[1])**2+(a[2]-b[2])**2)

    def moveToPosition(self, x: float, y: float, z: float, speed: float,
                    yaw_deg: float | None = None, timeout_sec: float = -1,
                    vehicle_name: str | None = None) -> bool:
        """ROS(FLU)座標で指定位置へ移動。位置+ヨー+速度が収束し、dwell継続で完了。"""
        vehicle = self._get_vehicle(vehicle_name)
        if not vehicle:
            return False

        # ---- パラメータ（必要に応じて調整） ----
        POS_TOL = 0.30        # 位置誤差 [m]
        POS_TOL_OUT = POS_TOL + 0.20  # ヒステリシス外側
        YAW_TOL_DEG = 5.0     # ヨー誤差 [deg]
        VEL_TOL = 0.20        # 速度しきい [m/s]
        DWELL_SEC = 1.0       # 収束状態の維持時間 [s]
        POLL = 0.1            # ポーリング周期 [s]
        SPEED_CMD = max(0.1, float(speed))

        try:
            # ---- 目標をNEDに変換してコマンド送出 ----
            ros_pos = Vector3r(x, y, z)
            ned_pos = self.converter.ros_to_ned_pos(ros_pos)
            if yaw_deg is None:
                ros_yaw_cmd = self._get_yaw_degree(vehicle_name)
            else:
                ros_yaw_cmd = float(yaw_deg)
            ned_yaw_cmd = self.converter.ros_to_ned_yaw(ros_yaw_cmd)

            print(f"[CMD] moveToPosition ROS(xyz,yaw)=({x:.2f},{y:.2f},{z:.2f},{ros_yaw_cmd:.1f}) "
                f"=> NED({ned_pos.x_val:.2f},{ned_pos.y_val:.2f},{ned_pos.z_val:.2f},{ned_yaw_cmd:.1f})")

            ok = vehicle.move_to_position(ned_pos.x_val, ned_pos.y_val, ned_pos.z_val, ned_yaw_cmd)
            if not ok:
                print("move_to_position rejected by vehicle")
                return False

            # ---- 監視ループ：ROS座標で誤差評価 ----
            target_ros = (x, y, z)
            target_yaw_ros = ros_yaw_cmd

            pos_hist = deque(maxlen=6)  # 0.5～0.6秒ぶんの履歴（POLL=0.1想定）
            t0 = time.time()
            dwell_entered_at = None
            inside = False

            while True:
                pose = self.simGetVehiclePose(vehicle_name)
                if pose is None:
                    time.sleep(POLL)
                    continue

                # 現在姿勢（ROS想定）
                cur_ros = (pose.position.x_val, pose.position.y_val, pose.position.z_val)
                # ※もし simGetVehiclePose が NED を返す環境なら下行を使ってROSへ変換
                # cur_ros = self.converter.ned_to_ros_pos(pose.position)

                # 現在ヨー（ROS想定）。NEDで来るなら変換関数を使う
                cur_yaw_ros = self._get_yaw_degree(vehicle_name)

                # 誤差
                pos_err = self._dist3(cur_ros, target_ros)
                yaw_err = abs(self._yaw_wrap_deg(cur_yaw_ros - target_yaw_ros))

                # 速度（位置差分から近似）
                now = time.time()
                pos_hist.append((now, cur_ros))
                vel = None
                if len(pos_hist) >= 2:
                    (t_prev, p_prev) = pos_hist[0]
                    dt = max(1e-3, now - t_prev)
                    vel = self._dist3(cur_ros, p_prev) / dt

                # 到達内側／外側の判定（ヒステリシス）
                if pos_err <= POS_TOL and (yaw_deg is None or yaw_err <= YAW_TOL_DEG) and (vel is None or vel <= VEL_TOL):
                    if not inside:
                        inside = True
                        dwell_entered_at = now
                    elif (now - dwell_entered_at) >= DWELL_SEC:
                        print(f"[DONE] pos_err={pos_err:.2f}m yaw_err={yaw_err:.1f}° vel={0.0 if vel is None else vel:.2f}m/s")
                        return True
                else:
                    # 外に出たときは、外側しきいでリセット
                    if pos_err >= POS_TOL_OUT or (yaw_deg is not None and yaw_err > YAW_TOL_DEG) or (vel is not None and vel > VEL_TOL):
                        inside = False
                        dwell_entered_at = None

                # デバッグ表示（必要なら間引いて）
                if vel is not None:
                    print(f"err={pos_err:.2f}m yaw={yaw_err:.1f}° vel={vel:.2f}m/s inside={inside}")

                # タイムアウト
                if timeout_sec > 0 and (now - t0) > timeout_sec:
                    print(f"[TIMEOUT] pos_err={pos_err:.2f}m yaw_err={yaw_err:.1f}°")
                    return False

                time.sleep(POLL)

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
            -pose.position.y_val,  # ROS Y(左) → Unity X(右) 符号反転
            pose.position.z_val,   # ROS Z(上) → Unity Y(上)
            pose.position.x_val    # ROS X(前) → Unity Z(前)
        )
        
        # 姿勢もROS→Unity座標系変換
        roll, pitch, yaw = Quaternionr.quaternion_to_euler(pose.orientation)
        unity_orientation = Quaternionr.euler_to_quaternion(
            pitch,  # ROS pitch → Unity roll
            -yaw,   # ROS yaw → Unity pitch (符号反転)
            -roll   # ROS roll → Unity yaw (符号反転)
        )

        print(f"ROS({pose.position.x_val:.2f}, {pose.position.y_val:.2f}, {pose.position.z_val:.2f}) -> Unity({unity_pos.x_val:.2f}, {unity_pos.y_val:.2f}, {unity_pos.z_val:.2f})")

        return Pose(unity_pos, unity_orientation)
    
    def _get_yaw_degree(self, vehicle_name: Optional[str] = None) -> float:
        """現在のヨー角度を取得"""
        pose = self.simGetVehiclePose(vehicle_name)
        if not pose:
            return 0.0
        
        _, _, yaw = Quaternionr.quaternion_to_euler(pose.orientation)
        return math.degrees(yaw)
    
    def simGetImage(self, camera_id: int, image_type: str, vehicle_name: Optional[str] = None) -> Optional[bytes]:
        """カメラ画像を取得"""
        if self.sensor_client is None:
            raise ValueError("HakoniwaSensorClient is not initialized")

        return self.sensor_client.simGetImage(camera_id, image_type, self.get_vehicle_name(vehicle_name))
    
    def simSetCameraOrientation(self, camera_id: int, degree: float, vehicle_name: Optional[str] = None) -> bool:
        """カメラ向きを設定"""
        if self.sensor_client is None:
            raise ValueError("HakoniwaSensorClient is not initialized")
        # hakosim.pyの戻り値は実際には角度情報だが、ここでは成功/失敗のbool値に変換
        result = self.sensor_client.simSetCameraOrientation(camera_id, degree, self.get_vehicle_name(vehicle_name))
        return result is not None
    
    def getLidarData(self, return_point_cloud: bool = False, vehicle_name: Optional[str] = None) -> Optional[LidarData]:
        """LIDARデータを取得"""
        if self.sensor_client is None:
            raise ValueError("HakoniwaSensorClient is not initialized")
        # 注: 返されるデータ型はHakoniwaSensorClientの実装に依存
        return self.sensor_client.getLidarData(return_point_cloud, self.get_vehicle_name(vehicle_name))
    
    def getGameJoystickData(self, vehicle_name: Optional[str] = None) -> Optional[GameControllerOperation]:
        """ゲームコントローラーデータを取得"""
        if self.sensor_client is None:
            raise ValueError("HakoniwaSensorClient is not initialized")
        # 注: 返されるデータ型はHakoniwaSensorClientの実装に依存
        return self.sensor_client.getGameJoystickData(self.get_vehicle_name(vehicle_name))
    
    def putGameJoystickData(self, data: GameControllerOperation, vehicle_name: Optional[str] = None) -> bool:
        """ゲームコントローラーデータを送信（プレースホルダー実装）"""
        if self.sensor_client is None:
            raise ValueError("HakoniwaSensorClient is not initialized")
        print(f"INFO: putGameJoystickData not fully implemented due to data type conversion requirement.")
        # 異なるGameControllerOperation型間の変換が必要なため、未実装
        return False
    
    def grab_baggage(self, grab: bool, timeout_sec: float = -1, vehicle_name: Optional[str] = None) -> bool:
        """荷物を掴む/離す"""
        if self.sensor_client is None:
            raise ValueError("HakoniwaSensorClient is not initialized")
        return self.sensor_client.grab_baggage(grab, timeout_sec, self.get_vehicle_name(vehicle_name))


# 使用例
if __name__ == "__main__":
    print("=== Initial Status Check ===")

    # MAVLink版クライアント作成
    client = MavlinkMultirotorClient()
    
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