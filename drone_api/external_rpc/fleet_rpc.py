#!/usr/bin/env python3
from __future__ import annotations

import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from hakosim_rpc import DEFAULT_SERVICE_CONFIG_PATH, HakoniwaRpcDroneClient


@dataclass
class DroneStateSnapshot:
    drone_name: str
    ok: bool
    is_ready: bool
    mode: str
    message: str
    x: float
    y: float
    z: float
    roll_deg: float
    pitch_deg: float
    yaw_deg: float


class FleetRpcController:
    def __init__(
        self,
        drone_names: list[str],
        service_config_path: Path | str = DEFAULT_SERVICE_CONFIG_PATH,
        *,
        max_workers: int | None = None,
        monitor_interval_sec: float = 0.1,
    ) -> None:
        self.drone_names = list(drone_names)
        self.service_config_path = Path(service_config_path).resolve()
        self.monitor_interval_sec = monitor_interval_sec
        self._clients = {
            drone_name: HakoniwaRpcDroneClient(
                drone_name=drone_name,
                service_config_path=self.service_config_path,
            )
            for drone_name in self.drone_names
        }
        self._locks = {
            drone_name: threading.Lock() for drone_name in self.drone_names
        }
        self._latest_states: dict[str, DroneStateSnapshot] = {}
        self._state_lock = threading.Lock()
        self._monitor_stop = threading.Event()
        self._monitor_thread: threading.Thread | None = None
        self._executor = ThreadPoolExecutor(
            max_workers=max_workers or max(len(self.drone_names), 1),
            thread_name_prefix="fleet-rpc",
        )

    def close(self) -> None:
        self.stop_monitoring()
        self._executor.shutdown(wait=True)

    def __enter__(self) -> "FleetRpcController":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _call_with_lock(self, drone_name: str, func):
        lock = self._locks[drone_name]
        with lock:
            try:
                return func(self._clients[drone_name])
            except Exception as e:
                raise RuntimeError(f"[{drone_name}] {e}") from e

    def _submit(self, drone_name: str, func) -> Future:
        return self._executor.submit(self._call_with_lock, drone_name, func)

    def set_ready_async(self, drone_name: str) -> Future:
        return self._submit(drone_name, lambda client: client.set_ready())

    def set_ready(self, drone_name: str):
        return self._call_with_lock(drone_name, lambda client: client.set_ready())

    def takeoff_async(self, drone_name: str, alt_m: float) -> Future:
        return self._submit(drone_name, lambda client: client.takeoff(alt_m))

    def takeoff(self, drone_name: str, alt_m: float):
        return self._call_with_lock(drone_name, lambda client: client.takeoff(alt_m))

    def goto_async(
        self,
        drone_name: str,
        x: float,
        y: float,
        z: float,
        yaw_deg: float = 0.0,
        *,
        speed_m_s: float = 1.0,
        tolerance_m: float = 0.5,
        timeout_sec: float = 30.0,
    ) -> Future:
        return self._submit(
            drone_name,
            lambda client: client.goto(
                x,
                y,
                z,
                yaw_deg,
                speed_m_s=speed_m_s,
                tolerance_m=tolerance_m,
                timeout_sec=timeout_sec,
            ),
        )

    def land_async(self, drone_name: str) -> Future:
        return self._submit(drone_name, lambda client: client.land())

    def goto(
        self,
        drone_name: str,
        x: float,
        y: float,
        z: float,
        yaw_deg: float = 0.0,
        *,
        speed_m_s: float = 1.0,
        tolerance_m: float = 0.5,
        timeout_sec: float = 30.0,
    ):
        return self._call_with_lock(
            drone_name,
            lambda client: client.goto(
                x,
                y,
                z,
                yaw_deg,
                speed_m_s=speed_m_s,
                tolerance_m=tolerance_m,
                timeout_sec=timeout_sec,
            ),
        )

    def land(self, drone_name: str):
        return self._call_with_lock(drone_name, lambda client: client.land())

    def get_state(self, drone_name: str):
        return self._call_with_lock(drone_name, lambda client: client.get_state())

    def get_state_async(self, drone_name: str) -> Future:
        return self._submit(drone_name, lambda client: client.get_state())

    def _to_snapshot(self, drone_name: str, state) -> DroneStateSnapshot:
        from hakosim_rpc import quaternion_to_euler_deg

        pos = state.current_pose.position
        ori = state.current_pose.orientation
        roll_deg, pitch_deg, yaw_deg = quaternion_to_euler_deg(
            ori.w, ori.x, ori.y, ori.z
        )
        return DroneStateSnapshot(
            drone_name=drone_name,
            ok=bool(state.ok),
            is_ready=bool(state.is_ready),
            mode=str(state.mode),
            message=str(state.message),
            x=float(pos.x),
            y=float(pos.y),
            z=float(pos.z),
            roll_deg=float(roll_deg),
            pitch_deg=float(pitch_deg),
            yaw_deg=float(yaw_deg),
        )

    def _monitor_loop(self) -> None:
        while not self._monitor_stop.is_set():
            for drone_name in self.drone_names:
                if self._monitor_stop.is_set():
                    break
                try:
                    state = self.get_state(drone_name)
                    snapshot = self._to_snapshot(drone_name, state)
                    with self._state_lock:
                        self._latest_states[drone_name] = snapshot
                except Exception:
                    pass
            self._monitor_stop.wait(self.monitor_interval_sec)

    def start_monitoring(self) -> None:
        if self._monitor_thread is not None and self._monitor_thread.is_alive():
            return
        self._monitor_stop.clear()
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            name="fleet-rpc-monitor",
            daemon=True,
        )
        self._monitor_thread.start()

    def stop_monitoring(self) -> None:
        self._monitor_stop.set()
        if self._monitor_thread is not None:
            self._monitor_thread.join(timeout=1.0)
            self._monitor_thread = None

    def get_latest_state(self, drone_name: str) -> DroneStateSnapshot | None:
        with self._state_lock:
            return self._latest_states.get(drone_name)

    def wait_for_all(
        self,
        futures: list[Future],
        timeout_sec: float | None = None,
        *,
        return_exceptions: bool = False,
    ):
        start = time.time()
        results = []
        for future in futures:
            remaining = None
            if timeout_sec is not None:
                remaining = max(timeout_sec - (time.time() - start), 0.0)
            try:
                results.append(future.result(timeout=remaining))
            except Exception as e:
                if return_exceptions:
                    results.append(e)
                else:
                    raise
        return results
