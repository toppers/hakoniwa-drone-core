#!/usr/bin/env python3
from __future__ import annotations

import threading
import time
from pathlib import Path

from hakosim_async_shared_rpc import AsyncSharedHakoniwaRpcDroneClient
from hakosim_rpc import DEFAULT_SERVICE_CONFIG_PATH
from hakoniwa_pdu.rpc.async_shared import RpcCallFuture


class AsyncSharedFleetRpcController:
    def __init__(
        self,
        drone_names: list[str],
        service_config_path: Path | str = DEFAULT_SERVICE_CONFIG_PATH,
        *,
        monitor_interval_sec: float = 0.1,
    ) -> None:
        self.drone_names = list(drone_names)
        self.service_config_path = Path(service_config_path).resolve()
        self.monitor_interval_sec = monitor_interval_sec
        self._clients = {
            drone_name: AsyncSharedHakoniwaRpcDroneClient(
                drone_name=drone_name,
                service_config_path=self.service_config_path,
            )
            for drone_name in self.drone_names
        }
        self._locks = {
            drone_name: threading.Lock() for drone_name in self.drone_names
        }
        self._future_runtime_ids: dict[int, int] = {}

    def close(self) -> None:
        return None

    def __enter__(self) -> "AsyncSharedFleetRpcController":
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

    def _register_future_runtime(self, future: RpcCallFuture, drone_name: str) -> RpcCallFuture:
        runtime = getattr(self._clients[drone_name], "_runtime", None)
        if runtime is not None:
            self._future_runtime_ids[id(future)] = id(runtime)
        return future

    def _poll_once(self, runtime_ids: set[int] | None = None) -> int:
        processed = 0
        seen_runtimes: set[int] = set()
        for client in self._clients.values():
            runtime = getattr(client, "_runtime", None)
            if runtime is None:
                continue
            runtime_id = id(runtime)
            if runtime_ids is not None and runtime_id not in runtime_ids:
                continue
            if runtime_id in seen_runtimes:
                continue
            seen_runtimes.add(runtime_id)
            processed += client.poll_once()
        return processed

    def prepare_basic_services(self) -> None:
        for drone_name in self.drone_names:
            self._call_with_lock(
                drone_name, lambda client: client.prepare_all_basic_services()
            )

    def prepare_services(self, service_types: list[str]) -> None:
        for drone_name in self.drone_names:
            self._call_with_lock(
                drone_name, lambda client: client.prepare_services(service_types)
            )

    def set_ready_async(self, drone_name: str) -> RpcCallFuture:
        future = self._call_with_lock(
            drone_name, lambda client: client.set_ready_async()
        )
        return self._register_future_runtime(future, drone_name)

    def set_ready(self, drone_name: str):
        return self._call_with_lock(drone_name, lambda client: client.set_ready())

    def takeoff_async(self, drone_name: str, alt_m: float) -> RpcCallFuture:
        future = self._call_with_lock(
            drone_name, lambda client: client.takeoff_async(alt_m)
        )
        return self._register_future_runtime(future, drone_name)

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
    ) -> RpcCallFuture:
        future = self._call_with_lock(
            drone_name,
            lambda client: client.goto_async(
                x,
                y,
                z,
                yaw_deg,
                speed_m_s=speed_m_s,
                tolerance_m=tolerance_m,
                timeout_sec=timeout_sec,
            ),
        )
        return self._register_future_runtime(future, drone_name)

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

    def land_async(self, drone_name: str) -> RpcCallFuture:
        future = self._call_with_lock(drone_name, lambda client: client.land_async())
        return self._register_future_runtime(future, drone_name)

    def land(self, drone_name: str):
        return self._call_with_lock(drone_name, lambda client: client.land())

    def get_state(self, drone_name: str):
        return self._call_with_lock(drone_name, lambda client: client.get_state())

    def get_state_async(self, drone_name: str) -> RpcCallFuture:
        future = self._call_with_lock(
            drone_name, lambda client: client.get_state_async()
        )
        return self._register_future_runtime(future, drone_name)

    def start_monitoring(self) -> None:
        return None

    def stop_monitoring(self) -> None:
        return None

    def get_latest_state(self, drone_name: str):
        return None

    def wait_for_all(
        self,
        futures: list[RpcCallFuture],
        timeout_sec: float | None = None,
        *,
        return_exceptions: bool = False,
    ):
        deadline = None if timeout_sec is None else time.monotonic() + timeout_sec
        pending = list(futures)
        while True:
            still_pending = [future for future in pending if not future.done()]
            if not still_pending:
                break
            pending = still_pending
            runtime_ids = {
                self._future_runtime_ids[ id(future) ]
                for future in pending
                if id(future) in self._future_runtime_ids
            }
            now = time.monotonic()
            if deadline is not None and now >= deadline:
                e = TimeoutError()
                if return_exceptions:
                    return [
                        future.result(timeout=0.0) if future.done() else e
                        for future in futures
                    ]
                raise e
            processed = self._poll_once(runtime_ids if runtime_ids else None)
            if processed == 0:
                remaining = None if deadline is None else max(deadline - now, 0.0)
                sleep_sec = self.monitor_interval_sec
                if remaining is not None:
                    sleep_sec = min(sleep_sec, remaining)
                if sleep_sec > 0:
                    time.sleep(sleep_sec)

        results = []
        for future in futures:
            try:
                results.append(future.result(timeout=0.0))
            except Exception as e:
                if return_exceptions:
                    results.append(e)
                else:
                    raise
            finally:
                self._future_runtime_ids.pop(id(future), None)
        return results
