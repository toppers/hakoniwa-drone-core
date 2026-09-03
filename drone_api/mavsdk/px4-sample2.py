#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import math
import argparse
from contextlib import suppress
from pymavlink import mavutil

KEEPALIVE_HZ = 10.0
PRE_OFFBOARD_SETPOINT_SEC = 1.5
PRE_OFFBOARD_SETPOINT_HZ = 20.0
# The bundled model reliably demonstrates a short 0.5 m takeoff.
ALT = 0.5
YAW0 = 0.0

def _ack_name(result):
    entry = mavutil.mavlink.enums.get('MAV_RESULT', {}).get(result)
    return entry.name if entry is not None else str(result)

# 正しい type_mask（forceビット=0）
MASK_POS_YAW = 0x09F8  # 位置+Yawのみ有効（vel/accel/yaw_rate無効, force無効）
# POSITION_TARGET_TYPEMASK: ignore x/y/z (bits 0..2), acceleration/force
# (bits 6..9), and yaw_rate (bit 11).  vx/vy/vz (bits 3..5) and yaw (bit 10)
# remain enabled, so this is velocity + yaw only.
MASK_VEL_YAW = 0x09C7

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
    # Do not block here: the Offboard proof-of-life stream must not pause.
    with suppress(Exception):
        ack = m.recv_match(type='COMMAND_ACK', blocking=False)
        if ack is not None:
            print(f"[INFO] ARM ACK: {_ack_name(ack.result)}")
    return True

def set_mode_offboard(m):
    PX4_CUSTOM_MAIN_MODE_OFFBOARD = 6
    m.mav.command_long_send(
        m.target_system, m.target_component,
        mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        PX4_CUSTOM_MAIN_MODE_OFFBOARD,
        0,0,0,0,0
    )
    # Do not block here: the next setpoint is sent immediately after this call.
    with suppress(Exception):
        ack = m.recv_match(type='COMMAND_ACK', blocking=False)
        if ack is not None:
            print(f"[INFO] OFFBOARD ACK: {_ack_name(ack.result)}")
    return True

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

def takeoff(m, t0, height_m=ALT, climb_speed_m_s=0.8):
    """PX4 Offboardで離陸し、指定高度を速度指令で保持する。

    Local NEDでは上向きが負のZなので、上昇中のvzは負値にする。
    Offboardのsetpoint切れを防ぐため、速度指令を継続送信した後、
    目標高度の位置setpointを継続送信して高度を保持する。
    """
    height_m = abs(float(height_m))
    climb_speed_m_s = abs(float(climb_speed_m_s))
    if height_m <= 0.0 or climb_speed_m_s <= 0.0:
        raise ValueError("height_m and climb_speed_m_s must be positive")

    print(f"[INFO] Takeoff: height={height_m:.2f}m speed={climb_speed_m_s:.2f}m/s")
    # Keep sending vz while observing LOCAL_POSITION_NED.  A fixed sleep is
    # insufficient because it would advance to the horizontal demo even when
    # PX4 ignored the vertical setpoint.
    timeout = max(15.0, height_m / climb_speed_m_s * 3.0)
    dt = 1.0 / KEEPALIVE_HZ
    started = time.time()
    last_report = 0.0
    reached = False
    initial_z = None
    target_z = None
    while time.time() - started < timeout:
        send_vel_ned(m, t0, 0.0, 0.0, -climb_speed_m_s, YAW0)
        msg = m.recv_match(type='LOCAL_POSITION_NED', blocking=False)
        if msg is not None:
            if initial_z is None:
                initial_z = float(msg.z)
                target_z = initial_z - height_m + 0.15
                print(f"[INFO] Takeoff reference: z0={initial_z:.2f}m target={target_z:.2f}m")
            if time.time() - last_report >= 1.0:
                print(f"[INFO] Takeoff state: z={msg.z:.2f}m vz={msg.vz:.2f}m/s")
                last_report = time.time()
            if target_z is not None and float(msg.z) <= target_z:
                reached = True
                break
        time.sleep(dt)
    if not reached:
        raise RuntimeError("Takeoff failed: target altitude was not reached")
    hold_vel(m, t0, 0.0, 0.0, 0.0, YAW0, seconds=2.0, hz=KEEPALIVE_HZ)
    print(f"[INFO] Takeoff complete: target_altitude={height_m:.2f}m")

def land(m):
    m.mav.command_long_send(
        m.target_system, m.target_component,
        mavutil.mavlink.MAV_CMD_NAV_LAND, 0,
        0,0,0,0, 0,0, 0
    )
    print("[INFO] LAND command sent")

def main():
    parser = argparse.ArgumentParser(description="PX4 single-vehicle offboard (pymavlink)")
    parser.add_argument("--udp", default="udp:127.0.0.1:14540",
                        help="Connection string (e.g., udp:127.0.0.1:14540)")
    parser.add_argument("--alt", type=float, default=ALT,
                        help=f"Takeoff height relative to the first LOCAL_POSITION_NED z (default: {ALT}m)")
    args = parser.parse_args()

    m = connect(args.udp)
    t0 = time.time()

    # PX4 requires a continuous setpoint stream for more than one second before
    # arming in Offboard or switching to Offboard.  Send a neutral position
    # stream first.  ARM before OFFBOARD is retained for compatibility with
    # PX4 SITL builds that require the vehicle to be armed before mode change.
    print(f"[INFO] Priming Offboard setpoints for {PRE_OFFBOARD_SETPOINT_SEC:.1f}s")
    hold_pos(m, t0, 0.0, 0.0, -0.2, YAW0,
             seconds=PRE_OFFBOARD_SETPOINT_SEC, hz=PRE_OFFBOARD_SETPOINT_HZ)

    # ARM -> OFFBOARD
    arm(m, True)
    print("[INFO] ARM command sent")
    set_mode_offboard(m)
    print("[INFO] OFFBOARD started")

    try:
        # 4) 速度setpointで離陸し、目標高度を保持
        takeoff(m, t0, height_m=args.alt, climb_speed_m_s=0.8)

        # 5) 水平速度デモ（Local NED: vx=North, vy=East, vz=Down）
        print("[INFO] Velocity demo: vx=1.0 m/s (North) for 5s")
        hold_vel(m, t0, vx=1.0, vy=0.0, vz=0.0,
                 yaw_deg=YAW0, seconds=5.0, hz=10.0)
        print("[INFO] Velocity demo: zero velocity for 2s")
        hold_vel(m, t0, vx=0.0, vy=0.0, vz=0.0,
                 yaw_deg=YAW0, seconds=2.0, hz=10.0)
        print("[INFO] Velocity demo: vy=1.0 m/s (East) for 5s")
        hold_vel(m, t0, vx=0.0, vy=1.0, vz=0.0,
                 yaw_deg=YAW0, seconds=5.0, hz=10.0)
        print("[INFO] Velocity demo: zero velocity for 2s")
        hold_vel(m, t0, vx=0.0, vy=0.0, vz=0.0,
                 yaw_deg=YAW0, seconds=2.0, hz=10.0)

    except KeyboardInterrupt:
        print("\n[WARN] Interrupted by user")
    finally:
        land(m)

if __name__ == "__main__":
    main()
