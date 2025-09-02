#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymavlink import mavutil
import time

# ===== 接続 =====
m = mavutil.mavlink_connection(
    "udp:127.0.0.1:14550",   # ←環境に合わせて
    source_system=255,       # MPに合わせるなら255
    source_component=190     # GCSっぽいID（任意）
)
m.wait_heartbeat()
print(f"HB from sys {m.target_system} comp {m.target_component}")

# ===== ヘルパ =====
def _param_id_to_str(pid):
    if isinstance(pid, (bytes, bytearray)):
        pid = pid.decode("utf-8", errors="ignore")
    return pid.strip("\x00")

def set_param(name: str, value, ptype=mavutil.mavlink.MAV_PARAM_TYPE_INT32, timeout=3):
    """PARAM_SET → 同名のPARAM_VALUEエコー確認まで"""
    m.mav.param_set_send(
        m.target_system, m.target_component,
        name.encode("utf-8"), float(value), ptype
    )
    t0 = time.time()
    while True:
        msg = m.recv_match(type="PARAM_VALUE", blocking=True, timeout=1)
        if msg:
            pid = _param_id_to_str(msg.param_id)
            if pid == name:
                print(f"{name} = {msg.param_value} (type={msg.param_type})")
                return True
        if time.time() - t0 > timeout:
            print(f"⚠ PARAM echo timeout: {name}")
            return False

def wait_gps_fix(min_fix=3, min_sats=6, timeout=30):
    print("Waiting for GPS fix...")
    t0 = time.time()
    while time.time() - t0 < timeout:
        g = m.recv_match(type="GPS_RAW_INT", blocking=True, timeout=1)
        if g:
            print(f"GPS status: fix={g.fix_type}, sats={g.satellites_visible}")
            if g.fix_type >= min_fix and g.satellites_visible >= min_sats:
                print(f"GPS OK: fix={g.fix_type}, sats={g.satellites_visible}")
                return True
    return False

def wait_origin(timeout=30):
    """Origin確定待ち"""
    print("Waiting for HOME/Origin to be set...")
    t0 = time.time()
    last_req = 0.0
    while time.time() - t0 < timeout:
        # 数秒おきにHOME要求を送って促す
        if time.time() - last_req > 3.0:
            m.mav.command_long_send(
                m.target_system, m.target_component,
                mavutil.mavlink.MAV_CMD_GET_HOME_POSITION, 0,
                0,0,0,0,0,0,0
            )
            last_req = time.time()

        msg = m.recv_match(blocking=True, timeout=1)
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

def mode_mapping_value(mode_name: str) -> int | None:
    mapping = m.mode_mapping() or {}
    return mapping.get(mode_name)

def wait_mode(target_mode: str, timeout=10):
    want = mode_mapping_value(target_mode)
    if want is None:
        print(f"Unknown mode: {target_mode}")
        return False
    
    print(f"Waiting for mode {target_mode} (value={want})...")
    t0 = time.time()
    while time.time() - t0 < timeout:
        hb = m.recv_match(type="HEARTBEAT", blocking=True, timeout=1)
        if hb:
            current_mode = hb.custom_mode
            print(f"Current mode: {current_mode} (want: {want})")
            if current_mode == want:
                return True
    return False

