#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import sys
import time
from pathlib import Path

EXTERNAL_RPC_DIR = Path(__file__).resolve().parents[1]
if str(EXTERNAL_RPC_DIR) not in sys.path:
    sys.path.insert(0, str(EXTERNAL_RPC_DIR))

from fleet_rpc import FleetRpcController
from hakosim_rpc import DEFAULT_SERVICE_CONFIG_PATH

REPO_ROOT = Path(__file__).resolve().parents[3]
SHOW_TOOL_DIR = REPO_ROOT / "tools" / "drone-show"
if str(SHOW_TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(SHOW_TOOL_DIR))

from load_show_config import resolve_show_config


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run formation show from JSON using FleetRpcController")
    p.add_argument("--show-json", type=Path, required=True, help="Path to show JSON")
    p.add_argument(
        "--service-config",
        dest="service_config_path",
        type=Path,
        default=DEFAULT_SERVICE_CONFIG_PATH,
    )
    p.add_argument("--drones", nargs="+", required=True, help="Target drone names")
    p.add_argument("--assign-mode", choices=["index", "nearest"], default="index")
    p.add_argument("--takeoff-alt", type=float, help="Takeoff altitude [m] (default: base_alt)")
    p.add_argument("--speed", type=float, default=1.5, help="GoTo speed [m/s]")
    p.add_argument("--tolerance", type=float, default=0.5, help="GoTo tolerance [m]")
    p.add_argument("--timeout-sec", type=float, default=90.0, help="Per-command timeout [sec]")
    p.add_argument(
        "--ready-gate-timeout-sec",
        type=float,
        default=120.0,
        help="Timeout for pre-set_ready readiness probe via get_state",
    )
    p.add_argument(
        "--ready-gate-interval-sec",
        type=float,
        default=0.5,
        help="Retry interval for readiness probe via get_state",
    )
    p.add_argument(
        "--ready-gate-call-timeout-sec",
        type=float,
        default=30.0,
        help="Per-attempt timeout for readiness probe get_state fan-out",
    )
    p.add_argument(
        "--no-ready-gate",
        action="store_true",
        help="Disable readiness gate before set_ready",
    )
    p.add_argument(
        "--init-retry-max",
        type=int,
        default=100,
        help="Max retry count for set_ready/takeoff initialization phases",
    )
    p.add_argument(
        "--init-retry-interval-sec",
        type=float,
        default=0.2,
        help="Retry interval seconds for set_ready/takeoff initialization phases",
    )
    p.add_argument(
        "--batch-size",
        type=int,
        default=0,
        help="Batch size for parallel RPC fan-out (0: auto, <0: no batching)",
    )
    p.add_argument(
        "--batch-init",
        type=int,
        default=None,
        help="Batch size for set_ready/takeoff (override --batch-size)",
    )
    p.add_argument(
        "--batch-goto",
        type=int,
        default=None,
        help="Batch size for goto steps (override --batch-size)",
    )
    p.add_argument(
        "--batch-land",
        type=int,
        default=None,
        help="Batch size for land (override --batch-size)",
    )
    p.add_argument("--serial", action="store_true", help="Run phases in serial mode")
    p.add_argument("--land", action="store_true", help="Land all drones at end")
    p.add_argument(
        "--proc-count",
        type=int,
        default=1,
        help="Number of drone-service processes used by launcher (for init batching heuristic)",
    )
    p.add_argument(
        "--init-concurrency-per-proc",
        type=int,
        default=12,
        help="Initialization RPC concurrency per drone-service process",
    )
    p.add_argument(
        "--use-async-shared",
        action="store_true",
        help="Use shared-runtime async RPC client implementation",
    )
    return p.parse_args()


def wait_and_print(tag: str, futures, timeout_sec: float, fleet: FleetRpcController):
    print(f"INFO: wait_start tag={tag} futures={len(futures)} timeout_sec={timeout_sec}")
    results = fleet.wait_for_all(
        list(futures), timeout_sec=timeout_sec, return_exceptions=True
    )
    for i, res in enumerate(results):
        if isinstance(res, Exception):
            print(f"INFO: {tag}[{i}] ok=False message={type(res).__name__}: {res!r}")
        else:
            print(f"INFO: {tag}[{i}] ok={res.ok} message={res.message}")
    print(f"INFO: wait_done tag={tag}")
    return results


