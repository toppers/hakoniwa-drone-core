#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MAVLink版 MultirotorClient
箱庭のPDU通信をpymavlinkのMAVLink通信に置き換えた実装
"""

from pymavlink import mavutil
from collections import deque
import math, time
import queue
import argparse
from typing import Optional, Dict, Any, List, Tuple, Callable

from hakoniwa_pdu.apps.drone.hakosim import MultirotorClient as HakoniwaSensorClient
from hakoniwa_pdu.apps.drone.hakosim import ImageType
from hakoniwa_pdu.apps.drone.hakosim_types import Pose, Quaternionr, Vector3r
from hakoniwa_pdu.apps.drone.hakosim_lidar import LidarData
from hakoniwa_pdu.pdu_msgs.hako_msgs.pdu_pytype_GameControllerOperation import GameControllerOperation

# 新しいコントローラークラスをインポート
from hakosim_controllers import AbstractFlightController, ArduPilotController, PX4Controller


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
        # x軸にπ回転（Rx(π) = [0, 1, 0, 0]）
        q_rot = Quaternionr.euler_to_quaternion(math.pi, 0.0, 0.0)
        w1, x1, y1, z1 = q_rot.w_val, q_rot.x_val, q_rot.y_val, q_rot.z_val
        w2, x2, y2, z2 = ned_q.w_val, ned_q.x_val, ned_q.y_val, ned_q.z_val

        w = w1*w2 - x1*x2 - y1*y2 - z1*z2
        x = w1*x2 + x1*w2 + y1*z2 - z1*y2
        y = w1*y2 - x1*z2 + y1*w2 + z1*x2
        z = w1*z2 + x1*y2 - y1*x2 + z1*w2
        return Quaternionr(w, x, y, z)

    @staticmethod
    def ros_to_ned_yaw(ros_yaw_deg: float) -> float:
        """ROS座標系のヨー角をNED座標系に変換"""
        return -ros_yaw_deg


class MavlinkDrone:
    """
    単一のドローンを管理するクラス。
    フライトスタック固有のロジックは `controller` に委譲する。
    """
    def __init__(self, name: str, connection_string: str, controller: AbstractFlightController):
        self.name = name
        self.connection_string = connection_string
        self.controller = controller
        self.mavlink_connection = None
        self.enableApiControl = False
        self.arm = False

    def connect(self) -> bool:
        """MAVLink接続を確立し、コントローラを初期化する"""
        try:
            self.mavlink_connection = mavutil.mavlink_connection(
                self.connection_string,
                source_system=255,
                source_component=190
            )

            print("Waiting for a valid heartbeat...")
            start_time = time.time()
            timeout = 10  # 10 seconds timeout
            while time.time() - start_time < timeout:
                self.mavlink_connection.wait_heartbeat(timeout=1)
                if self.mavlink_connection.target_system > 0:
                    break
                print(f"  ... received HB from sys {self.mavlink_connection.target_system}, waiting for a valid one.")

            if self.mavlink_connection.target_system == 0:
                print("Error: Timed out waiting for a valid heartbeat.")
                return False

            print(f"HB from sys {self.mavlink_connection.target_system} comp {self.mavlink_connection.target_component}")
            
            # コントローラに接続を渡し、初期化を実行
            self.controller.init_connection(self.mavlink_connection)
            
            print(f"Connected to {self.name}")
            return True
        except Exception as e:
            print(f"Failed to connect to {self.name}: {e}")
            return False

    def disconnect(self):
        """接続を切断"""
        # PX4のストリーミングを停止
        self.controller.stop_movement()
        if self.mavlink_connection:
            self.mavlink_connection.close()
        print(f"Disconnected from {self.name}")

    def get_vehicle_pose(self) -> Optional[Pose]:
        """車両の姿勢(NED)を取得"""
        if not self.mavlink_connection:
            return None
        
        try:
            att = self.mavlink_connection.recv_match(type='ATTITUDE', blocking=True, timeout=1.0)
            pos = self.mavlink_connection.recv_match(type='LOCAL_POSITION_NED', blocking=True, timeout=1.0)
            
            if not att or not pos:
                return None
            
            position = Vector3r(pos.x, pos.y, pos.z)
            orientation = Quaternionr.euler_to_quaternion(att.roll, att.pitch, att.yaw)
            return Pose(position, orientation)
            
        except Exception as e:
            print(f"Failed to get pose for {self.name}: {e}")
            return None


class MavlinkMultirotorClient:
    def __init__(self, default_drone_name: str = None, sensor_client: HakoniwaSensorClient = None):
        self.vehicles: Dict[str, MavlinkDrone] = {}
        self.default_drone_name = default_drone_name
        self._connected = False
        self.converter = FrameConverter()
        self.sensor_client = sensor_client

    def add_vehicle(self, name: str, connection_string: str, vehicle_type: str):
        if vehicle_type.lower() == "ardupilot":
            controller = ArduPilotController()
        elif vehicle_type.lower() == "px4":
            controller = PX4Controller()
        else:
            raise ValueError(f"Unknown vehicle_type: {vehicle_type}. Use 'ardupilot' or 'px4'.")

        self.vehicles[name] = MavlinkDrone(name, connection_string, controller)
        if self.default_drone_name is None:
            self.default_drone_name = name

    def confirmConnection(self) -> bool:
        if not self.vehicles:
            print("No vehicles configured. Use add_vehicle() first.")
            return False
            
        print("Connecting to MAVLink vehicles...")
        controller_ok = all(vehicle.connect() for vehicle in self.vehicles.values())

        if self.sensor_client:
            print("Connecting to Hakoniwa PDU for sensors...")
            sensor_ok = self.sensor_client.confirmConnection()
            self._connected = controller_ok and sensor_ok
        else:
            self._connected = controller_ok
        
        return self._connected

    def disconnect_all(self):
        for vehicle in self.vehicles.values():
            vehicle.disconnect()
        self._connected = False

    def get_vehicle_name(self, vehicle_name: Optional[str]) -> Optional[str]:
        if vehicle_name is None:
            return self.default_drone_name
        if vehicle_name in self.vehicles:
            return vehicle_name
        print(f"Vehicle '{vehicle_name}' not found.")
        return None

    def _get_vehicle(self, vehicle_name: Optional[str]) -> Optional[MavlinkDrone]:
        name = self.get_vehicle_name(vehicle_name)
        return self.vehicles.get(name) if name else None

    def enableApiControl(self, enable: bool, vehicle_name: Optional[str] = None):
        vehicle = self._get_vehicle(vehicle_name)
        if not vehicle: return

        if enable:
            print(f"Enabling API control for {vehicle.name}...")
            if vehicle.controller.set_api_mode():
                vehicle.enableApiControl = True
                print(f"API control enabled for {vehicle.name}")
            else:
                print(f"Failed to enable API control for {vehicle.name}")
        else:
            print(f"Disabling API control for {vehicle.name}...")
            vehicle.controller.stop_movement()
            vehicle.enableApiControl = False

    def armDisarm(self, arm: bool, vehicle_name: Optional[str] = None) -> bool:
        vehicle = self._get_vehicle(vehicle_name)
        if not vehicle: return False

        if arm:
            if not vehicle.enableApiControl:
                print("API control is not enabled. Call enableApiControl(True) first.")
                return False
            
            print(f"Arming {vehicle.name}...")
            if vehicle.controller.arm():
                vehicle.arm = True
                return True
            print(f"Failed to arm {vehicle.name}")
            return False
        else:
            print(f"Disarming {vehicle.name}...")
            if vehicle.controller.disarm():
                vehicle.arm = False
                return True
            print(f"Failed to disarm {vehicle.name}")
            return False

    def takeoff(self, height: float, vehicle_name: Optional[str] = None, timeout_sec: float = -1) -> bool:
        vehicle = self._get_vehicle(vehicle_name)
        if not vehicle: return False
        
        try:
            print(f"INFO: Takeoff requested to {height}m (ROS frame)")
            
            if not vehicle.arm:
                print("Vehicle not armed. Arming first...")
                if not self.armDisarm(True, vehicle_name):
                    print("Failed to arm before takeoff")
                    return False
                time.sleep(1.0)

            ned_z = -height
            if not vehicle.controller.takeoff(ned_z):
                print("Takeoff command failed")
                return False

            print(f"Waiting to reach altitude of {height}m...")
            start_time = time.time()
            while True:
                pose = self.simGetVehiclePose(vehicle_name)
                if pose:
                    current_altitude = pose.position.z_val
                    print(f"Current altitude: {current_altitude:.2f}m")
                    if current_altitude >= height * 0.95:
                        print(f"Reached target altitude of {height}m.")
                        return True
                
                if timeout_sec > 0 and (time.time() - start_time) > timeout_sec:
                    print(f"Takeoff timeout: Failed to reach {height}m in {timeout_sec}s.")
                    return False
                time.sleep(1)

        except Exception as e:
            print(f"Takeoff failed for {vehicle.name}: {e}")
            return False

    def land(self, vehicle_name: Optional[str] = None) -> bool:
        vehicle = self._get_vehicle(vehicle_name)
        if not vehicle: return False
        print(f"INFO: Landing {vehicle.name}")
        return vehicle.controller.land()

    def _yaw_wrap_deg(self, d):
        return (d + 180.0) % 360.0 - 180.0

    def _dist3(self, a, b):
        return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2)

    def moveToPosition(self, x: float, y: float, z: float, speed: float,
                    yaw_deg: float = None, timeout_sec: float = -1,
                    vehicle_name: str = None) -> bool:
        vehicle = self._get_vehicle(vehicle_name)
        if not vehicle: return False

        POS_TOL = 0.50
        POS_TOL_OUT = POS_TOL + 0.20
        YAW_TOL_DEG = 5.0
        VEL_TOL = 0.20
        DWELL_SEC = 1.0
        POLL = 0.1

        try:
            ros_pos = Vector3r(x, y, z)
            ned_pos = self.converter.ros_to_ned_pos(ros_pos)
            ros_yaw_cmd = yaw_deg if yaw_deg is not None else self._get_yaw_degree(vehicle_name)
            ned_yaw_cmd = self.converter.ros_to_ned_yaw(ros_yaw_cmd)

            print(f"[CMD] moveTo ROS(xyz,yaw)=({x:.2f},{y:.2f},{z:.2f},{ros_yaw_cmd:.1f}) "
                  f"=> NED({ned_pos.x_val:.2f},{ned_pos.y_val:.2f},{ned_pos.z_val:.2f},{ned_yaw_cmd:.1f})")

            vehicle.controller.go_to_local_ned(ned_pos.x_val, ned_pos.y_val, ned_pos.z_val, ned_yaw_cmd)

            target_ros = (x, y, z)
            pos_hist = deque(maxlen=6)
            t0 = time.time()
            dwell_entered_at = None
            inside = False
            
            while True:
                pose = self.simGetVehiclePose(vehicle_name)
                if not pose:
                    time.sleep(POLL)
                    continue

                cur_ros = (pose.position.x_val, pose.position.y_val, pose.position.z_val)
                cur_yaw_ros = self._get_yaw_degree(vehicle_name)

                pos_err = self._dist3(cur_ros, target_ros)
                yaw_err = abs(self._yaw_wrap_deg(cur_yaw_ros - ros_yaw_cmd))

                now = time.time()
                pos_hist.append((now, cur_ros))
                vel = None
                if len(pos_hist) >= 2:
                    (t_prev, p_prev) = pos_hist[0]
                    dt = max(1e-3, now - t_prev)
                    vel = self._dist3(cur_ros, p_prev) / dt

                if pos_err <= POS_TOL and yaw_err <= YAW_TOL_DEG and (vel is None or vel <= VEL_TOL):
                    if not inside:
                        inside = True
                        dwell_entered_at = now
                    elif (now - dwell_entered_at) >= DWELL_SEC:
                        print(f"[DONE] Reached target: pos_err={pos_err:.2f}m, yaw_err={yaw_err:.1f}°, vel={vel:.2f}m/s")
                        vehicle.controller.stop_movement()
                        return True
                else:
                    if pos_err >= POS_TOL_OUT or yaw_err > YAW_TOL_DEG or (vel is not None and vel > VEL_TOL):
                        inside = False
                        dwell_entered_at = None

                vel_str = f"{vel:.2f}m/s" if vel is not None else "N/A"
                print(f"err={pos_err:.2f}m, yaw={yaw_err:.1f}°, vel={vel_str}, inside={inside}")

                if timeout_sec > 0 and (time.time() - t0) > timeout_sec:
                    print(f"[TIMEOUT] Failed to reach target in time.")
                    vehicle.controller.stop_movement()
                    return False
                time.sleep(POLL)

        except Exception as e:
            print(f"Move failed for {vehicle.name}: {e}")
            if vehicle: vehicle.controller.stop_movement()
            return False

    def moveToPositionUnityFrame(self, x: float, y: float, z: float, speed: float,
                               yaw_deg: Optional[float] = None, timeout_sec: float = -1,
                               vehicle_name: Optional[str] = None) -> bool:
        ros_x, ros_y, ros_z = z, -x, y
        ros_yaw_deg = -yaw_deg if yaw_deg is not None else None
        return self.moveToPosition(ros_x, ros_y, ros_z, speed, ros_yaw_deg, timeout_sec, vehicle_name)

    def simGetVehiclePose(self, vehicle_name: Optional[str] = None) -> Optional[Pose]:
        vehicle = self._get_vehicle(vehicle_name)
        if not vehicle: return None
        ned_pose = vehicle.get_vehicle_pose()
        if not ned_pose: return None
        ros_pos = self.converter.ned_to_ros_pos(ned_pose.position)
        ros_q = self.converter.ned_to_ros_orient(ned_pose.orientation)
        return Pose(position=ros_pos, orientation=ros_q)

    def _get_yaw_degree(self, vehicle_name: Optional[str] = None) -> float:
        pose = self.simGetVehiclePose(vehicle_name)
        if not pose: return 0.0
        _, _, yaw = Quaternionr.quaternion_to_euler(pose.orientation)
        return math.degrees(yaw)

    def simGetImage(self, camera_id: int, image_type: ImageType, vehicle_name: Optional[str] = None) -> Optional[bytes]:
        if self.sensor_client is None: raise ValueError("Sensor client not initialized")
        return self.sensor_client.simGetImage(camera_id, image_type, self.get_vehicle_name(vehicle_name))

    def simSetCameraOrientation(self, camera_id: int, degree: float, vehicle_name: Optional[str] = None) -> bool:
        if self.sensor_client is None: raise ValueError("Sensor client not initialized")
        return self.sensor_client.simSetCameraOrientation(camera_id, degree, self.get_vehicle_name(vehicle_name)) is not None

    def getLidarData(self, vehicle_name: Optional[str] = None) -> Optional[LidarData]:
        if self.sensor_client is None: raise ValueError("Sensor client not initialized")
        return self.sensor_client.getLidarData(self.get_vehicle_name(vehicle_name))
    
    def grab_baggage(self, grab: bool, timeout_sec: float = -1, vehicle_name: Optional[str] = None) -> bool:
        if self.sensor_client is None: raise ValueError("Sensor client not initialized")
        return self.sensor_client.grab_baggage(grab, timeout_sec, self.get_vehicle_name(vehicle_name))

    def sleep(self, seconds: float):
        time.sleep(seconds)

# --- Main execution block ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Control a MAVLink drone.")
    parser.add_argument('--name', type=str, default='Drone', help='Name of the drone.')
    parser.add_argument('--connection', type=str, required=True, help='Connection string (e.g., udp:127.0.0.1:14540).')
    parser.add_argument('--type', type=str, default='px4', choices=['px4', 'ardupilot'], help='Vehicle type (px4 or ardupilot).')
    args = parser.parse_args()

    client = MavlinkMultirotorClient(default_drone_name=args.name)
    #client.add_vehicle("drone1", "udp:127.0.0.1:14540", "px4")
    print(f"Adding vehicle: {args.name} ({args.type}) with connection: {args.connection}")
    client.add_vehicle(args.name, args.connection, args.type)

    if not client.confirmConnection():
        print("Failed to connect to vehicle(s).")
        exit(1)
    
    try:
        print("--- Starting mission ---")
        client.enableApiControl(True)
        time.sleep(1)
        
        if not client.armDisarm(True):
            print("Failed to arm vehicle.")
            exit(1)
        time.sleep(2)
        
        if client.takeoff(1.0, timeout_sec=60):
            print("Takeoff successful.")
            time.sleep(5)
            
            if client.moveToPosition(2.0, 0.0, 1.0, 5.0, timeout_sec=60):
                print("Move 1 successful.")
                time.sleep(2)

                if client.moveToPosition(2.0, 2.0, 1.0, 5.0, yaw_deg=90, timeout_sec=60):
                    print("Move 2 successful.")
                    time.sleep(2)

                    if client.moveToPosition(0.0, 0.0, 1.0, 5.0, yaw_deg=0, timeout_sec=60):
                        print("Move 3 successful.")
                        time.sleep(2)

        client.land()
        time.sleep(5)
        
    except KeyboardInterrupt:
        print("Interrupted by user.")
    
    finally:
        print("--- Cleaning up ---")
        client.armDisarm(False)
        client.disconnect_all()
        print("Cleanup complete.")
