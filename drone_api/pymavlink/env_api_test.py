#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import time
import math
import sys
import argparse
from pathlib import Path

import hakoniwa_pdu.apps.drone.hakosim as hakosim
from hakoniwa_pdu.pdu_msgs.hako_msgs.pdu_pytype_HakoBatteryStatus import HakoBatteryStatus
from hakoniwa_pdu.pdu_msgs.hako_msgs.pdu_conv_HakoBatteryStatus import pdu_to_py_HakoBatteryStatus
from hakoniwa_pdu.pdu_msgs.hako_msgs.pdu_pytype_DroneStatus import DroneStatus
from hakoniwa_pdu.pdu_msgs.hako_msgs.pdu_conv_DroneStatus import pdu_to_py_DroneStatus
hako_drone_control_disabled_target_yaw_deg = 9999999.0
target_land_z = 0.0

def debug_print_drone_status(client: hakosim.MultirotorClient, drone_name: str) -> int | None:
    try:
        raw = client._read_carefully(drone_name, "status")
        status: DroneStatus = pdu_to_py_DroneStatus(raw)
        print(f"Drone Status - Collided_counts: {status.collided_counts}, Flight_mode: {status.flight_mode}, Internal_state: {status.internal_state}, Propeller_wind: ({status.propeller_wind.x}, {status.propeller_wind.y}, {status.propeller_wind.z})")
        sys.stdout.flush()
        return status.collided_counts
    except Exception as e:
        print(f"Warning: failed to read drone status: {e}")
        sys.stdout.flush()

def debug_print_battery_status(client: hakosim.MultirotorClient, drone_name: str) -> None:
    try:
        raw = client._read_carefully(drone_name, "battery")
        batt: HakoBatteryStatus = pdu_to_py_HakoBatteryStatus(raw)
        print(f"Battery Status - Curr_voltage: {batt.curr_voltage} V, full_voltage: {batt.full_voltage} V, Temp: {batt.curr_temp} C")
        sys.stdout.flush()
        return batt.curr_voltage
    except Exception as e:
        print(f"Warning: failed to read battery status: {e}")
        sys.stdout.flush()


