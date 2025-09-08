#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import math
import argparse
from contextlib import suppress
from pymavlink import mavutil

KEEPALIVE_HZ = 10.0
ALT = 5.0
YAW0 = 0.0

# 正しい type_mask（forceビット=0）
MASK_POS_YAW = 0x09F8  # 位置+Yawのみ有効（vel/accel/yaw_rate無効, force無効）
MASK_VEL_YAW = 0x01C7  # 速度+Yawのみ有効（pos/accel/yaw_rate無効, force無効）

def connect(conn_str: str):
    print(f"[INFO] Connecting: {conn_str}")
    m = mavutil.mavlink_connection(conn_str, source_system=255, source_component=190)
    m.wait_heartbeat()
    print(f"[INFO] Heartbeat from sys {m.target_system} comp {m.target_component}")
    # PX4のAUTOPILOTは comp=1
    m.target_component = 1
    return m

def arm(m, enable=True):
    m.mav.command_long_send(
        m.target_system, m.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
        1 if enable else 0, 0,0,0, 0,0,0
    )
    with suppress(Exception):
        m.recv_match(type='COMMAND_ACK', blocking=False, timeout=0.5)

def set_mode_offboard(m):
    PX4_CUSTOM_MAIN_MODE_OFFBOARD = 6
    m.mav.command_long_send(
        m.target_system, m.target_component,
        mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        PX4_CUSTOM_MAIN_MODE_OFFBOARD,
        0,0,0,0,0
    )
    with suppress(Exception):
        m.recv_match(type='COMMAND_ACK', blocking=False, timeout=0.5)

def _time_boot_ms(t0: float) -> int:
    return int((time.time() - t0) * 1000) & 0xFFFFFFFF

def send_pos_ned(m, t0, x, y, z, yaw_deg):
    """位置(x,y,z)+yaw のみ有効（forceビットは降ろす）"""
    m.mav.set_position_target_local_ned_send(
        _time_boot_ms(t0),
        m.target_system, m.target_component,
        mavutil.mavlink.MAV_FRAME_LOCAL_NED,
        MASK_POS_YAW,                # ← 修正
        float(x), float(y), float(z),
        0.0, 0.0, 0.0,               # vx,vy,vz 無効
        0.0, 0.0, 0.0,               # ax,ay,az 無効（forceフラグもオフ）
        math.radians(float(yaw_deg)),
        0.0                          # yaw_rate 無効
    )

def send_vel_ned(m, t0, vx, vy, vz, yaw_deg):
    """速度(vx,vy,vz)+yaw のみ有効（上昇は vz<0）"""
    m.mav.set_position_target_local_ned_send(
        _time_boot_ms(t0),
        m.target_system, m.target_component,
        mavutil.mavlink.MAV_FRAME_LOCAL_NED,
        MASK_VEL_YAW,                # ← 修正
        0.0, 0.0, 0.0,               # 位置 無効
        float(vx), float(vy), float(vz),
        0.0, 0.0, 0.0,               # 加速度 無効（forceフラグもオフ）
        math.radians(float(yaw_deg)),
        0.0
    )

def hold_pos(m, t0, x, y, z, yaw_deg, seconds, hz=KEEPALIVE_HZ):
    dt = max(0.001, 1.0 / hz)
    for _ in range(max(1, int(seconds * hz))):
        send_pos_ned(m, t0, x, y, z, yaw_deg)
        time.sleep(dt)

def hold_vel(m, t0, vx, vy, vz, yaw_deg, seconds, hz=KEEPALIVE_HZ):
    dt = max(0.001, 1.0 / hz)
    for _ in range(max(1, int(seconds * hz))):
        send_vel_ned(m, t0, vx, vy, vz, yaw_deg)
        time.sleep(dt)

def land(m):
    m.mav.command_long_send(
        m.target_system, m.target_component,
        mavutil.mavlink.MAV_CMD_NAV_LAND, 0,
        0,0,0,0, 0,0, 0
    )
    print("[INFO] LAND command sent")

def main():
    parser = argparse.ArgumentParser(description="PX4 single-vehicle offboard (pymavlink)")
    parser.add_argument("--udp", default="udp:127.0.0.1:14541",
                        help="Connection string (e.g., udp:127.0.0.1:14541)")
    args = parser.parse_args()

    m = connect(args.udp)
    t0 = time.time()

    # 1) ARM
    arm(m, True)

    # 2) OFFBOARD前に“軽く上方向”の位置SPを先送り（作法）
    hold_pos(m, t0, 0.0, 0.0, -0.2, YAW0, seconds=0.5, hz=20.0)

    # 3) OFFBOARD
    set_mode_offboard(m)
    print("[INFO] OFFBOARD started")

    try:
        # 4) まず速度で確実に上昇（vz<0）
        hold_vel(m, t0, 0.0, 0.0, -0.8, YAW0, seconds=2.0, hz=10.0)
        # 5) 目標高度で位置保持
        hold_pos(m, t0, 0.0, 0.0, -ALT, YAW0, seconds=2.0, hz=10.0)

        # 6) 移動デモ
        hold_pos(m, t0, 10.0,  0.0, -ALT,   0.0, seconds=5.0)
        hold_pos(m, t0, 10.0, 10.0, -ALT,  90.0, seconds=5.0)
        hold_pos(m, t0,  0.0, 10.0, -ALT, 180.0, seconds=5.0)

    except KeyboardInterrupt:
        print("\n[WARN] Interrupted by user")
    finally:
        land(m)

if __name__ == "__main__":
    main()
