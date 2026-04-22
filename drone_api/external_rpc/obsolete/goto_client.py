#!/usr/bin/env python3
from __future__ import annotations

import argparse
import time
from pathlib import Path
import sys

EXTERNAL_RPC_DIR = Path(__file__).resolve().parents[1]
if str(EXTERNAL_RPC_DIR) not in sys.path:
    sys.path.insert(0, str(EXTERNAL_RPC_DIR))

from hakosim_rpc import (
    DEFAULT_SERVICE_CONFIG_PATH,
    HakoniwaRpcDroneClient,
    print_response_elapsed,
)


DEFAULT_DRONE_NAME = "Drone"
DEFAULT_TARGET_X = 1.0
DEFAULT_TARGET_Y = 0.0
DEFAULT_TARGET_Z = 0.5
DEFAULT_SPEED_M_S = 1.0
DEFAULT_YAW_DEG = 0.0
DEFAULT_TOLERANCE_M = 0.5
DEFAULT_TIMEOUT_SEC = 30.0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send DroneGoTo request")
    parser.add_argument("x", nargs="?", type=float, default=DEFAULT_TARGET_X)
    parser.add_argument("y", nargs="?", type=float, default=DEFAULT_TARGET_Y)
    parser.add_argument("z", nargs="?", type=float, default=DEFAULT_TARGET_Z)
    parser.add_argument("yaw", nargs="?", type=float, default=DEFAULT_YAW_DEG)
    parser.add_argument(
        "--service-config",
        dest="service_config_path",
        type=Path,
        default=DEFAULT_SERVICE_CONFIG_PATH,
    )
    parser.add_argument("--drone", dest="drone_name", default=DEFAULT_DRONE_NAME)
    parser.add_argument(
        "--speed", dest="speed_m_s", type=float, default=DEFAULT_SPEED_M_S
    )
    parser.add_argument(
        "--tolerance", dest="tolerance_m", type=float, default=DEFAULT_TOLERANCE_M
    )
    parser.add_argument(
        "--timeout-sec", dest="timeout_sec", type=float, default=DEFAULT_TIMEOUT_SEC
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    client = HakoniwaRpcDroneClient(
        drone_name=args.drone_name,
        service_config_path=args.service_config_path.resolve(),
    )

    print(
        "INFO: request goto "
        f"drone={args.drone_name} "
        f"target=({args.x}, {args.y}, {args.z}) "
        f"yaw_deg={args.yaw}"
    )
    start_time = time.time()
    res = client.goto(
        args.x,
        args.y,
        args.z,
        args.yaw,
        speed_m_s=args.speed_m_s,
        tolerance_m=args.tolerance_m,
        timeout_sec=args.timeout_sec,
    )
    print_response_elapsed("goto call", start_time)
    print(f"INFO: response ok={res.ok} message={res.message}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