def execute_mission(client: hakosim.MultirotorClient, mission_data: dict) -> bool:
    print("--- Starting mission from JSON ---")
    sys.stdout.flush()
    start_time = time.time()
    client.enableApiControl(True)
    time.sleep(1)
    initial_collided_counts = 0
    total_collided_counts = 0
    initial_batt_voltage = 0
    costed_batt_voltage = 0

    client.armDisarm(True)
    time.sleep(1)

    for i, command_item in enumerate(mission_data.get('mission', [])):
        command_type = command_item.get('command')
        parameters = command_item.get('parameters', {})
        print(f"Executing command {i+1}: {command_type} with parameters {parameters}")
        sys.stdout.flush()

        if command_type == 'takeoff':
            pose = client.simGetVehiclePose(client.default_drone_name)
            target_land_z = pose.position.z_val if pose else 0.0
            height = parameters.get('height', 10.0) # Default height if not specified
            timeout_sec = parameters.get('timeout_sec', 6000)
            if not client.takeoff(height):
                print(f"Takeoff failed at command {i+1}.")
                sys.stdout.flush()
                return False
            print("Takeoff successful. target_land_z set to {:.2f}".format(target_land_z))
            initial_collided_counts = debug_print_drone_status(client, client.default_drone_name)
            initial_batt_voltage = debug_print_battery_status(client, client.default_drone_name)
            time.sleep(5)
            sys.stdout.flush()
        elif command_type == 'moveToPosition':
            x = parameters.get('x')
            y = parameters.get('y')
            z = parameters.get('z')
            speed = parameters.get('speed', 1.0) # Default speed if not specified
            timeout_sec = parameters.get('timeout_sec', 6000)

            if x is None or y is None or z is None:
                print(f"Error: x, y, z must be specified for moveToPosition at command {i+1}.")
                sys.stdout.flush()
                return False

            move_args = {
                'x': x,
                'y': y,
                'z': z,
                'speed': speed,
                'timeout_sec': timeout_sec
            }

            # Calculate yaw to face the target, assuming ENU coordinate system and PX4 conventions (0=North, clockwise)
            pose = client.simGetVehiclePose(client.default_drone_name)
            if pose:
                current_pos = pose.position
                move_args['yaw_deg'] = hako_drone_control_disabled_target_yaw_deg
                print(f"Current Pos: ({current_pos.x_val:.2f}, {current_pos.y_val:.2f}), Target: ({x}, {y})")
                debug_print_drone_status(client, client.default_drone_name)
                debug_print_battery_status(client, client.default_drone_name)
                sys.stdout.flush()
            else:
                print("Warning: Could not get current pose to calculate yaw. Proceeding without yaw.")
                sys.stdout.flush()
            time.sleep(2)

            if not client.moveToPosition(**move_args):
                print(f"moveToPosition failed at command {i+1}.")
                sys.stdout.flush()
                return False
            print("Move successful.")
            sys.stdout.flush()
        elif command_type == 'land':
            pose = client.simGetVehiclePose(client.default_drone_name)
            last_x = pose.position.x_val if pose else 0.0
            last_y = pose.position.y_val if pose else 0.0
            print(f"Landing at x: {last_x} y: {last_y} target z: {target_land_z}")
            counts = debug_print_drone_status(client, client.default_drone_name)
            curr_voltage = debug_print_battery_status(client, client.default_drone_name)
            total_collided_counts = counts - initial_collided_counts
            costed_batt_voltage = initial_batt_voltage - curr_voltage
            if not client.moveToPosition(x=last_x, y=last_y, z=target_land_z, speed=1.0, yaw_deg=hako_drone_control_disabled_target_yaw_deg):
                print(f"Landing failed at command {i+1}.")
                sys.stdout.flush()
                return False
            elapsed = time.time() - start_time
            print(f"Landed successfully. Total collided counts: {total_collided_counts}")
            print(f"end=Battery voltage used: {costed_batt_voltage:.2f} V")
            print(f"Elapsed time: {elapsed:.2f} seconds.")
            sys.stdout.flush()
        elif command_type == 'sleep':
            duration_sec = parameters.get('duration_sec', 1.0)
            print(f"Sleeping for {duration_sec} seconds.")
            sys.stdout.flush()
            time.sleep(duration_sec)
        else:
            print(f"Unknown command: {command_type} at command {i+1}.")
            return False
        time.sleep(1) # Small delay between commands for stability

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Control a MAVLink drone.",
        allow_abbrev=False
    )
    parser.add_argument('--name', type=str, default='Drone', help='Name of the drone.')
    parser.add_argument('--config-path', type=str, default=None,
                        help='Path to the vehicle configuration file for Hakoniwa sensor PDU (e.g., config/pdudef/webavatar.json).')
    parser.add_argument('--mission-file', type=str, default=None,
                        help='Path to a JSON file defining the mission (e.g., mission.json).')
    args = parser.parse_args()
    # check args
    if not args.config_path:
        print("Error: --config-path is required.")
        return 1
    if not args.mission_file:
        print("Error: --mission-file is required.")
        return 1

    print(f"--- Starting drone mission for '{args.name}' ---")
    #flush print
    sys.stdout.flush()
    # --- Hakoniwa sensor client (optional) ---
    client = hakosim.MultirotorClient(args.config_path, args.name)
    if not client.confirmConnection():
        print("Failed to connect to vehicle(s).")
        return 1

    debug_print_drone_status(client, args.name)
    # --- Mission run ---
    batt_init = None
    try:
        if client:
            raw = client._read_carefully(args.name, "battery")
            batt: HakoBatteryStatus = pdu_to_py_HakoBatteryStatus(raw)
            batt_init = batt.curr_voltage
            print(f"Last Battery Status: {batt_init} V")
    except Exception as e:
        print(f"Warning: failed to read last battery status: {e}")

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
            raise ValueError("No mission file specified.")

        if ok:
            pass
            print("Mission completed successfully.")             
        else:
            print("Mission failed.")

        if batt_init is not None and client:
            try:
                raw = client._read_carefully(args.name, "battery")
                batt: HakoBatteryStatus = pdu_to_py_HakoBatteryStatus(raw)
                batt_curr = batt.curr_voltage
                print(f"Last Battery Status: {batt_curr} V")
                print(f"Battery used: {batt_init - batt_curr} V")
            except Exception as e:
                print(f"Warning: failed to read last battery status: {e}")

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
        print("Cleanup complete.")

        while True:
            time.sleep(1)


if __name__ == "__main__":
    raise SystemExit(main())
