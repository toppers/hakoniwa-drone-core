#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import time
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

EXTERNAL_RPC_DIR = Path(__file__).resolve().parents[1]
if str(EXTERNAL_RPC_DIR) not in sys.path:
    sys.path.insert(0, str(EXTERNAL_RPC_DIR))

import hakopy

REPO_ROOT = Path(__file__).resolve().parents[3]
SHOW_TOOL_DIR = REPO_ROOT / "tools" / "drone-show"
if str(SHOW_TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(SHOW_TOOL_DIR))

from load_show_config import resolve_show_config

from hakosim_async_shared_asset_rpc import AssetAsyncSharedHakoniwaRpcDroneClient
from hakosim_rpc import DEFAULT_SERVICE_CONFIG_PATH
from service_config_loader import create_runtime_service_config
from show_runner import assign_index, assign_nearest, any_failed, world_points_from_formation


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run formation show as Hakoniwa asset")
    p.add_argument("--show-json", type=Path, required=True, help="Path to show JSON")
    p.add_argument(
        "--service-config",
        dest="service_config_path",
        type=Path,
        default=DEFAULT_SERVICE_CONFIG_PATH,
    )
    p.add_argument("--drones", nargs="+", help="Target drone names")
    p.add_argument("--drone-count", type=int, help="Generate Drone-1..N automatically")
    p.add_argument("--asset-name", default="ShowRunnerAsset", help="Hakoniwa asset name")
    p.add_argument("--proc-count", type=int, default=1, help="Number of drone-service processes")
    p.add_argument("--summary-json", type=Path, help="Optional summary JSON output path")
    p.add_argument("--assign-mode", choices=["index", "nearest"], default="index")
    p.add_argument("--takeoff-alt", type=float, help="Takeoff altitude [m] (default: base_alt)")
    p.add_argument("--z-offset-m", type=float, default=0.0, help="Additional Z offset applied to all formation points [m]")
    p.add_argument("--speed", type=float, default=1.5, help="GoTo speed [m/s]")
    p.add_argument("--tolerance", type=float, default=0.5, help="GoTo tolerance [m]")
    p.add_argument("--timeout-sec", type=float, default=90.0, help="Per-command timeout [sec]")
    p.add_argument("--delta-time-msec", type=int, default=20, help="Asset manual step interval [msec]")
    p.add_argument(
        "--final-hold-extra-sec",
        type=float,
        default=5.0,
        help="Extra hold time added only to the last formation [sec]",
    )
    p.add_argument("--land", action="store_true", help="Land all drones at end")
    p.add_argument(
        "--pdu-config-path",
        type=Path,
        help="Override PDU config path passed to hakopy.asset_register()",
    )
    return p.parse_args()


@dataclass
class Phase:
    name: str
    submit: Callable[[], list]
    on_complete: Callable[[list], None]


class AssetAsyncSharedFleet:
    def __init__(
        self,
        *,
        drone_names: list[str],
        service_config_path: Path,
        asset_name: str,
        delta_time_usec: int,
        timeout_msec: int,
    ) -> None:
        self.drone_names = list(drone_names)
        self.clients = {
            drone_name: AssetAsyncSharedHakoniwaRpcDroneClient(
                drone_name=drone_name,
                service_config_path=service_config_path,
                asset_name=asset_name,
                delta_time_usec=delta_time_usec,
                timeout_msec=timeout_msec,
                poll_interval_sec=0.0,
            )
            for drone_name in self.drone_names
        }

    def prepare_services(self, service_types: list[str]) -> None:
        for client in self.clients.values():
            client.prepare_services(service_types)

    def poll_once(self) -> int:
        runtime_ids: set[int] = set()
        processed = 0
        for client in self.clients.values():
            rid = id(client._runtime)
            if rid in runtime_ids:
                continue
            runtime_ids.add(rid)
            processed += client.poll_once()
        return processed

    def set_ready_async_all(self) -> list:
        return [self.clients[d].set_ready_async() for d in self.drone_names]

    def takeoff_async_all(self, alt_m: float) -> list:
        return [self.clients[d].takeoff_async(alt_m) for d in self.drone_names]

    def goto_async_all(
        self,
        assignments: dict[str, tuple[float, float, float]],
        *,
        speed_m_s: float,
        tolerance_m: float,
        timeout_sec: float,
    ) -> list:
        return [
            self.clients[d].goto_async(
                assignments[d][0],
                assignments[d][1],
                assignments[d][2],
                yaw_deg=0.0,
                speed_m_s=speed_m_s,
                tolerance_m=tolerance_m,
                timeout_sec=timeout_sec,
            )
            for d in self.drone_names
        ]

    def land_async_all(self) -> list:
        return [self.clients[d].land_async() for d in self.drone_names]


