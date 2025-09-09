#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import abc
import time
import math
import threading
from pymavlink import mavutil
from typing import Any, Callable

# PX4 OFFBOARDモードで目標値を送り続ける頻度
PX4_KEEPALIVE_HZ = 10.0

class AbstractFlightController(abc.ABC):
    """
    フライトスタック(ArduPilot/PX4)ごとのMAVLink通信の違いを吸収するインターフェース。
    """
    def __init__(self):
        self.mav_conn = None
        self.target_system = None
        self.target_component = None

    def init_connection(self, mav_conn: mavutil.mavlink_connection):
        self.mav_conn = mav_conn
        self.target_system = mav_conn.target_system
        self._initialize()

    def _param_id_to_str(self, pid):
        if isinstance(pid, (bytes, bytearray)):
            pid = pid.decode("utf-8", errors="ignore")
        return pid.strip("\x00")

    def _wait_for_message(self, msg_type: str, condition: Callable[[Any], bool], timeout: float):
        t0 = time.time()
        while time.time() - t0 < timeout:
            msg = self.mav_conn.recv_match(type=msg_type, blocking=True, timeout=1)
            if msg and condition(msg):
                return msg
        return None

    def _wait_for_command_ack(self, command: int, timeout: float = 5.0):
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

    @abc.abstractmethod
    def _initialize(self):
        pass

    @abc.abstractmethod
    def set_api_mode(self) -> bool:
        pass

    @abc.abstractmethod
    def arm(self) -> bool:
        pass

    @abc.abstractmethod
    def disarm(self) -> bool:
        pass

    @abc.abstractmethod
    def takeoff(self, height_m: float) -> bool:
        pass

    @abc.abstractmethod
    def land(self) -> bool:
        pass

    @abc.abstractmethod
    def go_to_local_ned(self, x: float, y: float, z: float, yaw_deg: float):
        pass

    @abc.abstractmethod
    def stop_movement(self):
        pass

