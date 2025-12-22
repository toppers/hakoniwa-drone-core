#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import time
import math
import argparse
from pathlib import Path

import hakoniwa_pdu.apps.drone.hakosim as hakosim
from hakosim_mavlink import MavlinkMultirotorClient
from hakoniwa_pdu.pdu_msgs.hako_msgs.pdu_pytype_HakoBatteryStatus import HakoBatteryStatus
from hakoniwa_pdu.pdu_msgs.hako_msgs.pdu_conv_HakoBatteryStatus import pdu_to_py_HakoBatteryStatus


def _run_hardcoded_mission(client: MavlinkMultirotorClient) -> bool:
    print("--- Starting hardcoded mission ---")
    client.enableApiControl(True)
    time.sleep(1)

    if client.vehicles[client.default_drone_name].is_ardupilot():
        client.wait_ardupilot_ekf_using_gps(timeout=60.0)

    client.armDisarm(True)
    time.sleep(1)
    if client.takeoff(20.0, timeout_sec=6000):
        print("Takeoff successful.")
        time.sleep(5)

        if client.moveToPosition(100.0, 0.0, 20.0, speed=20.0, yaw_deg=0, timeout_sec=6000):
            print("Move 1 successful.")
            time.sleep(2)

            if client.moveToPosition(100.0, -100.0, 20.0, speed=20.0, yaw_deg=-90, timeout_sec=6000):
                print("Move 2 successful.")
                time.sleep(2)

                if client.moveToPosition(0.0, 0.0, 20.0, speed=20.0, yaw_deg=-45, timeout_sec=6000):
                    print("Move 3 successful.")
                    time.sleep(2)
                    return True
    return False