class AssetShowStateMachine:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.delta_time_usec = int(args.delta_time_msec) * 1000
        self.resolved = resolve_show_config(args.show_json.resolve(), enforce_drone_count=True)
        self.meta = self.resolved.get("meta", {})
        self.options = self.resolved.get("options", {})
        self.formations = self.resolved.get("formations", {})
        self.timeline = self.resolved.get("timeline", [])
        self.drone_names = self._resolve_drones()
        if len(self.drone_names) != int(self.meta.get("drone_count", 0)):
            raise SystemExit(
                f"drone count ({len(self.drone_names)}) must equal show meta.drone_count ({self.meta.get('drone_count')})"
            )
        self.center = self.options.get("center", [0.0, 0.0, 0.0])
        self.scale = float(self.options.get("scale", 1.0))
        self.base_alt = float(self.options.get("base_alt", 0.0))
        self.z_offset_m = float(args.z_offset_m)
        self.takeoff_alt = (
            args.takeoff_alt if args.takeoff_alt is not None else max(0.5, self.base_alt)
        )
        self.estimated_positions: dict[str, tuple[float, float, float]] | None = None
        self.pending = []
        self.phase_index = 0
        self.hold_remaining_usec = 0
        self.final_settle_remaining_usec = 0
        self.done = False
        self.failed = False
        self.failure_logged = False
        self.prepared = False
        self.prepare_attempts = 0
        self.fleet: AssetAsyncSharedFleet | None = None
        self.total_t0 = time.perf_counter()
        self.prepare_t0: float | None = None
        self.phase_t0: float | None = None
        self.phase_times: dict[str, float] = {}
        self.summary_written = False
        self.phases = self._build_phases()

    def _resolve_drones(self) -> list[str]:
        if self.args.drones:
            return list(self.args.drones)
        if self.args.drone_count:
            return [f"Drone-{i}" for i in range(1, self.args.drone_count + 1)]
        raise SystemExit("Either --drones or --drone-count is required")

    def _write_summary(self, status: str, error: str | None = None) -> None:
        if self.summary_written or self.args.summary_json is None:
            return
        total_sec = time.perf_counter() - self.total_t0
        if "total" not in self.phase_times:
            self.phase_times["total"] = total_sec
        payload = {
            "status": status,
            "error": error,
            "asset_name": self.args.asset_name,
            "show_name": self.meta.get("name", "unknown"),
            "show_json": str(self.args.show_json.resolve()),
            "drone_count": len(self.drone_names),
            "proc_count": int(self.args.proc_count),
            "assign_mode": self.args.assign_mode,
            "delta_time_msec": int(self.args.delta_time_msec),
            "phase_times_sec": self.phase_times,
            "total_sec": total_sec,
        }
        path = self.args.summary_json.resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
        self.summary_written = True

    def _build_phases(self) -> list[Phase]:
        phases: list[Phase] = []
        phases.append(
            Phase(
                name="set_ready",
                submit=lambda: self.fleet.set_ready_async_all(),
                on_complete=self._on_simple_complete("set_ready"),
            )
        )
        phases.append(
            Phase(
                name="takeoff",
                submit=lambda: self.fleet.takeoff_async_all(self.takeoff_alt),
                on_complete=self._on_simple_complete("takeoff"),
            )
        )
        for idx, step in enumerate(self.timeline, start=1):
            fid = step["formation"]
            duration = float(step["duration_sec"])
            phases.append(
                Phase(
                    name=f"goto#{idx}:{fid}",
                    submit=self._make_goto_submit(fid=fid, duration=duration),
                    on_complete=self._make_goto_complete(fid=fid, step=step),
                )
            )
        if self.args.land:
            phases.append(
                Phase(
                    name="land",
                    submit=lambda: self.fleet.land_async_all(),
                    on_complete=self._on_simple_complete("land"),
                )
            )
        return phases

    def _on_simple_complete(self, phase_name: str) -> Callable[[list], None]:
        def _handler(results: list) -> None:
            if any_failed(results):
                raise RuntimeError(f"{phase_name} failed")
        return _handler

    def _make_goto_submit(self, *, fid: str, duration: float) -> Callable[[], list]:
        def _submit() -> list:
            world_points = world_points_from_formation(
                self.formations[fid]["points"],
                center=self.center,
                scale=self.scale,
                base_alt=self.base_alt,
            )
            if self.z_offset_m != 0.0:
                world_points = [
                    (point[0], point[1], point[2] + self.z_offset_m)
                    for point in world_points
                ]
            if self.args.assign_mode == "index" or self.estimated_positions is None:
                assignments = assign_index(self.drone_names, world_points)
            else:
                assignments = assign_nearest(
                    self.drone_names,
                    self.estimated_positions,
                    world_points,
                )
            self._current_assignments = assignments
            return self.fleet.goto_async_all(
                assignments,
                speed_m_s=self.args.speed,
                tolerance_m=self.args.tolerance,
                timeout_sec=max(self.args.timeout_sec, duration + 10.0),
            )

        return _submit

    def _make_goto_complete(self, *, fid: str, step: dict) -> Callable[[list], None]:
        def _handler(results: list) -> None:
            if any_failed(results):
                raise RuntimeError(f"goto failed: formation={fid}")
            if self.estimated_positions is None:
                self.estimated_positions = {}
            for d in self.drone_names:
                self.estimated_positions[d] = self._current_assignments[d]
            hold_sec = float(step.get("hold_sec", 0.0))
            if self.phase_index == len(self.phases) - 1:
                hold_sec += max(0.0, float(self.args.final_hold_extra_sec))
            self.hold_remaining_usec = int(max(0.0, hold_sec) * 1_000_000)

        return _handler

    def on_initialize(self) -> int:
        try:
            print(
                "INFO: asset_show_start "
                f"name={self.meta.get('name', 'unknown')} "
                f"drones={len(self.drone_names)} "
                f"steps={len(self.timeline)} "
                f"assign_mode={self.args.assign_mode} "
                f"z_offset_m={self.args.z_offset_m}"
            )
            self.fleet = AssetAsyncSharedFleet(
                drone_names=self.drone_names,
                service_config_path=self.args.service_config_path.resolve(),
                asset_name=self.args.asset_name,
                delta_time_usec=self.delta_time_usec,
                timeout_msec=int(self.args.timeout_sec * 1000),
            )
        except Exception as e:
            self.failed = True
            if not self.failure_logged:
                self.failure_logged = True
                print(f"ERROR: asset_initialize failed: {e}")
                traceback.print_exc()
            self._write_summary("failed", str(e))
        return 0

    def _prepare_services_if_needed(self) -> None:
        if self.prepared:
            return
        self.prepare_attempts += 1
        prepare_services = ["DroneSetReady", "DroneTakeOff", "DroneGoTo"]
        if self.args.land:
            prepare_services.append("DroneLand")
        try:
            self.prepare_t0 = time.perf_counter()
            self.fleet.prepare_services(prepare_services)
            self.prepared = True
            sec = time.perf_counter() - self.prepare_t0
            self.phase_times["prepare_basic_services"] = sec
            print(f"INFO: phase_time name=prepare_basic_services sec={sec:.3f}")
            self.prepare_t0 = None
        except Exception:
            pass

    def step_once(self) -> None:
        if self.done or self.failed:
            return
        if not self.prepared:
            self._prepare_services_if_needed()
            return
        if self.hold_remaining_usec > 0:
            self.hold_remaining_usec = max(0, self.hold_remaining_usec - self.delta_time_usec)
            return
        if self.pending:
            processed = self.fleet.poll_once()
            if not all(f.done() for f in self.pending):
                if processed == 0:
                    time.sleep(min(self.args.delta_time_msec / 1000.0, 0.01))
                return
            if all(f.done() for f in self.pending):
                results = [f.result(timeout=0.0) for f in self.pending]
                phase = self.phases[self.phase_index]
                print(f"INFO: asset_phase_done name={phase.name}")
                if self.phase_t0 is not None:
                    sec = time.perf_counter() - self.phase_t0
                    self.phase_times[phase.name] = sec
                    print(f"INFO: phase_time name={phase.name} sec={sec:.3f}")
                    self.phase_t0 = None
                phase.on_complete(results)
                self.pending = []
                self.phase_index += 1
                if self.phase_index >= len(self.phases):
                    self.final_settle_remaining_usec = self.hold_remaining_usec
                    self.hold_remaining_usec = 0
                    if self.final_settle_remaining_usec <= 0:
                        self.done = True
                        print("INFO: asset_show_done")
                        total_sec = time.perf_counter() - self.total_t0
                        self.phase_times["total"] = total_sec
                        print(f"INFO: phase_time name=total sec={total_sec:.3f}")
                        self._write_summary("done")
            return
        if self.final_settle_remaining_usec > 0:
            self.final_settle_remaining_usec = max(
                0, self.final_settle_remaining_usec - self.delta_time_usec
            )
            if self.final_settle_remaining_usec == 0:
                self.done = True
                print("INFO: asset_show_done")
                total_sec = time.perf_counter() - self.total_t0
                self.phase_times["total"] = total_sec
                print(f"INFO: phase_time name=total sec={total_sec:.3f}")
                self._write_summary("done")
            return
        if self.phase_index >= len(self.phases):
            self.done = True
            print("INFO: asset_show_done")
            total_sec = time.perf_counter() - self.total_t0
            self.phase_times["total"] = total_sec
            print(f"INFO: phase_time name=total sec={total_sec:.3f}")
            self._write_summary("done")
            return
        phase = self.phases[self.phase_index]
        print(f"INFO: asset_phase_start name={phase.name}")
        self.phase_t0 = time.perf_counter()
        self.pending = phase.submit()


