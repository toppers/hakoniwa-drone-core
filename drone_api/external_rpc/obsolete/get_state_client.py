#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

EXTERNAL_RPC_DIR = Path(__file__).resolve().parents[1]
if str(EXTERNAL_RPC_DIR) not in sys.path:
    sys.path.insert(0, str(EXTERNAL_RPC_DIR))

from hakosim_rpc import (
    DEFAULT_SERVICE_CONFIG_PATH,
    HakoniwaRpcDroneClient,
    quaternion_to_euler_deg,
)


DEFAULT_DRONE_NAME = "Drone"


def main() -> int:
    service_config_path = (
        Path(sys.argv[1]).resolve()
        if len(sys.argv) >= 2
        else DEFAULT_SERVICE_CONFIG_PATH
    )
    drone_name = sys.argv[2] if len(sys.argv) >= 3 else DEFAULT_DRONE_NAME
    client = HakoniwaRpcDroneClient(
        drone_name=drone_name,
        service_config_path=service_config_path,
    )

    print(f"INFO: request get-state drone={drone_name}")
    res = client.get_state()
    pos = res.current_pose.position
    roll_deg, pitch_deg, yaw_deg = quaternion_to_euler_deg(
        res.current_pose.orientation.w,
        res.current_pose.orientation.x,
        res.current_pose.orientation.y,
        res.current_pose.orientation.z,
    )
    print(
        "INFO: response "
        f"ok={res.ok} "
        f"is_ready={res.is_ready} "
        f"mode={res.mode} "
        f"message={res.message} "
        f"position=({pos.x}, {pos.y}, {pos.z}) "
        f"angle_deg=({roll_deg}, {pitch_deg}, {yaw_deg})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