def is_armed(timeout=2):
    t0 = time.time()
    while time.time() - t0 < timeout:
        hb = m.recv_match(type="HEARTBEAT", blocking=True, timeout=1)
        if hb:
            armed = bool(hb.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
            print(f"Armed status: {armed} (base_mode={hb.base_mode})")
            return armed
    return False

def pump_status_text(duration=2.0, non_block_time=0.1):
    t0 = time.time()
    while time.time() - t0 < duration:
        st = m.recv_match(type="STATUSTEXT", blocking=False)
        if st:
            print(f"[STATUSTEXT] sev={st.severity} text={getattr(st, 'text', '')}")
        time.sleep(non_block_time)

def get_arming_check_status():
    """現在のarming checkの状態を確認"""
    print("Checking current arming status...")
    
    # SYS_STATUSメッセージで詳細な状態を確認
    sys_status = m.recv_match(type="SYS_STATUS", blocking=True, timeout=3)
    if sys_status:
        print(f"SYS_STATUS: onboard_control_sensors_health={sys_status.onboard_control_sensors_health}")
    
    # EKF_STATUS_REPORTでEKFの状態を確認
    ekf = m.recv_match(type="EKF_STATUS_REPORT", blocking=True, timeout=3)
    if ekf:
        print(f"EKF flags: {ekf.flags}")
    
    # VIBRATIONでバイブレーション状態確認
    vib = m.recv_match(type="VIBRATION", blocking=True, timeout=3)
    if vib:
        print(f"Vibration: X={vib.vibration_x}, Y={vib.vibration_y}, Z={vib.vibration_z}")

# ===== デバッグ情報の取得 =====
print("=== Initial Status Check ===")
get_arming_check_status()
pump_status_text(3.0)

# ===== 1) SITL向け: より積極的なセーフティ緩和 =====
print("=== Setting Parameters ===")
# ARMING_CHECKを完全に無効化
set_param("ARMING_CHECK", 0, mavutil.mavlink.MAV_PARAM_TYPE_INT32)

# その他のSITL用パラメータ
set_param("SIM_SPEEDUP", 1, mavutil.mavlink.MAV_PARAM_TYPE_REAL32)
set_param("SCHED_LOOP_RATE", 50, mavutil.mavlink.MAV_PARAM_TYPE_INT32)  # 180は高すぎかも

# GPSとEKF関連の緩和
set_param("GPS_TYPE", 1, mavutil.mavlink.MAV_PARAM_TYPE_INT8)
set_param("EK2_ENABLE", 0, mavutil.mavlink.MAV_PARAM_TYPE_INT8)  # EKF2無効
set_param("EK3_ENABLE", 1, mavutil.mavlink.MAV_PARAM_TYPE_INT8)  # EKF3有効
set_param("AHRS_EKF_TYPE", 3, mavutil.mavlink.MAV_PARAM_TYPE_INT8)  # EKF3使用

# バッテリー関連の緩和（SITL用）
set_param("BATT_MONITOR", 4, mavutil.mavlink.MAV_PARAM_TYPE_INT8)  # シミュレーション
set_param("FS_BATT_ENABLE", 0, mavutil.mavlink.MAV_PARAM_TYPE_INT8)  # バッテリーフェールセーフ無効

# ===== 2) 再起動なしで進める（まず試す） =====
print("=== Skipping reboot for now ===")
time.sleep(2.0)  # パラメータ反映待ち

# ===== 3) GPS fix / Origin 待ち =====
if not wait_gps_fix(min_fix=2, min_sats=4, timeout=45):  # 条件緩和
    print("⚠ GPS not ready, but continuing...")

if not wait_origin(timeout=30):
    print("⚠ Origin not confirmed, but continuing...")
    # 手動でHOMEを設定してみる
    print("Trying to set HOME manually...")
    m.mav.command_long_send(
        m.target_system, m.target_component,
        mavutil.mavlink.MAV_CMD_DO_SET_HOME, 0,
        1,  # use current location
        0,0,0,0,0,0
    )
    time.sleep(2.0)

# ===== 4) まずSTABILIZEモードにしてからGUIDEDへ =====
print("=== Setting Mode to STABILIZE first ===")
m.set_mode_apm("STABILIZE")
time.sleep(2.0)

print("=== Setting Mode to GUIDED ===")
m.set_mode_apm("GUIDED")
if not wait_mode("GUIDED", timeout=8):
    print("⚠ Failed to enter GUIDED, trying LOITER...")
    m.set_mode_apm("LOITER")
    if not wait_mode("LOITER", timeout=8):
        print("⚠ Failed to enter LOITER, continuing anyway...")

# ===== 5) ARM前の最終チェック =====
print("=== Pre-ARM Status Check ===")
get_arming_check_status()
pump_status_text(2.0)

# ===== 6) ARM試行（複数の方法） =====
if not is_armed():
    print("=== Attempting to ARM ===")
    
    # 方法1: 基本的なARM
    print("ARM attempt 1: Basic ARM")
    m.mav.command_long_send(
        m.target_system, m.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0, 1, 0, 0,0,0,0,0
    )
    
    # ACKを待つ
    ack = m.recv_match(type="COMMAND_ACK", blocking=True, timeout=5)
    if ack:
        print(f"ARM ACK: result={ack.result}")
        if ack.result != mavutil.mavlink.MAV_RESULT_ACCEPTED:
            print("ARM rejected, checking status...")
            pump_status_text(3.0)
    
    time.sleep(2.0)
    
    if not is_armed():
        # 方法2: 強制ARM (param2=21196)
        print("ARM attempt 2: Force ARM with magic number")
        m.mav.command_long_send(
            m.target_system, m.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0, 1, 21196, 0,0,0,0,0
        )
        
        ack = m.recv_match(type="COMMAND_ACK", blocking=True, timeout=5)
        if ack:
            print(f"Force ARM ACK: result={ack.result}")
        
        time.sleep(2.0)
    
    if not is_armed():
        # 方法3: MAVLINKメッセージでのARM
        print("ARM attempt 3: SET_MODE with armed flag")
        mode_val = mode_mapping_value("GUIDED") or 4
        m.mav.set_mode_send(
            m.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED | mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED,
            mode_val
        )
        time.sleep(2.0)
    
    # 最終確認
    armed = is_armed(timeout=5)
    if armed:
        print("✓ Successfully ARMED!")
    else:
        print("✗ ARM failed - checking final status...")
        pump_status_text(5.0)
        
        # パラメータリストを取得してArming checkを確認
        print("Requesting parameter list...")
        m.mav.param_request_list_send(m.target_system, m.target_component)
        time.sleep(2.0)
        
        # いくつかの重要なパラメータを確認
        for param in ["ARMING_CHECK", "GPS_TYPE", "EK3_ENABLE"]:
            m.mav.param_request_read_send(
                m.target_system, m.target_component,
                param.encode("utf-8"), -1
            )
            time.sleep(0.5)
        
        pump_status_text(3.0)
        
else:
    print("✓ Already armed")

# ===== 7) TAKEOFF（ARMできた場合のみ） =====
if is_armed():
    print("=== TAKEOFF ===")
    alt = 10.0  # HOME相対[m]
    m.mav.command_long_send(
        m.target_system, m.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
        0, 0,0,0,0, 0,0, float(alt)
    )
    ack = m.recv_match(type="COMMAND_ACK", blocking=True, timeout=5)
    print("TAKEOFF ACK:", ack)
    
    # STATUSTEXTを監視
    pump_status_text(5.0)
else:
    print("Skipping TAKEOFF - not armed")

print("=== Script Complete ===")