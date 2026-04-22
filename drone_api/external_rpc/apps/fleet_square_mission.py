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
    p = argparse.ArgumentParser(description="Run square mission for multiple drones in parallel")
    p.add_argument(
        "--service-config",
        dest="service_config_path",
        type=Path,
        default=DEFAULT_SERVICE_CONFIG_PATH,
    )
    p.add_argument("--drones", nargs="+", required=True, help="Target drone names")
    p.add_argument("--alt", type=float, default=0.5, help="Takeoff altitude [m]")
    p.add_argument("--center-x", type=float, default=0.0, help="Square center X [m]")
    p.add_argument("--center-y", type=float, default=0.0, help="Square center Y [m]")
    p.add_argument("--side", type=float, default=4.0, help="Square side length [m]")
    p.add_argument("--z", type=float, default=0.5, help="Square altitude [m]")
    p.add_argument(
        "--layer-size",
        type=int,
        default=8,
        help="Number of drones per altitude layer",
    )
    p.add_argument(
        "--layer-step",
        type=float,
        default=1.0,
        help="Altitude increment [m] per layer",
    )
    p.add_argument("--yaw", type=float, default=0.0, help="Target yaw [deg]")
    p.add_argument(
        "--phase-step",
        type=int,
        default=0,
        help="Waypoint phase shift step per drone index (0 keeps all drones in-phase)",
    )
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


def square_points(center_x: float, center_y: float, side: float) -> list[tuple[float, float]]:
    half = side / 2.0
    p1 = (center_x - half, center_y - half)
    p2 = (center_x + half, center_y - half)
    p3 = (center_x + half, center_y + half)
    p4 = (center_x - half, center_y + half)
    return [p1, p2, p3, p4, p1]


def capture_initial_positions(fleet: FleetRpcController, drone_names: list[str]) -> dict[str, tuple[float, float, float]]:
    positions: dict[str, tuple[float, float, float]] = {}
    for drone_name in drone_names:
        state = fleet.get_state(drone_name)
        pos = state.current_pose.position
        positions[drone_name] = (float(pos.x), float(pos.y), float(pos.z))
        print(
            "INFO: initial_position "
            f"drone={drone_name} "
            f"pos=({positions[drone_name][0]:.3f}, {positions[drone_name][1]:.3f}, {positions[drone_name][2]:.3f})"
        )
    return positions


def build_relative_z_by_drone(
    drone_names: list[str],
    base_relative_z: float,
    layer_size: int,
    layer_step: float,
) -> dict[str, float]:
    if layer_size <= 0:
        raise ValueError("layer_size must be > 0")
    relative_z: dict[str, float] = {}
    for index, drone_name in enumerate(drone_names):
        layer_index = index // layer_size
        relative_z[drone_name] = base_relative_z + (layer_index * layer_step)
    return relative_z


def build_phase_by_drone(
    drone_names: list[str],
    phase_step: int,
    waypoint_count: int,
) -> dict[str, int]:
    if waypoint_count <= 0:
        raise ValueError("waypoint_count must be > 0")
    phases: dict[str, int] = {}
    for index, drone_name in enumerate(drone_names):
        phases[drone_name] = (index * phase_step) % waypoint_count
    return phases


def main() -> int:
    args = parse_args()
    relative_points = square_points(args.center_x, args.center_y, args.side)
    core_points = relative_points[:-1]
    with FleetRpcController(
        drone_names=args.drones,
        service_config_path=args.service_config_path.resolve(),
    ) as fleet:
        relative_z_by_drone = build_relative_z_by_drone(
            args.drones,
            args.z,
            args.layer_size,
            args.layer_step,
        )
        print(
            "INFO: altitude layering "
            f"layer_size={args.layer_size} "
            f"layer_step={args.layer_step}"
        )
        for drone_name in args.drones:
            print(
                "INFO: relative_altitude "
                f"drone={drone_name} "
                f"relative_z={relative_z_by_drone[drone_name]:.3f}"
            )
        phase_by_drone = build_phase_by_drone(args.drones, args.phase_step, len(core_points))
        print(
            "INFO: phase_shift "
            f"phase_step={args.phase_step} "
            f"waypoint_count={len(core_points)}"
        )
        for drone_name in args.drones:
            print(
                "INFO: phase "
                f"drone={drone_name} "
                f"offset={phase_by_drone[drone_name]}"
            )

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

        # Capture per-drone reference positions after takeoff completion.
        # Before set_ready/takeoff, GetState can return default/uninitialized
        # values in some environments, which collapses all routes to one point.
        initial_positions = capture_initial_positions(fleet, args.drones)

        for i in range(len(relative_points)):
            step_no = i + 1
            print(
                f"INFO: goto waypoint={step_no}/{len(relative_points)} "
                f"target_relative=(phase-shifted, per-drone-z) yaw={args.yaw} "
                f"speed={args.speed} tol={args.tolerance}"
            )
            def relative_target(drone_name: str) -> tuple[float, float]:
                base_index = i if i < len(core_points) else 0
                point_index = (base_index + phase_by_drone[drone_name]) % len(core_points)
                return core_points[point_index]

            if args.serial:
                run_serial(
                    f"goto#{step_no}",
                    args.drones,
                    lambda d: fleet.goto(
                        d,
                        initial_positions[d][0] + relative_target(d)[0],
                        initial_positions[d][1] + relative_target(d)[1],
                        initial_positions[d][2] + relative_z_by_drone[d],
                        args.yaw,
                        speed_m_s=args.speed,
                        tolerance_m=args.tolerance,
                        timeout_sec=args.timeout_sec,
                    ),
                    timeout_sec=args.timeout_sec + 5.0,
                )
            else:
                run_parallel(
                    f"goto#{step_no}",
                    args.drones,
                    lambda d: fleet.goto_async(
                        d,
                        initial_positions[d][0] + relative_target(d)[0],
                        initial_positions[d][1] + relative_target(d)[1],
                        initial_positions[d][2] + relative_z_by_drone[d],
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
