import hakopy
from hakoniwa_pdu.pdu_manager import PduManager
from hakoniwa_pdu.impl.shm_communication_service import ShmCommunicationService
from hakoniwa_pdu.pdu_msgs.geometry_msgs.pdu_pytype_Twist import Twist
from hakoniwa_pdu.pdu_msgs.geometry_msgs.pdu_conv_Twist import pdu_to_py_Twist 
from hakoniwa_pdu.pdu_msgs.hako_msgs.pdu_pytype_GameControllerOperation import GameControllerOperation
from hakoniwa_pdu.pdu_msgs.hako_msgs.pdu_conv_GameControllerOperation import py_to_pdu_GameControllerOperation, pdu_to_py_GameControllerOperation

from hakoniwa_pdu.pdu_msgs.hako_msgs.pdu_pytype_HakoDroneCmdTakeoff import HakoDroneCmdTakeoff
from hakoniwa_pdu.pdu_msgs.hako_msgs.pdu_conv_HakoDroneCmdTakeoff import py_to_pdu_HakoDroneCmdTakeoff, pdu_to_py_HakoDroneCmdTakeoff
from hakoniwa_pdu.pdu_msgs.hako_msgs.pdu_pytype_HakoDroneCmdLand import HakoDroneCmdLand
from hakoniwa_pdu.pdu_msgs.hako_msgs.pdu_conv_HakoDroneCmdLand import py_to_pdu_HakoDroneCmdLand, pdu_to_py_HakoDroneCmdLand
from hakoniwa_pdu.pdu_msgs.hako_msgs.pdu_pytype_HakoDroneCmdMove import HakoDroneCmdMove
from hakoniwa_pdu.pdu_msgs.hako_msgs.pdu_conv_HakoDroneCmdMove import py_to_pdu_HakoDroneCmdMove, pdu_to_py_HakoDroneCmdMove

# hako_msgs/HakoCmdCamera
from hakoniwa_pdu.pdu_msgs.hako_msgs.pdu_pytype_HakoCmdCamera import HakoCmdCamera
from hakoniwa_pdu.pdu_msgs.hako_msgs.pdu_conv_HakoCmdCamera import py_to_pdu_HakoCmdCamera, pdu_to_py_HakoCmdCamera
# hako_msgs/HakoCmdCameraMove
from hakoniwa_pdu.pdu_msgs.hako_msgs.pdu_pytype_HakoCmdCameraMove import HakoCmdCameraMove
from hakoniwa_pdu.pdu_msgs.hako_msgs.pdu_conv_HakoCmdCameraMove import py_to_pdu_HakoCmdCameraMove, pdu_to_py_HakoCmdCameraMove
# hako_msgs/HakoCameraData
from hakoniwa_pdu.pdu_msgs.hako_msgs.pdu_pytype_HakoCameraData import HakoCameraData
from hakoniwa_pdu.pdu_msgs.hako_msgs.pdu_conv_HakoCameraData import py_to_pdu_HakoCameraData, pdu_to_py_HakoCameraData
# hako_msgs/HakoCameraInfo
from hakoniwa_pdu.pdu_msgs.hako_msgs.pdu_pytype_HakoCameraInfo import HakoCameraInfo
from hakoniwa_pdu.pdu_msgs.hako_msgs.pdu_conv_HakoCameraInfo import py_to_pdu_HakoCameraInfo, pdu_to_py_HakoCameraInfo
# hako_msgs/HakoStatusMagnetHolder
from hakoniwa_pdu.pdu_msgs.hako_msgs.pdu_pytype_HakoStatusMagnetHolder import HakoStatusMagnetHolder
from hakoniwa_pdu.pdu_msgs.hako_msgs.pdu_conv_HakoStatusMagnetHolder import py_to_pdu_HakoStatusMagnetHolder, pdu_to_py_HakoStatusMagnetHolder
# hako_msgs/HakoCmdMagnetHolder
from hakoniwa_pdu.pdu_msgs.hako_msgs.pdu_pytype_HakoCmdMagnetHolder import HakoCmdMagnetHolder
from hakoniwa_pdu.pdu_msgs.hako_msgs.pdu_conv_HakoCmdMagnetHolder import py_to_pdu_HakoCmdMagnetHolder, pdu_to_py_HakoCmdMagnetHolder
# sensor_msgs/PointCloud2
from hakoniwa_pdu.pdu_msgs.sensor_msgs.pdu_pytype_PointCloud2 import PointCloud2
from hakoniwa_pdu.pdu_msgs.sensor_msgs.pdu_conv_PointCloud2 import pdu_to_py_PointCloud2, py_to_pdu_PointCloud2