_RUNNER: AssetShowStateMachine | None = None


def _on_initialize(context) -> int:
    assert _RUNNER is not None
    return _RUNNER.on_initialize()


def _on_reset(context) -> int:
    return 0


def _on_manual_timing_control(context) -> int:
    assert _RUNNER is not None
    try:
        while not _RUNNER.done:
            _RUNNER.step_once()
            if not hakopy.usleep(_RUNNER.delta_time_usec):
                _RUNNER.failed = True
                if not _RUNNER.failure_logged:
                    _RUNNER.failure_logged = True
                    print("ERROR: hakopy.usleep() failed")
                _RUNNER._write_summary("failed", "hakopy.usleep() failed")
                return 0
            if _RUNNER.failed:
                return 0
        return 0
    except Exception as e:
        _RUNNER.failed = True
        if not _RUNNER.failure_logged:
            _RUNNER.failure_logged = True
            print(f"ERROR: asset runner failed: {e}")
            traceback.print_exc()
        _RUNNER._write_summary("failed", str(e))
        return 0


def main() -> int:
    global _RUNNER
    args = parse_args()
    _RUNNER = AssetShowStateMachine(args)

    runtime_service_config_path = create_runtime_service_config(args.service_config_path.resolve())
    if args.pdu_config_path is not None:
        pdu_config_path = args.pdu_config_path.resolve()
    else:
        runtime_service = json.loads(runtime_service_config_path.read_text())
        runtime_pdu_config_path = runtime_service.get("pdu_config_path")
        if not runtime_pdu_config_path:
            raise SystemExit(
                f"pdu_config_path is missing in runtime service config: {runtime_service_config_path}"
            )
        pdu_config_path = Path(runtime_pdu_config_path).resolve()

    callbacks = {
        "on_initialize": _on_initialize,
        "on_simulation_step": None,
        "on_manual_timing_control": _on_manual_timing_control,
        "on_reset": _on_reset,
    }
    ret = hakopy.asset_register(
        args.asset_name,
        str(pdu_config_path),
        callbacks,
        _RUNNER.delta_time_usec,
        hakopy.HAKO_ASSET_MODEL_CONTROLLER,
    )
    if ret is False:
        print(f"ERROR: hako_asset_register() returns {ret}.")
        return 1

    ret = hakopy.start()
    print(f"INFO: hako_asset_start() returns {ret}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
