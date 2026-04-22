#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

EXTERNAL_RPC_DIR = Path(__file__).resolve().parents[1]
if str(EXTERNAL_RPC_DIR) not in sys.path:
    sys.path.insert(0, str(EXTERNAL_RPC_DIR))

from fleet_rpc import FleetRpcController


SERVICE_CONFIG_PATH = Path("config/drone/fleets/services/api-current-service.json")
DRONE_NAMES = ["Drone-1", "Drone-2"]
TAKEOFF_ALT_M = 1.5
TARGETS = {
    "Drone-1": (0.0, 1.0, 1.5),
    "Drone-2": (1.0, 1.0, 1.5),
}


def wait_and_print(
    tag: str,
    futures,
    fleet: FleetRpcController,
    *,
    return_exceptions: bool = False,
) -> None:
    print(f"INFO: {tag} wait_start futures={len(futures)}")
    results = fleet.wait_for_all(
        list(futures), timeout_sec=35.0, return_exceptions=return_exceptions
    )
    for index, result in enumerate(results):
        if isinstance(result, Exception):
            print(
                f"WARN: {tag}[{index}] "
                f"exception={type(result).__name__} message={result}"
            )
            continue
        print(f"INFO: {tag}[{index}] ok={result.ok} message={result.message}")
    print(f"INFO: {tag} wait_done")


def main() -> int:
    with FleetRpcController(
        drone_names=DRONE_NAMES,
        service_config_path=SERVICE_CONFIG_PATH.resolve(),
        use_async_shared=True,
    ) as fleet:
        status1 = fleet.get_status("Drone-1")
        status2 = fleet.get_status("Drone-2")
        print(f"INFO: Drone-1 status={status1}")
        print(f"INFO: Drone-2 status={status2}")
        # 1. SetReady for each drone, then wait for both responses.
        ready_futures = [
            fleet.set_ready_async("Drone-1"),
            fleet.set_ready_async("Drone-2"),
        ]
        wait_and_print("set_ready", ready_futures, fleet)

        # 2. TakeOff for each drone, then wait for both responses.
        takeoff_futures = [
            fleet.takeoff_async("Drone-1", TAKEOFF_ALT_M),
            fleet.takeoff_async("Drone-2", TAKEOFF_ALT_M),
        ]
        wait_and_print("takeoff", takeoff_futures, fleet)

        # 3. GoTo for each drone, then wait for both responses.
        goto_futures = [
            fleet.goto_async(
                "Drone-1",
                TARGETS["Drone-1"][0],
                TARGETS["Drone-1"][1],
                TARGETS["Drone-1"][2],
            ),
            fleet.goto_async(
                "Drone-2",
                TARGETS["Drone-2"][0],
                TARGETS["Drone-2"][1],
                TARGETS["Drone-2"][2],
            ),
        ]
        wait_and_print("goto", goto_futures, fleet)

        # 4. Read back the final state explicitly.
        state1 = fleet.get_state("Drone-1")
        state2 = fleet.get_state("Drone-2")
        pos1 = state1.current_pose.position
        pos2 = state2.current_pose.position
        print(f"INFO: Drone-1 final pos=({float(pos1.x):.3f}, {float(pos1.y):.3f}, {float(pos1.z):.3f})")
        print(f"INFO: Drone-2 final pos=({float(pos2.x):.3f}, {float(pos2.y):.3f}, {float(pos2.z):.3f})")

        # 5. Land for each drone, then wait for both responses.
        land_futures = [
            fleet.land_async("Drone-1", timeout_sec=5.0),
            fleet.land_async("Drone-2", timeout_sec=5.0),
        ]
        wait_and_print("land", land_futures, fleet, return_exceptions=True)

        try:
            status1 = fleet.get_status("Drone-1")
            print(f"INFO: Drone-1 status={status1}")
        except Exception as e:
            print(f"WARN: Drone-1 status unavailable after land: {e}")
        try:
            status2 = fleet.get_status("Drone-2")
            print(f"INFO: Drone-2 status={status2}")
        except Exception as e:
            print(f"WARN: Drone-2 status unavailable after land: {e}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