import libs.hakosim_types as hakosim_types
import libs.hakosim_lidar as hakosim_lidar
import math
import json
import os
import time

class ImageType:
    Scene = "png"

class HakoDrone:
    def __init__(self, name):
        self.name = name
        self.enableApiControl = False
        self.arm = False
        self.camera_cmd_request_id = 1
        self.camera_move_cmd_request_id = 1

class MultirotorClient:
    def __init__(self, config_path, default_drone_name = None):
        self.pdu_manager = None
        self.config_path = config_path
        self.pdudef = self._load_json(config_path)
        self.vehicles = {}
        self.last_read_time = 0
        default_drone_set = False
        if default_drone_name is None:
            for entry in self.pdudef['robots']:
                entry_name = entry['name']
                if len(entry['shm_pdu_readers']) > 0 or len(entry['shm_pdu_writers']) > 0 or len(entry['rpc_pdu_readers']) > 0 or len(entry['rpc_pdu_writers']) > 0:
                    self.vehicles[entry_name] = HakoDrone(entry_name)
                    if not default_drone_set:
                        self.default_drone_name = entry_name
                        default_drone_set = True
            print("default drone name: ", default_drone_name)
        else:
            print("default drone name: ", default_drone_name)
            self.default_drone_name = default_drone_name
            self.vehicles[default_drone_name] = HakoDrone(default_drone_name)

    def _load_json(self, path):
        try:
            with open(path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"ERROR: File not found '{path}'")
        except json.JSONDecodeError:
            print(f"ERROR: Invalid Json fromat '{path}'")
        except PermissionError:
            print(f"ERROR: Permission denied '{path}'")
        except Exception as e:
            print(f"ERROR: {e}")
        return None

    def run_nowait(self):
        if self.pdu_manager is not None:
            self.pdu_manager.run_nowait()
        else:
            print("ERROR: PDU manager is not initialized. Call confirmConnection() first.")
            return False

    def sleep(self, seconds: float):
        if seconds > 0:
            time.sleep(seconds)
        else:
            print("ERROR: sleep seconds must be greater than 0")
            return False
        self.run_nowait()
        return True
    
    def _read_carefully(self, vehicle_name, pdu_name):
        if self.pdu_manager is None:
            print("ERROR: PDU manager is not initialized. Call confirmConnection() first.")
            return None
        if time.time() - self.last_read_time > 0.02: #20ms
            self.pdu_manager.run_nowait()
        raw_data = self.pdu_manager.read_pdu_raw_data(vehicle_name, pdu_name)
        if raw_data is None or len(raw_data) == 0:
            self.pdu_manager.run_nowait()
            raw_data = self.pdu_manager.read_pdu_raw_data(vehicle_name, pdu_name)
            if raw_data is None or len(raw_data) == 0:
                print(f"ERROR: Failed to read data for {pdu_name} from vehicle '{vehicle_name}'")
                return None
        if raw_data is not None and len(raw_data) > 0:
            self.last_read_time = time.time()
        return raw_data

    def confirmConnection(self):
        pdu_manager = PduManager()
        pdu_manager.initialize(config_path=self.config_path, comm_service=ShmCommunicationService())
        pdu_manager.start_service_nowait()
        self.pdu_manager = pdu_manager
        ret = hakopy.init_for_external()
        if ret == False:
            print(f"ERROR: init_for_external() returns {ret}.")
            return False
        return True

    def enableApiControl(self, v, vehicle_name=None):
        if vehicle_name is None:
            vehicle_name = self.default_drone_name
        if vehicle_name in self.vehicles:
            self.vehicles[vehicle_name].enableApiControl = v
        else:
            print(f"Vehicle '{vehicle_name}' not found.")

    def armDisarm(self, v, vehicle_name=None):
        if vehicle_name is None:
            vehicle_name = self.default_drone_name
        if vehicle_name in self.vehicles:
            self.vehicles[vehicle_name].arm = v
        else:
            print(f"Vehicle '{vehicle_name}' not found.")

    def simGetVehiclePose(self, vehicle_name=None):
        name = self.get_vehicle_name(vehicle_name)
        raw_data = self._read_carefully(name, 'pos')
        if raw_data is None or len(raw_data) == 0:
            print(f"ERROR: Failed to read pose data for vehicle '{name}'")
            return None
        pose: Twist = pdu_to_py_Twist(raw_data)
        pos = hakosim_types.Vector3r(pose.linear.x, pose.linear.y, pose.linear.z)
        orientation = hakosim_types.Quaternionr.euler_to_quaternion(pose.angular.x, pose.angular.y, pose.angular.z)
        return hakosim_types.Pose(pos, orientation)

    def simGetVehiclePoseUnityFrame(self, vehicle_name=None):
        name = self.get_vehicle_name(vehicle_name)
        raw_data = self._read_carefully(name, 'pos')
        if raw_data is None or len(raw_data) == 0:
            print(f"ERROR: Failed to read pose data for vehicle '{name}'")
            return None
        pose: Twist = pdu_to_py_Twist(raw_data)
        pos = hakosim_types.Vector3r(
            -pose.linear.y, 
            pose.linear.z, 
            pose.linear.x)
        orientation = hakosim_types.Quaternionr.euler_to_quaternion(
            pose.angular.y, 
            -pose.angular.z, 
            -pose.angular.x)
        return hakosim_types.Pose(pos, orientation)


    def _initialize_header(self, header):
        header.request = 1
        header.result = 0
        header.result_code = 0

    def _reset_header(self, header):
        header.result = 0
        header.result_code = 0

    def _send_request(self, pdu_name: str, py_obj, conv_py_to_pdu):
        raw_data = conv_py_to_pdu(py_obj)
        ret = self.pdu_manager.flush_pdu_raw_data_nowait(self.get_vehicle_name(self.default_drone_name), pdu_name, raw_data)
        if not ret:
            print(f"ERROR: Failed to send request for {pdu_name}")
            return False
        return True

    def _wait_res(self, pdu_name: str, conv_pdu_to_py, conv_py_to_pdu, timeout_sec=-1):
        start_time = time.time()
        while True:
            self.pdu_manager.run_nowait()
            raw_data = self._read_carefully(self.get_vehicle_name(self.default_drone_name), pdu_name)
            if raw_data is None or len(raw_data) == 0:
                print(f"INFO: No data received for {pdu_name}")
                time.sleep(1)
                return False
            #print(f"INFO: Received data for {pdu_name}, length: {len(raw_data)} bytes: {raw_data[:24]}...")  # Print first 24 bytes for debugging
            py_obj = conv_pdu_to_py(raw_data)

            if py_obj.header.result == 1:
                py_obj.header.result = 0
                self.pdu_manager.flush_pdu_raw_data_nowait(self.get_vehicle_name(self.default_drone_name), pdu_name, conv_py_to_pdu(py_obj))
                print('DONE')
                return True

            if timeout_sec >= 0 and time.time() - start_time > timeout_sec:
                print(f"Timeout reached: {timeout_sec} seconds")
                return False

            time.sleep(1)

    def get_vehicle_name(self, vehicle_name):
        if vehicle_name is None:
            return self.default_drone_name
        if vehicle_name in self.vehicles:
            return vehicle_name
        else:
            print(f"Vehicle '{vehicle_name}' not found.")
            return None

    def takeoff(self, height, vehicle_name=None):
        if self.get_vehicle_name(vehicle_name) != None:
            print(f"INFO: takeoff: height={height}")
            pdu_cmd: HakoDroneCmdTakeoff = HakoDroneCmdTakeoff()
            self._initialize_header(pdu_cmd.header)
            pdu_cmd.height = height
            pdu_cmd.speed = 5
            pdu_cmd.yaw_deg = self._get_yaw_degree(vehicle_name)
            if not self._send_request('drone_cmd_takeoff', pdu_cmd, py_to_pdu_HakoDroneCmdTakeoff):
                return False
            print("takeoff request sent")
            # Wait for response
            print("Waiting for takeoff response...")
            return self._wait_res('drone_cmd_takeoff', pdu_to_py_HakoDroneCmdTakeoff, py_to_pdu_HakoDroneCmdTakeoff)
        else:
            return False

    def moveToPositionUnityFrame(self, x, y, z, speed, yaw_deg=None, timeout_sec=-1, vehicle_name=None):
        ros_x = z
        ros_y = -x
        ros_z = y
        if yaw_deg == None:
            ros_yaw_deg = None
        else:
            ros_yaw_deg = -yaw_deg
        self.moveToPosition(ros_x, ros_y, ros_z, speed, ros_yaw_deg, timeout_sec, vehicle_name)

    def moveToPosition(self, x, y, z, speed, yaw_deg=None, timeout_sec=-1, vehicle_name=None):
        if self.get_vehicle_name(vehicle_name) != None:
            print("INFO: moveToPosition")
            pdu_cmd: HakoDroneCmdMove = HakoDroneCmdMove()
            self._initialize_header(pdu_cmd.header)
            pdu_cmd.x = x
            pdu_cmd.y = y
            pdu_cmd.z = z
            pdu_cmd.speed = speed
            if yaw_deg is None:
                yaw_deg = self._get_yaw_degree(vehicle_name)
            pdu_cmd.yaw_deg = yaw_deg
            if not self._send_request('drone_cmd_move', pdu_cmd, py_to_pdu_HakoDroneCmdMove):
                return False
            print("move request sent")            
            # Wait for response
            print("Waiting for move response...")
            return self._wait_res('drone_cmd_move', pdu_to_py_HakoDroneCmdMove, py_to_pdu_HakoDroneCmdMove, timeout_sec)
        else:
            return False

    def land(self, vehicle_name=None):
        if self.get_vehicle_name(vehicle_name) != None:
            print("INFO: Landing")
            py_obj = HakoDroneCmdLand()
            self._initialize_header(py_obj.header)
            py_obj.height = 0
            py_obj.speed = 5
            py_obj.yaw_deg = self._get_yaw_degree(vehicle_name)
            if not self._send_request('drone_cmd_land', py_obj, py_to_pdu_HakoDroneCmdLand):
                return False
            print("land request sent")
            # Wait for response
            print("Waiting for land response...")
            return self._wait_res('drone_cmd_land', pdu_to_py_HakoDroneCmdLand, py_to_pdu_HakoDroneCmdLand)
        else:
            return False


    def wait_grab(self, grab, timeout_sec, vehicle_name):
        start_time = time.time()
        ret = False
        while True:
            raw_data = self._read_carefully(self.get_vehicle_name(vehicle_name), 'hako_status_magnet_holder')
            if raw_data is None or len(raw_data) == 0:
                time.sleep(0.1)
                continue
            pdu_cmd = pdu_to_py_HakoStatusMagnetHolder(raw_data)
            if grab:
                if pdu_cmd.magnet_on == 1 and pdu_cmd.contact_on == 1:
                    ret = True
                    break
            else:
                if pdu_cmd.magnet_on == 0 and pdu_cmd.contact_on == 0:
                    ret = True
                    break

            # タイムアウトチェック (timeout_secが正の値の場合のみ)
            if timeout_sec >= 0 and time.time() - start_time > timeout_sec:
                print(f"Timeout reached: {timeout_sec} seconds")
                break
            
            time.sleep(0.1)
        return ret

    def grab_baggage(self, grab, timeout_sec=-1, vehicle_name=None):
        if self.get_vehicle_name(vehicle_name) != None:
            print("INFO: grab baggage: ", grab)
            pdu_cmd = HakoCmdMagnetHolder()
            self._initialize_header(pdu_cmd.header)
            pdu_cmd.magnet_on = grab
            raw_data = py_to_pdu_HakoCmdMagnetHolder(pdu_cmd)
            ret = self.pdu_manager.flush_pdu_raw_data_nowait(self.get_vehicle_name(vehicle_name), 'hako_cmd_magnet_holder', raw_data)
            if not ret:
                print(f"ERROR: Failed to send grab command for vehicle '{vehicle_name}'")
                return False
            print("grab command sent")
            # Wait for response
            ret = self.wait_grab(grab, timeout_sec, vehicle_name)
            if ret == False:
                pdu_cmd.magnet_on = False

            pdu_cmd.header.request = 0
            pdu_cmd.header.result = 0
            raw_data = py_to_pdu_HakoCmdMagnetHolder(pdu_cmd)
            self.pdu_manager.flush_pdu_raw_data_nowait(self.get_vehicle_name(vehicle_name), 'hako_cmd_magnet_holder', raw_data)
            print("grab command reset")
            return ret
        else:
            return False

    def _get_camera_data(self, vehicle):
        while True:
            raw_data = self._read_carefully(vehicle.name, 'hako_camera_data')
            if raw_data is None or len(raw_data) == 0:
                time.sleep(0.1)
                continue
            try:
                pdu_data = pdu_to_py_HakoCameraData(raw_data)
                if pdu_data.request_id == vehicle.camera_cmd_request_id:
                #print("request_id", pdu_data['request_id'])
                    print(f"INFO: get camera data len={len(pdu_data.image.data)}")
                    return pdu_data.image.data
                else:
                    pass
            except Exception as e:
                print(f"INFO: not written to camera data for vehicle '{vehicle.name}': {e}")
                time.sleep(0.1)
                continue

    def _get_camera_info(self, vehicle):
        print("INFO: get camera info")
        while True:
            raw_data = self._read_carefully(vehicle.name, 'hako_cmd_camera_info')
            if raw_data is None or len(raw_data) == 0:
                print(f"ERROR: Failed to read camera info for vehicle '{vehicle.name}'")
                self.sleep(0.1)
                continue
            try:
                pdu_data = pdu_to_py_HakoCameraInfo(raw_data)
                if pdu_data.request_id == vehicle.camera_move_cmd_request_id:
                    vehicle.camera_move_cmd_request_id += 1
                    return pdu_data.angle
            except Exception as e:
                print(f"INFO: not written to camera info for vehicle '{vehicle.name}': {e}")
                self.sleep(0.1)
                continue

    def _get_yaw_degree(self, vehicle_name=None):
        pose = self.simGetVehiclePose(vehicle_name)
        _, _, yaw = hakosim_types.Quaternionr.quaternion_to_euler(pose.orientation)
        return math.degrees(yaw)

    def simGetImage(self, id, image_type, vehicle_name=None):
        vehicle_name = self.get_vehicle_name(vehicle_name)
        if vehicle_name != None:
            vehicle = self.vehicles[vehicle_name]
            #print("INFO: get image ")
            pdu_cmd = HakoCmdCamera()
            self._initialize_header(pdu_cmd.header)
            pdu_cmd.request_id = vehicle.camera_cmd_request_id
            pdu_cmd.encode_type = 0
            raw_data = py_to_pdu_HakoCmdCamera(pdu_cmd)
            ret = self.pdu_manager.flush_pdu_raw_data_nowait(vehicle.name, 'hako_cmd_camera', raw_data)
            if not ret:
                print(f"ERROR: Failed to send camera command for vehicle '{vehicle_name}'")
                return None
            img = self._get_camera_data(vehicle)
            pdu_cmd.header.request = 0
            pdu_cmd.header.result = 0
            ret = self.pdu_manager.flush_pdu_raw_data_nowait(vehicle.name, 'hako_cmd_camera', py_to_pdu_HakoCmdCamera(pdu_cmd))
            if not ret:
                print(f"ERROR: Failed to reset camera command for vehicle '{vehicle_name}'")
                return None
            vehicle.camera_cmd_request_id = vehicle.camera_cmd_request_id + 1
            return bytes(img)
        else:
            return None

    def simSetCameraOrientation(self, id, degree, vehicle_name=None):
        vehicle_name = self.get_vehicle_name(vehicle_name)
        if vehicle_name != None:
            vehicle = self.vehicles[vehicle_name]
            pdu_cmd = HakoCmdCameraMove()
            self._initialize_header(pdu_cmd.header)
            pdu_cmd.request_id = vehicle.camera_move_cmd_request_id
            pdu_cmd.angle.x = 0
            pdu_cmd.angle.y = degree
            pdu_cmd.angle.z = 0
            ret = self.pdu_manager.flush_pdu_raw_data_nowait(vehicle.name, 'hako_cmd_camera_move', py_to_pdu_HakoCmdCameraMove(pdu_cmd))
            if not ret:
                print(f"ERROR: Failed to send camera move command for vehicle '{vehicle_name}'")
                return None
            print(f"Camera move command sent for vehicle '{vehicle_name}'")
            info = self._get_camera_info(vehicle)
            pdu_cmd.header.request = 0
            pdu_cmd.header.result = 0
            ret = self.pdu_manager.flush_pdu_raw_data_nowait(vehicle.name, 'hako_cmd_camera_move', py_to_pdu_HakoCmdCameraMove(pdu_cmd))
            if not ret:
                print(f"ERROR: Failed to reset camera move command for vehicle '{vehicle_name}'")
                return None
            vehicle.camera_move_cmd_request_id = vehicle.camera_move_cmd_request_id + 1
            return info
        else:
            return None

    def simGetCameraImage(self, id, image_type, vehicle_name=None):
        if vehicle_name != None:
            vehicle = self.vehicles[vehicle_name]
            img = self._get_camera_data(vehicle)
            return bytes(img)
        else:
            return None


    def getLidarData(self, return_point_cloud=False, vehicle_name=None):
        vehicle_name = self.get_vehicle_name(vehicle_name)
        if vehicle_name != None:
            vehicle = self.vehicles[vehicle_name]
            raw_data = self._read_carefully(vehicle.name, 'lidar_points')
            if raw_data is None or len(raw_data) == 0:
                print(f"ERROR: Failed to read Lidar data for vehicle '{vehicle_name}'")
                return None
            lidar_pdu_data = pdu_to_py_PointCloud2(raw_data)
            raw_data = self._read_carefully(vehicle.name, 'lidar_pos')
            if raw_data is None or len(raw_data) == 0:
                print(f"ERROR: Failed to read Lidar pose for vehicle '{vehicle_name}'")
                return None
            lidar_pos_pdu_data = pdu_to_py_Twist(raw_data)
            time_stamp = lidar_pdu_data.header.stamp.sec
            point_cloud_bytes = lidar_pdu_data.data
            height = lidar_pdu_data.height
            row_step = lidar_pdu_data.row_step
            total_data_bytes = height * row_step
            point_cloud = hakosim_lidar.LidarData.extract_xyz_from_point_cloud(point_cloud_bytes, total_data_bytes)
            position = hakosim_types.Vector3r(lidar_pos_pdu_data.linear.x, lidar_pos_pdu_data.linear.y, lidar_pos_pdu_data.linear.z)
            orientation = hakosim_types.Quaternionr.euler_to_quaternion(lidar_pos_pdu_data.angular.x, lidar_pos_pdu_data.angular.y, lidar_pos_pdu_data.angular.z)
            pose = hakosim_types.Pose(position, orientation)
            if return_point_cloud:
                return lidar_pdu_data, pose
            return hakosim_lidar.LidarData(point_cloud, time_stamp, pose)
        else:
            return None

    def getGameJoystickData(self, vehicle_name=None) -> GameControllerOperation:
        vehicle_name = self.get_vehicle_name(vehicle_name)
        if vehicle_name != None:
            vehicle = self.vehicles[vehicle_name]
            raw_data = self._read_carefully(vehicle.name, 'hako_cmd_game')
            if raw_data is None or len(raw_data) == 0:
                print(f"ERROR: Failed to read game joystick data for vehicle '{vehicle_name}'")
                return None
            try:
                game_pdu_data: GameControllerOperation = pdu_to_py_GameControllerOperation(raw_data)
                return game_pdu_data
            except Exception as e:
                print(f"WARNING: Failed to convert PDU to GameControllerOperation for vehicle '{vehicle_name}': {e}")
                return GameControllerOperation()
        else:
            return None

    def putGameJoystickData(self, data: GameControllerOperation, vehicle_name=None):
        vehicle_name = self.get_vehicle_name(vehicle_name)
        if vehicle_name != None:
            vehicle = self.vehicles[vehicle_name]
            ret = self.pdu_manager.flush_pdu_raw_data_nowait(vehicle.name, 'hako_cmd_game', py_to_pdu_GameControllerOperation(data))
            return ret
        else:
            return False
