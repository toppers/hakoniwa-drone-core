#!/usr/bin/env python3
from __future__ import annotations

import argparse
import time
from pathlib import Path
import sys

EXTERNAL_RPC_DIR = Path(__file__).resolve().parents[1]
if str(EXTERNAL_RPC_DIR) not in sys.path:
    sys.path.insert(0, str(EXTERNAL_RPC_DIR))

from fleet_rpc import FleetRpcController
from hakosim_rpc import DEFAULT_SERVICE_CONFIG_PATH


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Multi-drone GoTo demo")
    parser.add_argument(
        "--service-config",
        dest="service_config_path",
        type=Path,
        default=DEFAULT_SERVICE_CONFIG_PATH,
    )
    parser.add_argument(
        "--drones",
        nargs="+",
        required=True,
        help="Target drone names",
    )
    parser.add_argument("--x", type=float, default=1.0)
    parser.add_argument("--y", type=float, default=0.0)
    parser.add_argument("--z", type=float, default=3.0)
    parser.add_argument("--yaw", type=float, default=0.0)
    parser.add_argument("--speed", type=float, default=1.0)
    parser.add_argument("--tolerance", type=float, default=0.5)
    parser.add_argument("--timeout-sec", type=float, default=30.0)
    parser.add_argument("--monitor-sec", type=float, default=3.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    with FleetRpcController(
        drone_names=args.drones,
        service_config_path=args.service_config_path.resolve(),
    ) as fleet:
        fleet.start_monitoring()
        futures = [
            fleet.goto_async(
                drone_name,
                args.x,
                args.y,
                args.z,
                args.yaw,
                speed_m_s=args.speed,
                tolerance_m=args.tolerance,
                timeout_sec=args.timeout_sec,
            )
            for drone_name in args.drones
        ]
        for response in fleet.wait_for_all(futures, timeout_sec=args.timeout_sec + 5.0):
            print(f"INFO: goto response ok={response.ok} message={response.message}")

        end_time = time.time() + args.monitor_sec
        while time.time() < end_time:
            for drone_name in args.drones:
                state = fleet.get_latest_state(drone_name)
                if state is None:
                    continue
                print(
                    "INFO: latest_state "
                    f"drone={state.drone_name} "
                    f"mode={state.mode} "
                    f"message={state.message} "
                    f"pos=({state.x:.3f}, {state.y:.3f}, {state.z:.3f}) "
                    f"yaw_deg={state.yaw_deg:.3f}"
                )
            time.sleep(0.5)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
