#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

EXTERNAL_RPC_DIR = Path(__file__).resolve().parents[1]
if str(EXTERNAL_RPC_DIR) not in sys.path:
    sys.path.insert(0, str(EXTERNAL_RPC_DIR))

from fleet_rpc import FleetRpcController
from hakosim_rpc import DEFAULT_SERVICE_CONFIG_PATH


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run single-point mission for multiple drones in parallel")
    p.add_argument(
        "--service-config",
        dest="service_config_path",
        type=Path,
        default=DEFAULT_SERVICE_CONFIG_PATH,
    )
    p.add_argument("--drones", nargs="+", required=True, help="Target drone names")
    p.add_argument("--alt", type=float, default=0.5, help="Takeoff altitude [m]")
    p.add_argument("--x", type=float, default=2.0, help="Target X [m]")
    p.add_argument("--y", type=float, default=1.0, help="Target Y [m]")
    p.add_argument("--z", type=float, default=0.1, help="Target Z [m]")
    p.add_argument("--yaw", type=float, default=-45.0, help="Target yaw [deg]")
    p.add_argument("--speed", type=float, default=1.0, help="GoTo speed [m/s]")
    p.add_argument("--tolerance", type=float, default=0.5, help="GoTo tolerance [m]")
    p.add_argument("--timeout-sec", type=float, default=30.0, help="Per-command timeout [sec]")
    p.add_argument("--land", action="store_true", help="Land all drones at end")
    p.add_argument("--serial", action="store_true", help="Run command phases in serial mode")
    return p.parse_args()


def wait_and_print(tag: str, futures, timeout_sec: float, fleet: FleetRpcController) -> None:
    print(f"INFO: wait_start tag={tag} futures={len(futures)} timeout_sec={timeout_sec}")
    results = fleet.wait_for_all(list(futures), timeout_sec=timeout_sec)
    for i, res in enumerate(results):
        print(f"INFO: {tag}[{i}] ok={res.ok} message={res.message}")
    print(f"INFO: wait_done tag={tag}")

def run_serial(tag: str, drone_names: list[str], op, timeout_sec: float) -> None:
    for drone_name in drone_names:
        print(f"INFO: {tag} request drone={drone_name}")
        _ = timeout_sec
        res = op(drone_name)
        print(f"INFO: {tag} drone={drone_name} ok={res.ok} message={res.message}")


def run_parallel(tag: str, drone_names: list[str], op_async, timeout_sec: float, fleet: FleetRpcController) -> None:
    futures = [op_async(drone_name) for drone_name in drone_names]
    wait_and_print(tag, futures, timeout_sec=timeout_sec, fleet=fleet)


def main() -> int:
    args = parse_args()
    with FleetRpcController(
        drone_names=args.drones,
        service_config_path=args.service_config_path.resolve(),
    ) as fleet:
        if args.serial:
            print(f"INFO: set_ready serial drones={args.drones}")
            run_serial(
                "set_ready",
                args.drones,
                lambda d: fleet.set_ready(d),
                timeout_sec=args.timeout_sec + 5.0,
            )
        else:
            print(f"INFO: set_ready parallel drones={args.drones}")
            run_parallel(
                "set_ready",
                args.drones,
                lambda d: fleet.set_ready_async(d),
                timeout_sec=args.timeout_sec + 5.0,
                fleet=fleet,
            )

        if args.serial:
            print(f"INFO: takeoff serial alt={args.alt}")
            run_serial(
                "takeoff",
                args.drones,
                lambda d: fleet.takeoff(d, args.alt),
                timeout_sec=args.timeout_sec + 5.0,
            )
        else:
            print(f"INFO: takeoff parallel alt={args.alt}")
            run_parallel(
                "takeoff",
                args.drones,
                lambda d: fleet.takeoff_async(d, args.alt),
                timeout_sec=args.timeout_sec + 5.0,
                fleet=fleet,
            )

        print(
            "INFO: goto parallel "
            f"target=({args.x}, {args.y}, {args.z}) yaw={args.yaw} "
            f"speed={args.speed} tol={args.tolerance}"
        )
        if args.serial:
            run_serial(
                "goto",
                args.drones,
                lambda d: fleet.goto(
                    d,
                    args.x,
                    args.y,
                    args.z,
                    args.yaw,
                    speed_m_s=args.speed,
                    tolerance_m=args.tolerance,
                    timeout_sec=args.timeout_sec,
                ),
                timeout_sec=args.timeout_sec + 5.0,
            )
        else:
            run_parallel(
                "goto",
                args.drones,
                lambda d: fleet.goto_async(
                    d,
                    args.x,
                    args.y,
                    args.z,
                    args.yaw,
                    speed_m_s=args.speed,
                    tolerance_m=args.tolerance,
                    timeout_sec=args.timeout_sec,
                ),
                timeout_sec=args.timeout_sec + 5.0,
                fleet=fleet,
            )

        if args.land:
            if args.serial:
                print("INFO: land serial")
                run_serial(
                    "land",
                    args.drones,
                    lambda d: fleet.land(d),
                    timeout_sec=args.timeout_sec + 5.0,
                )
            else:
                print("INFO: land parallel")
                run_parallel(
                    "land",
                    args.drones,
                    lambda d: fleet.land_async(d),
                    timeout_sec=args.timeout_sec + 5.0,
                    fleet=fleet,
                )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