class ArduPilotController(AbstractFlightController):
    """ArduPilot用のフライトコントローラ実装"""

    def _initialize(self):
        self.target_component = self.mav_conn.target_component
        print("=== [ArduPilot] Setting Parameters ===")
        self._set_param("ARMING_CHECK", 0)
        self._set_param("SIM_SPEEDUP", 1, mavutil.mavlink.MAV_PARAM_TYPE_REAL32)
        self._set_param("GPS_TYPE", 1, mavutil.mavlink.MAV_PARAM_TYPE_INT8)
        self._set_param("EK3_ENABLE", 1, mavutil.mavlink.MAV_PARAM_TYPE_INT8)
        self._set_param("AHRS_EKF_TYPE", 3, mavutil.mavlink.MAV_PARAM_TYPE_INT8)
        self._set_param("BATT_MONITOR", 4, mavutil.mavlink.MAV_PARAM_TYPE_INT8)
        self._set_param("FS_BATT_ENABLE", 0, mavutil.mavlink.MAV_PARAM_TYPE_INT8)
        time.sleep(1.0)

    def _set_param(self, name: str, value, ptype=mavutil.mavlink.MAV_PARAM_TYPE_INT32, timeout=3):
        self.mav_conn.mav.param_set_send(
            self.target_system, self.target_component,
            name.encode("utf-8"), float(value), ptype
        )
        msg = self._wait_for_message(
            "PARAM_VALUE",
            lambda m: self._param_id_to_str(m.param_id) == name,
            timeout
        )
        if msg:
            print(f"[ArduPilot] {name} = {msg.param_value}")
            return True
        print(f"⚠ [ArduPilot] PARAM echo timeout: {name}")
        return False

    def set_api_mode(self) -> bool:
        print("=== [ArduPilot] Setting Mode to GUIDED ===")
        self.mav_conn.set_mode_apm("GUIDED")
        hb = self._wait_for_message("HEARTBEAT", lambda m: m.custom_mode == 4, timeout=8) # GUIDED is 4
        if hb:
            print("[ArduPilot] Mode set to GUIDED")
            return True
        print("⚠ [ArduPilot] Failed to set mode to GUIDED")
        return False

    def arm(self) -> bool:
        if self._is_armed():
            print("✓ [ArduPilot] Already armed")
            return True

        print("=== [ArduPilot] Pre-flight checks... ===")
        if not self.wait_gps_fix(min_fix=2, min_sats=5, timeout=15):
            print("⚠ [ArduPilot] GPS not ready, but continuing...")

        if not self.wait_origin(timeout=15):
            print("⚠ [ArduPilot] Origin not confirmed, but continuing...")
            self.set_home_manually()

        print("=== [ArduPilot] Setting mode for arming... ===")
        self.mav_conn.set_mode_apm("STABILIZE")
        time.sleep(1)
        self.set_api_mode() # Set GUIDED

        return self._arm_and_verify()

    def _arm_and_verify(self) -> bool:
        print("=== [ArduPilot] Attempting to ARM ===")
        # Attempt 1: Basic ARM
        self.mav_conn.mav.command_long_send(
            self.target_system, self.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
            1, 0, 0, 0, 0, 0, 0
        )
        self._wait_for_command_ack(mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, timeout=3)
        time.sleep(1)
        if self._is_armed():
            print("✓ [ArduPilot] Successfully ARMED!")
            return True

        # Attempt 2: Force ARM (magic number)
        print("[ArduPilot] ARM attempt 2: Force ARM")
        self.mav_conn.mav.command_long_send(
            self.target_system, self.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
            1, 21196, 0, 0, 0, 0, 0
        )
        self._wait_for_command_ack(mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, timeout=3)
        time.sleep(1)
        if self._is_armed():
            print("✓ [ArduPilot] Successfully ARMED!")
            return True

        print("✗ [ArduPilot] ARM failed after all attempts.")
        return False

    def _is_armed(self, timeout=2) -> bool:
        hb = self._wait_for_message("HEARTBEAT", lambda m: True, timeout)
        return bool(hb.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED) if hb else False

    def disarm(self) -> bool:
        print("=== [ArduPilot] Attempting to DISARM ===")
        self.mav_conn.mav.command_long_send(
            self.target_system, self.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
            0, 0, 0, 0, 0, 0, 0
        )
        ack = self._wait_for_command_ack(mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM)
        return ack and ack.result == mavutil.mavlink.MAV_RESULT_ACCEPTED

    def takeoff(self, height_m: float) -> bool:
        print(f"=== [ArduPilot] Takeoff to {abs(height_m)}m (ROS frame) ===")
        self.mav_conn.mav.command_long_send(
            self.target_system, self.target_component,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0,
            0, 0, 0, 0, 0, 0, -height_m
        )
        ack = self._wait_for_command_ack(mavutil.mavlink.MAV_CMD_NAV_TAKEOFF)
        return ack and ack.result == mavutil.mavlink.MAV_RESULT_ACCEPTED

    def land(self) -> bool:
        print("=== [ArduPilot] Landing ===")
        self.mav_conn.mav.command_long_send(
            self.target_system, self.target_component,
            mavutil.mavlink.MAV_CMD_NAV_LAND, 0,
            0, 0, 0, 0, 0, 0, 0
        )
        ack = self._wait_for_command_ack(mavutil.mavlink.MAV_CMD_NAV_LAND)
        return ack and ack.result == mavutil.mavlink.MAV_RESULT_ACCEPTED

    def go_to_local_ned(self, x: float, y: float, z: float, yaw_deg: float):
        TYPE_MASK_POS_YAW = 0x09F8
        self.mav_conn.mav.set_position_target_local_ned_send(
            0, self.target_system, self.target_component,
            mavutil.mavlink.MAV_FRAME_LOCAL_NED,
            TYPE_MASK_POS_YAW, 
            float(x), float(y), float(z),
            0, 0, 0, 0, 0, 0,
            math.radians(float(yaw_deg)), 0
        )

    def stop_movement(self):
        pass # Not needed for ArduPilot

    # --- Helper methods for pre-arm checks ---
    def wait_gps_fix(self, min_fix=3, min_sats=6, timeout=30) -> bool:
        print("[ArduPilot] Waiting for GPS fix...")
        condition = lambda g: g.fix_type >= min_fix and g.satellites_visible >= min_sats
        initial_msg = self.mav_conn.recv_match(type="GPS_RAW_INT", blocking=True, timeout=1)
        if initial_msg:
            print(f"GPS status: fix={initial_msg.fix_type}, sats={initial_msg.satellites_visible}")
            if condition(initial_msg): return True
        g = self._wait_for_message("GPS_RAW_INT", condition, timeout - 1)
        return g is not None

    def wait_origin(self, timeout=30) -> bool:
        print("[ArduPilot] Waiting for HOME/Origin to be set...")
        t0 = time.time()
        last_req = 0.0
        while time.time() - t0 < timeout:
            if time.time() - last_req > 3.0:
                self.mav_conn.mav.command_long_send(
                    self.target_system, self.target_component,
                    mavutil.mavlink.MAV_CMD_GET_HOME_POSITION, 0, 0,0,0,0,0,0,0)
                last_req = time.time()
            msg = self.mav_conn.recv_match(type=["HOME_POSITION", "GPS_GLOBAL_ORIGIN"], blocking=True, timeout=1)
            if msg: return True
        return False

    def set_home_manually(self):
        print("[ArduPilot] Trying to set HOME manually...")
        self.mav_conn.mav.command_long_send(
            self.target_system, self.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_HOME, 0, 1, 0,0,0,0,0,0)

