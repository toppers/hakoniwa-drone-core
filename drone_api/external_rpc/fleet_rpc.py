#!/usr/bin/env python3
from __future__ import annotations

import json
import threading
import time
import hakopy
from concurrent.futures import Future, ThreadPoolExecutor, wait
from dataclasses import dataclass
from pathlib import Path

from fleet_rpc_async_shared import AsyncSharedFleetRpcController
from hakosim_rpc import DEFAULT_SERVICE_CONFIG_PATH, HakoniwaRpcDroneClient
from hakoniwa_pdu.impl.pdu_channel_config import PduChannelConfig
from hakoniwa_pdu.pdu_msgs.hako_msgs.pdu_conv_DroneStatus import pdu_to_py_DroneStatus
from service_config_loader import create_runtime_service_config


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


class _FleetStatusReader:
    def __init__(self, service_config_path: Path | str, ensure_initialized) -> None:
        self.service_config_path = Path(service_config_path).resolve()
        self._ensure_initialized = ensure_initialized
        runtime_service_config_path = create_runtime_service_config(
            self.service_config_path
        )
        runtime_service = json.loads(runtime_service_config_path.read_text())
        pdu_config_path = runtime_service.get("pdu_config_path")
        if not pdu_config_path:
            raise RuntimeError(
                f"pdu_config_path is missing in runtime service config: {runtime_service_config_path}"
            )
        self.pdu_config_path = Path(pdu_config_path).resolve()
        self._pdu_config = PduChannelConfig(str(self.pdu_config_path))
        self._read_lock = threading.Lock()

    def get_raw_pdu(self, drone_name: str, pdu_name: str) -> bytearray:
        self._ensure_initialized()
        channel_id = self._pdu_config.get_pdu_channel_id(drone_name, pdu_name)
        pdu_size = self._pdu_config.get_pdu_size(drone_name, pdu_name)
        if channel_id < 0 or pdu_size <= 0:
            raise RuntimeError(
                f"PDU channel is not defined: drone={drone_name} pdu={pdu_name}"
            )
        last_error = None
        with self._read_lock:
            for _ in range(5):
                try:
                    raw_data = hakopy.pdu_read(drone_name, channel_id, pdu_size)
                    if raw_data:
                        return raw_data
                except Exception as e:
                    last_error = e
                time.sleep(0.01)
        raise RuntimeError(
            f"Failed to read PDU raw data directly: drone={drone_name} pdu={pdu_name}"
        ) from last_error

    def get_status(self, drone_name: str):
        return pdu_to_py_DroneStatus(self.get_raw_pdu(drone_name, "status"))


class _SyncFleetRpcController:
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
        self._status_reader = _FleetStatusReader(
            self.service_config_path, self._ensure_external_initialized
        )
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

    def __enter__(self) -> "_SyncFleetRpcController":
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

    def _ensure_external_initialized(self) -> None:
        if not self.drone_names:
            return
        first = self.drone_names[0]
        self._clients[first]._ensure_initialized()

    def _submit(self, drone_name: str, func) -> Future:
        return self._executor.submit(self._call_with_lock, drone_name, func)

    def prepare_basic_services(self) -> None:
        return None

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

    def land_async(self, drone_name: str, timeout_sec: float = 0.0) -> Future:
        return self._submit(
            drone_name, lambda client: client.land(timeout_sec=timeout_sec)
        )

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

    def land(self, drone_name: str, timeout_sec: float = 0.0):
        return self._call_with_lock(
            drone_name, lambda client: client.land(timeout_sec=timeout_sec)
        )

    def get_state(self, drone_name: str):
        return self._call_with_lock(drone_name, lambda client: client.get_state())

    def get_state_async(self, drone_name: str) -> Future:
        return self._submit(drone_name, lambda client: client.get_state())

    def get_raw_pdu(self, drone_name: str, pdu_name: str):
        return self._status_reader.get_raw_pdu(drone_name, pdu_name)

    def get_status(self, drone_name: str):
        return self._status_reader.get_status(drone_name)

    def get_status_async(self, drone_name: str) -> Future:
        return self._executor.submit(self._status_reader.get_status, drone_name)

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
        done, _not_done = wait(futures, timeout=timeout_sec)
        results = []
        for future in futures:
            if future in done:
                try:
                    results.append(future.result())
                except Exception as e:
                    if return_exceptions:
                        results.append(e)
                    else:
                        raise
            else:
                e = TimeoutError()
                if return_exceptions:
                    results.append(e)
                else:
                    raise e
        return results


def FleetRpcController(
    drone_names: list[str],
    service_config_path: Path | str = DEFAULT_SERVICE_CONFIG_PATH,
    *,
    max_workers: int | None = None,
    monitor_interval_sec: float = 0.1,
    use_async_shared: bool = False,
):
    if use_async_shared:
        return AsyncSharedFleetRpcController(
            drone_names=drone_names,
            service_config_path=service_config_path,
            monitor_interval_sec=monitor_interval_sec,
        )
    return _SyncFleetRpcController(
        drone_names=drone_names,
        service_config_path=service_config_path,
        max_workers=max_workers,
        monitor_interval_sec=monitor_interval_sec,
    )