def execute_mission(client: MavlinkMultirotorClient, mission_data: dict) -> bool:
    print("--- Starting mission from JSON ---")
    client.enableApiControl(True)
    time.sleep(1)

    if client.vehicles[client.default_drone_name].is_ardupilot():
        client.wait_ardupilot_ekf_using_gps(timeout=60.0)

    client.armDisarm(True)
    time.sleep(1)

    for i, command_item in enumerate(mission_data.get('mission', [])):
        command_type = command_item.get('command')
        parameters = command_item.get('parameters', {})
        print(f"Executing command {i+1}: {command_type} with parameters {parameters}")

        if command_type == 'takeoff':
            height = parameters.get('height', 10.0) # Default height if not specified
            timeout_sec = parameters.get('timeout_sec', 6000)
            if not client.takeoff(height, timeout_sec=timeout_sec):
                print(f"Takeoff failed at command {i+1}.")
                return False
            print("Takeoff successful.")
        elif command_type == 'moveToPosition':
            x = parameters.get('x')
            y = parameters.get('y')
            z = parameters.get('z')
            speed = parameters.get('speed', 20.0) # Default speed if not specified
            timeout_sec = parameters.get('timeout_sec', 6000)

            if x is None or y is None or z is None:
                print(f"Error: x, y, z must be specified for moveToPosition at command {i+1}.")
                return False

            move_args = {
                'x': x,
                'y': y,
                'z': z,
                'speed': speed,
                'timeout_sec': timeout_sec
            }
            if 'yaw_deg' in parameters:
                move_args['yaw_deg'] = parameters['yaw_deg']
                print("Using specified yaw.")
            else:
                # Calculate yaw to face the target, assuming ENU coordinate system and PX4 conventions (0=North, clockwise)
                print("Calculating yaw to face target...")
                pose = client.simGetVehiclePose(client.default_drone_name)
                if pose:
                    current_pos = pose.position
                    dy = y - current_pos.y_val
                    dx = x - current_pos.x_val
                    # Convert angle from X-axis (East) to Y-axis (North) and clockwise
                    yaw_rad = math.atan2(dy, dx)
                    yaw_deg = 90.0 - math.degrees(yaw_rad)
                    # Normalize angle to -180 to 180
                    if yaw_deg > 180:
                        yaw_deg = yaw_deg - 360
                    elif yaw_deg < -180:
                        yaw_deg = yaw_deg + 360
                    move_args['yaw_deg'] = yaw_deg
                    print(f"Current Pos: ({current_pos.x_val:.2f}, {current_pos.y_val:.2f}), Target: ({x}, {y}), Calculated Yaw: {yaw_deg:.2f} degrees")
                else:
                    print("Warning: Could not get current pose to calculate yaw. Proceeding without yaw.")

            if not client.moveToPosition(move_args['x'], move_args['y'], move_args['z'],
                                         speed=move_args['speed'],
                                         yaw_deg=move_args.get('yaw_deg', 0),
                                         timeout_sec=move_args['timeout_sec']):
                print(f"moveToPosition failed at command {i+1}.")
                return False
            print("Move successful.")
        elif command_type == 'land':
            if not client.land():
                print(f"Landing failed at command {i+1}.")
                return False
            print("Landed successfully.")
        elif command_type == 'sleep':
            duration_sec = parameters.get('duration_sec', 1.0)
            print(f"Sleeping for {duration_sec} seconds.")
            time.sleep(duration_sec)
        else:
            print(f"Unknown command: {command_type} at command {i+1}.")
            return False

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Control a MAVLink drone.",
        allow_abbrev=False
    )
    parser.add_argument('--name', type=str, default='Drone', help='Name of the drone.')
    parser.add_argument('--connect', type=str, required=True,
                        help='Connection string (e.g., udp:127.0.0.1:14540).')
    parser.add_argument('--type', type=str, default='px4', choices=['px4', 'ardupilot'],
                        help='Vehicle type (px4 or ardupilot).')
    parser.add_argument('--config-path', type=str, default=None,
                        help='Path to the vehicle configuration file for Hakoniwa sensor PDU (e.g., config/pdudef/webavatar.json).')
    parser.add_argument('--idle', action='store_true',
                        help='Keep process running after landing until Ctrl+C.')
    parser.add_argument('--mission-file', type=str, default=None,
                        help='Path to a JSON file defining the mission (e.g., mission.json).')
    args = parser.parse_args()

    time.sleep(10)  # Wait for Hakoniwa environment to be ready

    # --- Hakoniwa sensor client (optional) ---
    sensor_client = None
    if args.config_path:
        cfg_path = Path(args.config_path)
        if not cfg_path.exists():
            raise FileNotFoundError(f"Config not found: {cfg_path}")
        sensor_client = hakosim.MultirotorClient(args.config_path, args.name)

    # --- Mavlink client ---
    client = MavlinkMultirotorClient(default_drone_name=args.name, sensor_client=sensor_client)
    print(f"Adding vehicle: {args.name} ({args.type}) with connection: {args.connect}")
    client.add_vehicle(args.name, args.connect, args.type)

    if not client.confirmConnection():
        print("Failed to connect to vehicle(s).")
        return 1

    # --- Mission run ---
    batt_init = None
    try:
        if sensor_client:
            raw = sensor_client._read_carefully(args.name, "battery")
            batt: HakoBatteryStatus = pdu_to_py_HakoBatteryStatus(raw)
            batt_init = batt.curr_voltage
            print(f"Last Battery Status: {batt_init} V")
    except Exception as e:
        print(f"Warning: failed to read last battery status: {e}")

    start_time = time.time()
    ok = False
    try:
        if args.mission_file:
            mission_file_path = Path(args.mission_file)
            if not mission_file_path.exists():
                raise FileNotFoundError(f"Mission file not found: {mission_file_path}")
            with open(mission_file_path, 'r') as f:
                mission_data = json.load(f)
            ok = execute_mission(client, mission_data)
        else:
            ok = _run_hardcoded_mission(client)

        elapsed = time.time() - start_time
        if ok:
            print(f"Mission completed successfully in {elapsed:.2f} seconds.")
        else:
            print("Mission failed.")

        if batt_init is not None and sensor_client:
            try:
                raw = sensor_client._read_carefully(args.name, "battery")
                batt: HakoBatteryStatus = pdu_to_py_HakoBatteryStatus(raw)
                batt_curr = batt.curr_voltage
                print(f"Last Battery Status: {batt_curr} V")
                print(f"Battery used: {batt_init - batt_curr} V")
            except Exception as e:
                print(f"Warning: failed to read last battery status: {e}")

        # 待機オプション
        if args.idle:
            print("Idling... Press Ctrl+C to exit.")
            while True:
                time.sleep(5)
        return 0
    except KeyboardInterrupt:
        print("Interrupted by user.")
        return 130
    finally:
        print("--- Cleaning up ---")
        try:
            client.armDisarm(False)
        except Exception:
            pass
        client.disconnect_all()
        print("Cleanup complete.")


if __name__ == "__main__":
    raise SystemExit(main())