class PX4Controller(AbstractFlightController):
    """PX4用のフライトコントローラ実装"""

    def __init__(self):
        super().__init__()
        self._streaming_thread = None
        self._stop_event = threading.Event()
        self._target_pos = (0, 0, 0)
        self._target_yaw_deg = 0

    def _initialize(self):
        self.target_component = 1 # PX4 Autopilot is typically component 1
        print("=== [PX4] Initialized ===")
        time.sleep(1.0)

    def set_api_mode(self) -> bool:
        print("=== [PX4] Setting Mode to OFFBOARD ===")
        print("[PX4] Sending initial setpoints before switching...")
        self.go_to_local_ned(0, 0, 0, 0) # Start streaming with a dummy setpoint
        time.sleep(0.5)

        PX4_CUSTOM_MAIN_MODE_OFFBOARD = 6
        self.mav_conn.mav.command_long_send(
            self.target_system, self.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            PX4_CUSTOM_MAIN_MODE_OFFBOARD, 0, 0, 0, 0, 0
        )
        ack = self._wait_for_command_ack(mavutil.mavlink.MAV_CMD_DO_SET_MODE, timeout=3)
        if ack and ack.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
            print("[PX4] Mode set to OFFBOARD")
            return True
        
        print("⚠ [PX4] Failed to set mode to OFFBOARD")
        self.stop_movement()
        return False

    def arm(self) -> bool:
        print("=== [PX4] Attempting to ARM ===")
        self.mav_conn.mav.command_long_send(
            self.target_system, self.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0
        )
        ack = self._wait_for_command_ack(mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, timeout=3)
        if ack and ack.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
            print("✓ [PX4] Successfully ARMED!")
            return True
        print("⚠ [PX4] ARM failed")
        return False

    def disarm(self) -> bool:
        print("=== [PX4] Attempting to DISARM ===")
        self.stop_movement()
        self.mav_conn.mav.command_long_send(
            self.target_system, self.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 0, 0, 0, 0, 0, 0, 0
        )
        ack = self._wait_for_command_ack(mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, timeout=3)
        return ack and ack.result == mavutil.mavlink.MAV_RESULT_ACCEPTED

    def takeoff(self, height_m: float) -> bool:
        print(f"=== [PX4] Takeoff to {abs(height_m)}m (ROS frame) ===")
        self.go_to_local_ned(0, 0, height_m, 0)
        return True

    def land(self) -> bool:
        print("=== [PX4] Landing ===")
        self.stop_movement()
        self.mav_conn.mav.command_long_send(
            self.target_system, self.target_component,
            mavutil.mavlink.MAV_CMD_NAV_LAND, 0, 0, 0, 0, 0, 0, 0, 0
        )
        ack = self._wait_for_command_ack(mavutil.mavlink.MAV_CMD_NAV_LAND)
        return ack and ack.result == mavutil.mavlink.MAV_RESULT_ACCEPTED

    def go_to_local_ned(self, x: float, y: float, z: float, yaw_deg: float):
        self._target_pos = (x, y, z)
        self._target_yaw_deg = yaw_deg
        
        if self._streaming_thread is None or not self._streaming_thread.is_alive():
            self._stop_event.clear()
            self._streaming_thread = threading.Thread(target=self._stream_setpoints, daemon=True)
            self._streaming_thread.start()
            print("[PX4] Setpoint streaming started.")

    def stop_movement(self):
        if self._streaming_thread and self._streaming_thread.is_alive():
            self._stop_event.set()
            self._streaming_thread.join(timeout=1.0)
            print("[PX4] Setpoint streaming stopped.")
        self._streaming_thread = None

    def _stream_setpoints(self):
        MASK_POS_YAW = 0x09F8
        dt = 1.0 / PX4_KEEPALIVE_HZ
        
        while not self._stop_event.is_set():
            x, y, z = self._target_pos
            yaw_deg = self._target_yaw_deg
            
            self.mav_conn.mav.set_position_target_local_ned_send(
                0, # time_boot_ms (0 for now)
                self.target_system, self.target_component,
                mavutil.mavlink.MAV_FRAME_LOCAL_NED,
                MASK_POS_YAW,
                float(x), float(y), float(z),
                0, 0, 0, 0, 0, 0,
                math.radians(float(yaw_deg)), 0
            )
            time.sleep(dt)