def run_serial(tag: str, drone_names: list[str], op):
    out = []
    for drone_name in drone_names:
        print(f"INFO: {tag} request drone={drone_name}")
        res = op(drone_name)
        print(f"INFO: {tag} drone={drone_name} ok={res.ok} message={res.message}")
        out.append(res)
    return out


def run_parallel(tag: str, drone_names: list[str], op_async, timeout_sec: float, fleet: FleetRpcController):
    futures = [op_async(drone_name) for drone_name in drone_names]
    return wait_and_print(tag, futures, timeout_sec=timeout_sec, fleet=fleet)


def run_parallel_batched(
    tag: str,
    drone_names: list[str],
    op_async,
    timeout_sec: float,
    fleet: FleetRpcController,
    *,
    batch_size: int,
):
    if batch_size <= 0 or len(drone_names) <= batch_size:
        return run_parallel(tag, drone_names, op_async, timeout_sec=timeout_sec, fleet=fleet)

    results = []
    total = len(drone_names)
    batch_count = (total + batch_size - 1) // batch_size
    for i in range(0, total, batch_size):
        chunk = drone_names[i : i + batch_size]
        bidx = (i // batch_size) + 1
        print(
            "INFO: batch_start "
            f"tag={tag} batch={bidx}/{batch_count} size={len(chunk)}"
        )
        futures = [op_async(drone_name) for drone_name in chunk]
        batch_results = wait_and_print(
            f"{tag}.b{bidx}/{batch_count}",
            futures,
            timeout_sec=timeout_sec,
            fleet=fleet,
        )
        results.extend(batch_results)
    return results


def world_points_from_formation(formation_points, center, scale, base_alt):
    out: list[tuple[float, float, float]] = []
    for p in formation_points:
        x, y, z = p
        out.append(
            (
                float(center[0]) + (float(x) * float(scale)),
                float(center[1]) + (float(y) * float(scale)),
                float(center[2]) + float(base_alt) + (float(z) * float(scale)),
            )
        )
    return out


def capture_positions(
    fleet: FleetRpcController,
    drone_names: list[str],
    *,
    retries: int = 3,
    retry_sleep_sec: float = 0.05,
) -> dict[str, tuple[float, float, float]]:
    out: dict[str, tuple[float, float, float]] = {}
    for d in drone_names:
        last_err: Exception | None = None
        for _ in range(max(1, retries)):
            try:
                st = fleet.get_state(d)
                pos = st.current_pose.position
                out[d] = (float(pos.x), float(pos.y), float(pos.z))
                last_err = None
                break
            except Exception as e:
                last_err = e
                time.sleep(retry_sleep_sec)
        if last_err is not None:
            raise RuntimeError(f"get_state failed for {d}: {last_err}") from last_err
    return out


def assign_index(drone_names: list[str], targets: list[tuple[float, float, float]]) -> dict[str, tuple[float, float, float]]:
    if len(drone_names) != len(targets):
        raise ValueError("drone count and target count mismatch")
    return {d: targets[i] for i, d in enumerate(drone_names)}


def _dist3(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)


def assign_nearest(
    drone_names: list[str],
    current_positions: dict[str, tuple[float, float, float]],
    targets: list[tuple[float, float, float]],
) -> dict[str, tuple[float, float, float]]:
    remaining = targets[:]
    out: dict[str, tuple[float, float, float]] = {}
    for d in drone_names:
        cp = current_positions[d]
        best_i = min(range(len(remaining)), key=lambda i: _dist3(cp, remaining[i]))
        out[d] = remaining.pop(best_i)
    return out


def any_failed(results) -> bool:
    return any(isinstance(r, Exception) or (not bool(getattr(r, "ok", False))) for r in results)


def _failed_drones(drone_names: list[str], results) -> list[str]:
    failed: list[str] = []
    for i, d in enumerate(drone_names):
        if i >= len(results):
            failed.append(d)
            continue
        r = results[i]
        if isinstance(r, Exception) or (not bool(getattr(r, "ok", False))):
            failed.append(d)
    return failed


def _retry_init_phase(
    phase: str,
    drones: list[str],
    op_async,
    *,
    fleet: FleetRpcController,
    timeout_sec: float,
    retry_max: int,
    retry_interval_sec: float,
    batch_size: int,
) -> None:
    pending = list(drones)
    for retry in range(1, retry_max + 1):
        results = run_parallel_batched(
            f"{phase}.r{retry}",
            pending,
            op_async,
            timeout_sec=timeout_sec,
            fleet=fleet,
            batch_size=batch_size,
        )
        pending = _failed_drones(pending, results)
        if not pending:
            return
        print(f"WARN: {phase} retry={retry} failed={len(pending)}")
        time.sleep(retry_interval_sec)
    raise RuntimeError(
        f"{phase} failed after retries: count={len(pending)} sample={pending[:10]}"
    )


def wait_ready_gate(
    fleet: FleetRpcController,
    drone_names: list[str],
    *,
    timeout_sec: float,
    interval_sec: float,
    batch_size: int,
    call_timeout_sec: float,
) -> None:
    if not drone_names:
        return
    # Warm up shared RPC manager with one synchronous call to avoid
    # looking "stuck" during first batched fan-out.
    warmup_deadline = time.time() + min(timeout_sec, 60.0)
    while True:
        try:
            fleet.get_state(drone_names[0])
            break
        except Exception:
            if time.time() >= warmup_deadline:
                break
            time.sleep(0.5)

    deadline = time.time() + timeout_sec
    pending = list(drone_names)
    attempt = 0
    while pending:
        attempt += 1
        results = run_parallel_batched(
            f"ready_gate.r{attempt}",
            pending,
            lambda d: fleet.get_state_async(d),
            timeout_sec=max(5.0, call_timeout_sec),
            fleet=fleet,
            batch_size=batch_size,
        )
        next_pending: list[str] = []
        for i, d in enumerate(pending):
            if i >= len(results):
                next_pending.append(d)
                continue
            if isinstance(results[i], Exception):
                next_pending.append(d)
        pending = next_pending
        if not pending:
            print(f"INFO: ready_gate done attempts={attempt}")
            return
        now = time.time()
        if now >= deadline:
            raise RuntimeError(
                f"ready_gate timeout: pending={len(pending)} sample={pending[:10]} attempts={attempt}"
            )
        print(f"WARN: ready_gate pending={len(pending)} attempt={attempt}")
        time.sleep(interval_sec)


def main() -> int:
    args = parse_args()
    total_t0 = time.perf_counter()
    if args.proc_count < 1:
        raise SystemExit("--proc-count must be >= 1")
    if args.init_concurrency_per_proc < 1:
        raise SystemExit("--init-concurrency-per-proc must be >= 1")

    resolved = resolve_show_config(args.show_json.resolve(), enforce_drone_count=True)
    meta = resolved.get("meta", {})
    options = resolved.get("options", {})
    formations = resolved.get("formations", {})
    timeline = resolved.get("timeline", [])

    if len(args.drones) != int(meta.get("drone_count", 0)):
        raise SystemExit(
            f"--drones count ({len(args.drones)}) must equal show meta.drone_count ({meta.get('drone_count')})"
        )

    center = options.get("center", [0.0, 0.0, 0.0])
    scale = float(options.get("scale", 1.0))
    base_alt = float(options.get("base_alt", 0.0))
    failure_policy = str(options.get("failure_policy", "abort")).lower()
    if failure_policy not in {"abort", "continue", "hold"}:
        raise SystemExit(f"invalid failure_policy: {failure_policy}")

    takeoff_alt = args.takeoff_alt if args.takeoff_alt is not None else max(0.5, base_alt)
    if args.batch_size < 0:
        global_batch_size = 0
    elif args.batch_size == 0:
        # Auto: enable batching only for larger fleets.
        global_batch_size = 32 if len(args.drones) >= 64 else 0
    else:
        global_batch_size = args.batch_size

    auto_init_batch_size = max(1, args.proc_count * args.init_concurrency_per_proc)
    init_batch_size = auto_init_batch_size if args.batch_init is None else max(0, args.batch_init)
    goto_batch_size = global_batch_size if args.batch_goto is None else max(0, args.batch_goto)
    land_batch_size = global_batch_size if args.batch_land is None else max(0, args.batch_land)
    active_drones = list(args.drones)
    held_drones: set[str] = set()
    estimated_positions: dict[str, tuple[float, float, float]] | None = None

    print(
        "INFO: show_start "
        f"name={meta.get('name', 'unknown')} "
        f"drones={len(args.drones)} "
        f"steps={len(timeline)} "
        f"assign_mode={args.assign_mode} "
        f"failure_policy={failure_policy} "
        f"proc_count={args.proc_count} "
        f"init_concurrency_per_proc={args.init_concurrency_per_proc} "
        f"batch_init={init_batch_size if init_batch_size > 0 else 'off'} "
        f"batch_goto={goto_batch_size if goto_batch_size > 0 else 'off'} "
        f"batch_land={land_batch_size if land_batch_size > 0 else 'off'} "
        f"ready_gate={'off' if args.no_ready_gate else 'on'}"
    )

    with FleetRpcController(
        drone_names=args.drones,
        service_config_path=args.service_config_path.resolve(),
        use_async_shared=args.use_async_shared,
    ) as fleet:
        if args.use_async_shared:
            prepare_services = ["DroneSetReady", "DroneTakeOff", "DroneGoTo"]
            if not args.no_ready_gate:
                prepare_services.append("DroneGetState")
            if args.land:
                prepare_services.append("DroneLand")
            print("INFO: prepare_basic_services start")
            t0 = time.perf_counter()
            fleet.prepare_services(prepare_services)
            print(f"INFO: phase_time name=prepare_basic_services sec={time.perf_counter() - t0:.3f}")
            print("INFO: prepare_basic_services done")
        if not args.no_ready_gate:
            t0 = time.perf_counter()
            wait_ready_gate(
                fleet,
                args.drones,
                timeout_sec=args.ready_gate_timeout_sec,
                interval_sec=args.ready_gate_interval_sec,
                batch_size=init_batch_size if init_batch_size > 0 else 24,
                call_timeout_sec=args.ready_gate_call_timeout_sec,
            )
            print(f"INFO: phase_time name=ready_gate sec={time.perf_counter() - t0:.3f}")

        if args.serial:
            t0 = time.perf_counter()
            for d in args.drones:
                print(f"INFO: init serial request drone={d} op=set_ready")
                r1 = fleet.set_ready(d)
                print(f"INFO: init serial drone={d} op=set_ready ok={r1.ok} message={r1.message}")
                print(f"INFO: init serial request drone={d} op=takeoff")
                r2 = fleet.takeoff(d, takeoff_alt)
                print(f"INFO: init serial drone={d} op=takeoff ok={r2.ok} message={r2.message}")
            print(f"INFO: phase_time name=init sec={time.perf_counter() - t0:.3f}")
        else:
            t0 = time.perf_counter()
            retry_batch_size = init_batch_size if init_batch_size > 0 else auto_init_batch_size
            init_groups = [args.drones]
            if retry_batch_size > 0 and len(args.drones) > retry_batch_size:
                init_groups = [
                    args.drones[i : i + retry_batch_size]
                    for i in range(0, len(args.drones), retry_batch_size)
                ]
            total_groups = len(init_groups)
            for i, group in enumerate(init_groups, start=1):
                print(f"INFO: init batch_start {i}/{total_groups} size={len(group)}")
                _retry_init_phase(
                    "set_ready",
                    group,
                    lambda d: fleet.set_ready_async(d),
                    fleet=fleet,
                    timeout_sec=args.timeout_sec,
                    retry_max=args.init_retry_max,
                    retry_interval_sec=args.init_retry_interval_sec,
                    batch_size=retry_batch_size,
                )
                _retry_init_phase(
                    "takeoff",
                    group,
                    lambda d: fleet.takeoff_async(d, takeoff_alt),
                    fleet=fleet,
                    timeout_sec=args.timeout_sec,
                    retry_max=args.init_retry_max,
                    retry_interval_sec=args.init_retry_interval_sec,
                    batch_size=retry_batch_size,
                )
                print(f"INFO: init batch_done {i}/{total_groups}")
            print(f"INFO: phase_time name=init sec={time.perf_counter() - t0:.3f}")

        for idx, step in enumerate(timeline, start=1):
            step_t0 = time.perf_counter()
            fid = step["formation"]
            duration = float(step["duration_sec"])
            hold_sec = float(step["hold_sec"])
            world_points = world_points_from_formation(
                formations[fid]["points"],
                center=center,
                scale=scale,
                base_alt=base_alt,
            )
            if args.assign_mode == "index":
                assignments = assign_index(args.drones, world_points)
            else:
                if estimated_positions is None:
                    # Skip initial get_state fan-out after takeoff.
                    # Start from deterministic index mapping, then update
                    # estimated_positions from successful goto responses.
                    assignments = assign_index(args.drones, world_points)
                    estimated_positions = dict(assignments)
                else:
                    current = estimated_positions
                    assignments = assign_nearest(args.drones, current, world_points)

            target_drones = [d for d in active_drones if d not in held_drones]
            print(
                "INFO: step_start "
                f"index={idx} formation={fid} duration_sec={duration} hold_sec={hold_sec} "
                f"active={len(target_drones)} held={len(held_drones)}"
            )

            if args.serial:
                results = run_serial(
                    f"goto#{idx}",
                    target_drones,
                    lambda d: fleet.goto(
                        d,
                        assignments[d][0],
                        assignments[d][1],
                        assignments[d][2],
                        yaw_deg=0.0,
                        speed_m_s=args.speed,
                        tolerance_m=args.tolerance,
                        timeout_sec=max(args.timeout_sec, duration + 5.0),
                    ),
                )
            else:
                results = run_parallel_batched(
                    f"goto#{idx}",
                    target_drones,
                    lambda d: fleet.goto_async(
                        d,
                        assignments[d][0],
                        assignments[d][1],
                        assignments[d][2],
                        yaw_deg=0.0,
                        speed_m_s=args.speed,
                        tolerance_m=args.tolerance,
                        timeout_sec=max(args.timeout_sec, duration + 5.0),
                    ),
                    timeout_sec=max(args.timeout_sec, duration + 10.0),
                    fleet=fleet,
                    batch_size=goto_batch_size,
                )

            if any_failed(results):
                print(f"WARN: step_failed index={idx} formation={fid} policy={failure_policy}")
                if failure_policy == "abort":
                    raise RuntimeError(f"step failed: {idx}/{len(timeline)} formation={fid}")
                if failure_policy == "hold":
                    # crude hold policy: remove failed drones from subsequent motion
                    for i, r in enumerate(results):
                        if not bool(getattr(r, "ok", False)):
                            held_drones.add(target_drones[i])
                    print(f"WARN: hold_applied held_drones={sorted(held_drones)}")

            # Update estimated positions for next nearest assignment.
            if estimated_positions is None:
                estimated_positions = {}
            for i, d in enumerate(target_drones):
                if i < len(results) and bool(getattr(results[i], "ok", False)):
                    estimated_positions[d] = assignments[d]

            if hold_sec > 0:
                time.sleep(hold_sec)
            print(
                f"INFO: phase_time name=step#{idx} formation={fid} sec={time.perf_counter() - step_t0:.3f}"
            )

        if args.land:
            t0 = time.perf_counter()
            final_targets = [d for d in args.drones if d not in held_drones]
            if args.serial:
                run_serial("land", final_targets, lambda d: fleet.land(d))
            else:
                run_parallel_batched(
                    "land",
                    final_targets,
                    lambda d: fleet.land_async(d),
                    timeout_sec=args.timeout_sec,
                    fleet=fleet,
                    batch_size=land_batch_size,
                )
            print(f"INFO: phase_time name=land sec={time.perf_counter() - t0:.3f}")

    print(f"INFO: phase_time name=total sec={time.perf_counter() - total_t0:.3f}")
    print("INFO: show_done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
