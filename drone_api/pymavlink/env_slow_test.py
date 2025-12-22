#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import argparse
from pathlib import Path
from xmlrpc import client

import hakoniwa_pdu.apps.drone.hakosim as hakosim
from hakosim_mavlink import MavlinkMultirotorClient
from hakoniwa_pdu.pdu_msgs.hako_msgs.pdu_pytype_HakoBatteryStatus import HakoBatteryStatus
from hakoniwa_pdu.pdu_msgs.hako_msgs.pdu_conv_HakoBatteryStatus import pdu_to_py_HakoBatteryStatus


def run_mission(client: MavlinkMultirotorClient) -> bool:
    print("--- Starting mission ---")
    client.enableApiControl(True)
    time.sleep(1)

    hb = client.get_heartbeat()
    if hb:
        print(
            f"BEFORE Heartbeat received: "
            f"type={hb.type}, autopilot={hb.autopilot}, base_mode={hb.base_mode}, "
            f"system_status={hb.system_status}, custom_mode={hb.custom_mode}"
        )
    else:
        print("No heartbeat received.")

    if client.vehicles[client.default_drone_name].is_ardupilot():
        client.wait_ardupilot_ekf_using_gps(timeout=60.0)

    client.armDisarm(True)
    time.sleep(1)
    if client.takeoff(10.0, timeout_sec=6000):
        print("Takeoff successful.")
        time.sleep(5)

        hb = client.get_heartbeat()
        if hb:
            print(
                f"AFTER Heartbeat received: "
                f"type={hb.type}, autopilot={hb.autopilot}, base_mode={hb.base_mode}, "
                f"system_status={hb.system_status}, custom_mode={hb.custom_mode}"
            )
        else:
            print("No heartbeat received.")


        if client.moveToPosition(400.0, 400.0, 10.0, 0.1, yaw_deg=180, timeout_sec=6000):
            print("Move 1 successful.")
            time.sleep(5)

            if client.moveToPosition(400.0, 0.0, 10.0, 0.1, yaw_deg=-90, timeout_sec=6000):
                print("Move 2 successful.")
                time.sleep(5)

                if client.moveToPosition(0.0, 0.0, 10.0, 0.1, yaw_deg=45, timeout_sec=6000):
                    print("Move 3 successful.")
                    time.sleep(5)
                    return True
    return False


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
    args = parser.parse_args()

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
    try:
        raw = sensor_client._read_carefully(args.name, "battery")
        batt: HakoBatteryStatus = pdu_to_py_HakoBatteryStatus(raw)
        batt_init = batt.curr_voltage
        print(f"Last Battery Status: {batt_init} V")
    except Exception as e:
        print(f"Warning: failed to read last battery status: {e}")

    start_time = time.time()
    try:
        ok = run_mission(client)
        elapsed = time.time() - start_time
        if ok:
            print(f"Mission completed successfully in {elapsed:.2f} seconds.")
        else:
            print("Mission failed.")


        try:
            raw = sensor_client._read_carefully(args.name, "battery")
            batt: HakoBatteryStatus = pdu_to_py_HakoBatteryStatus(raw)
            batt = batt.curr_voltage
            print(f"Last Battery Status: {batt} V")
            print(f"Battery used: {batt_init - batt} V")
        except Exception as e:
            print(f"Warning: failed to read last battery status: {e}")


        # 着陸
        client.land()
        print("Landed successfully.")
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
