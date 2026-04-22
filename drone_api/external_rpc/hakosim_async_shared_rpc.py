#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import threading
import time
from pathlib import Path

import hakopy

REPO_ROOT = Path(__file__).resolve().parents[2]
HAKO_PDU_PYTHON_SRC = REPO_ROOT / "work" / "hakoniwa-pdu-python" / "src"
if str(HAKO_PDU_PYTHON_SRC) not in sys.path:
    sys.path.insert(0, str(HAKO_PDU_PYTHON_SRC))

from hakoniwa_pdu.rpc.auto_wire import _load_protocol_components
from hakoniwa_pdu.rpc.async_shared import (
    AsyncRpcClientHandle,
    RpcCallFuture,
    SharedRpcRuntime,
    SharedRpcRuntimeConfig,
)
from hakoniwa_pdu.pdu_msgs.drone_srv_msgs.pdu_pytype_DroneGetStateRequest import (
    DroneGetStateRequest,
)
from hakoniwa_pdu.pdu_msgs.drone_srv_msgs.pdu_pytype_DroneGoToRequest import (
    DroneGoToRequest,
)
from hakoniwa_pdu.pdu_msgs.drone_srv_msgs.pdu_pytype_DroneLandRequest import (
    DroneLandRequest,
)
from hakoniwa_pdu.pdu_msgs.drone_srv_msgs.pdu_pytype_DroneSetReadyRequest import (
    DroneSetReadyRequest,
)
from hakoniwa_pdu.pdu_msgs.drone_srv_msgs.pdu_pytype_DroneTakeOffRequest import (
    DroneTakeOffRequest,
)
from hakoniwa_pdu.pdu_msgs.geometry_msgs.pdu_pytype_Vector3 import Vector3

from hakosim_rpc import (
    DEFAULT_ASSET_NAME,
    DEFAULT_DELTA_TIME_USEC,
    DEFAULT_OFFSET_PATH,
    DEFAULT_POLL_INTERVAL_SEC,
    DEFAULT_SERVICE_CONFIG_PATH,
    DEFAULT_TIMEOUT_MSEC,
    DEFAULT_TRACE_ENABLED,
    DEFAULT_TRACE_VERBOSE,
)
from service_config_loader import create_runtime_service_config


class AsyncSharedHakoniwaRpcDroneClient:
    _external_init_lock = threading.Lock()
    _external_initialized = False
    _runtime_lock = threading.Lock()
    _runtimes: dict[tuple[str, str, str, int], SharedRpcRuntime] = {}

    def __init__(
        self,
        drone_name: str = "Drone",
        service_config_path: Path | str = DEFAULT_SERVICE_CONFIG_PATH,
        *,
        asset_name: str = DEFAULT_ASSET_NAME,
        pdu_config_path: Path | str | None = None,
        offset_path: Path | str = DEFAULT_OFFSET_PATH,
        delta_time_usec: int = DEFAULT_DELTA_TIME_USEC,
        timeout_msec: int = DEFAULT_TIMEOUT_MSEC,
        poll_interval_sec: float = DEFAULT_POLL_INTERVAL_SEC,
    ) -> None:
        self.drone_name = drone_name
        self.service_config_path = Path(service_config_path).resolve()
        self.asset_name = asset_name
        self.offset_path = str(Path(offset_path).resolve())
        self.delta_time_usec = delta_time_usec
        self.timeout_msec = timeout_msec
        self.poll_interval_sec = poll_interval_sec
        self.trace_enabled = DEFAULT_TRACE_ENABLED
        self.trace_verbose = DEFAULT_TRACE_VERBOSE
        self.runtime_service_config_path = create_runtime_service_config(
            self.service_config_path
        )
        if pdu_config_path is None:
            runtime_service = json.loads(self.runtime_service_config_path.read_text())
            runtime_pdu_config_path = runtime_service.get("pdu_config_path")
            if not runtime_pdu_config_path:
                raise RuntimeError(
                    f"pdu_config_path is missing in runtime service config: {self.runtime_service_config_path}"
                )
            self.pdu_config_path = str(Path(runtime_pdu_config_path).resolve())
        else:
            self.pdu_config_path = str(Path(pdu_config_path).resolve())
        self._handles: dict[str, AsyncRpcClientHandle] = {}
        self._runtime = self._get_or_create_runtime()

    def _trace(self, message: str) -> None:
        if self.trace_enabled:
            print(f"TRACE_RPC_ASYNC_SHARED: {message}")

    @classmethod
    def _ensure_external_initialized(cls) -> None:
        with cls._external_init_lock:
            if cls._external_initialized:
                return
            ret = hakopy.init_for_external()
            if ret is False:
                raise RuntimeError("hakopy.init_for_external() failed")
            cls._external_initialized = True

    def _runtime_key(self) -> tuple[str, str, str, int]:
        return (
            self.asset_name,
            self.pdu_config_path,
            str(self.runtime_service_config_path),
            self.delta_time_usec,
        )

    def _get_or_create_runtime(self) -> SharedRpcRuntime:
        self._ensure_external_initialized()
        key = self._runtime_key()
        with self._runtime_lock:
            runtime = self._runtimes.get(key)
            if runtime is not None:
                return runtime
            runtime = SharedRpcRuntime(
                asset_name=self.asset_name,
                pdu_config_path=self.pdu_config_path,
                service_config_path=self.runtime_service_config_path,
                offset_path=self.offset_path,
                delta_time_usec=self.delta_time_usec,
                config=SharedRpcRuntimeConfig(mode="manual"),
            )
            self._runtimes[key] = runtime
            return runtime

    def _service_name(self, service_type: str) -> str:
        return f"DroneService/{service_type}/{self.drone_name}"

    def _client_name(self, service_type: str) -> str:
        safe_drone = "".join(ch if ch.isalnum() else "_" for ch in self.drone_name)
        return f"{service_type}AsyncSharedClient_{safe_drone}"

    def _get_handle(self, service_type: str) -> AsyncRpcClientHandle:
        handle = self._handles.get(service_type)
        if handle is not None:
            return handle
        # Profiling example:
        # with ScopedTimer(
        #     f"AsyncSharedHakoniwaRpcDroneClient._get_handle drone={self.drone_name} service={service_type}"
        # ):
        req_packet, res_packet, req_encoder, req_decoder, res_encoder, res_decoder = (
            _load_protocol_components(
                service_type, "hakoniwa_pdu.pdu_msgs.drone_srv_msgs"
            )
        )
        handle = AsyncRpcClientHandle(
            runtime=self._runtime,
            service_name=self._service_name(service_type),
            client_name=self._client_name(service_type),
            cls_req_packet=req_packet,
            req_encoder=req_encoder,
            req_decoder=req_decoder,
            cls_res_packet=res_packet,
            res_encoder=res_encoder,
            res_decoder=res_decoder,
        )
        handle.register()
        self._handles[service_type] = handle
        return handle

    def prepare_service(self, service_type: str) -> None:
        self._trace(
            f"prepare_service_start drone={self.drone_name} service={service_type}"
        )
        # Profiling example:
        # with ScopedTimer(
        #     f"AsyncSharedHakoniwaRpcDroneClient.prepare_service drone={self.drone_name} service={service_type}"
        # ):
        self._get_handle(service_type)
        self._trace(
            f"prepare_service_done drone={self.drone_name} service={service_type}"
        )

    def prepare_services(self, service_types: list[str]) -> None:
        for service_type in service_types:
            self.prepare_service(service_type)

    def prepare_all_basic_services(self) -> None:
        self.prepare_services(
            [
                "DroneSetReady",
                "DroneTakeOff",
                "DroneGoTo",
                "DroneGetState",
                "DroneLand",
            ]
        )

    def _call_async(
        self, service_type: str, request, *, timeout_msec: int | None = None
    ) -> RpcCallFuture:
        self._trace(f"call_async_start drone={self.drone_name} service={service_type}")
        handle = self._get_handle(service_type)
        effective_timeout_msec = (
            self.timeout_msec if timeout_msec is None else timeout_msec
        )
        future = handle.call_async(
            request,
            timeout_msec=effective_timeout_msec,
            poll_interval=max(self.poll_interval_sec, 0.0),
        )
        self._trace(
            "call_async_submitted "
            f"drone={self.drone_name} service={service_type} "
            f"service_id={future.service_id} client_id={future.client_id} request_id={future.request_id}"
        )
        return future

    def _call(self, service_type: str, request, *, timeout_msec: int | None = None):
        future = self._call_async(service_type, request, timeout_msec=timeout_msec)
        start = time.monotonic()
        polls = 0
        while not future.done():
            self._runtime.poll_once()
            polls += 1
            if self.poll_interval_sec > 0:
                time.sleep(self.poll_interval_sec)
            if self.timeout_msec >= 0:
                elapsed_msec = (time.monotonic() - start) * 1000.0
                if elapsed_msec > max(self.timeout_msec * 2, self.timeout_msec + 1000):
                    raise TimeoutError(
                        f"RPC wall timeout: drone={self.drone_name} service={service_type}"
                    )
        self._trace(
            f"call_done drone={self.drone_name} service={service_type} polls={polls}"
        )
        return future.result(timeout=0.0)

    def poll_once(self) -> int:
        return self._runtime.poll_once()

    def _restart_pdu_read_service(self) -> None:
        pass # No-op for async shared runtime, as it should be always running

    def set_ready_async(self) -> RpcCallFuture:
        req = DroneSetReadyRequest()
        req.drone_name = self.drone_name
        return self._call_async("DroneSetReady", req)

    def set_ready(self):
        req = DroneSetReadyRequest()
        req.drone_name = self.drone_name
        return self._call("DroneSetReady", req)

    def takeoff_async(self, alt_m: float) -> RpcCallFuture:
        req = DroneTakeOffRequest()
        req.drone_name = self.drone_name
        req.alt_m = alt_m
        return self._call_async("DroneTakeOff", req)

    def takeoff(self, alt_m: float):
        req = DroneTakeOffRequest()
        req.drone_name = self.drone_name
        req.alt_m = alt_m
        return self._call("DroneTakeOff", req)

    def get_state_async(self) -> RpcCallFuture:
        req = DroneGetStateRequest()
        req.drone_name = self.drone_name
        return self._call_async("DroneGetState", req)

    def get_state(self):
        req = DroneGetStateRequest()
        req.drone_name = self.drone_name
        return self._call("DroneGetState", req)

    def get_raw_pdu(self, pdu_name: str):
        last_error = None
        for attempt in range(3):
            try:
                if not self._runtime.manager.is_service_enabled():
                    if not self._runtime.manager.start_service_nowait():
                        raise RuntimeError("Failed to start PDU read service")
                self._runtime.manager.run_nowait()
                raw_data = self._runtime.manager.read_pdu_raw_data(
                    self.drone_name, pdu_name
                )
                if raw_data:
                    return raw_data
                self._runtime.manager.run_nowait()
                raw_data = self._runtime.manager.read_pdu_raw_data(
                    self.drone_name, pdu_name
                )
                if raw_data:
                    return raw_data
                last_error = RuntimeError(
                    f"Failed to read PDU raw data: drone={self.drone_name} pdu={pdu_name}"
                )
            except Exception as e:
                last_error = e
            if attempt < 2:
                self._restart_pdu_read_service()
                time.sleep(0.05)
        raise RuntimeError(
            f"Failed to read PDU raw data: drone={self.drone_name} pdu={pdu_name}"
        ) from last_error

    def get_status(self):
        from hakoniwa_pdu.pdu_msgs.hako_msgs.pdu_conv_DroneStatus import (
            pdu_to_py_DroneStatus,
        )

        return pdu_to_py_DroneStatus(self.get_raw_pdu("status"))

    def goto_async(
        self,
        x: float,
        y: float,
        z: float,
        yaw_deg: float = 0.0,
        *,
        speed_m_s: float = 1.0,
        tolerance_m: float = 0.5,
        timeout_sec: float = 30.0,
    ) -> RpcCallFuture:
        req = DroneGoToRequest()
        req.drone_name = self.drone_name
        req.target_pose = Vector3()
        req.target_pose.x = x
        req.target_pose.y = y
        req.target_pose.z = z
        req.speed_m_s = speed_m_s
        req.yaw_deg = yaw_deg
        req.tolerance_m = tolerance_m
        req.timeout_sec = timeout_sec
        return self._call_async("DroneGoTo", req)

    def goto(
        self,
        x: float,
        y: float,
        z: float,
        yaw_deg: float = 0.0,
        *,
        speed_m_s: float = 1.0,
        tolerance_m: float = 0.5,
        timeout_sec: float = 30.0,
    ):
        req = DroneGoToRequest()
        req.drone_name = self.drone_name
        req.target_pose = Vector3()
        req.target_pose.x = x
        req.target_pose.y = y
        req.target_pose.z = z
        req.speed_m_s = speed_m_s
        req.yaw_deg = yaw_deg
        req.tolerance_m = tolerance_m
        req.timeout_sec = timeout_sec
        return self._call("DroneGoTo", req)

    def land_async(self, timeout_sec: float = 0.0) -> RpcCallFuture:
        req = DroneLandRequest()
        req.drone_name = self.drone_name
        timeout_msec = int(timeout_sec * 1000) if timeout_sec > 0 else None
        return self._call_async("DroneLand", req, timeout_msec=timeout_msec)

    def land(self, timeout_sec: float = 0.0):
        req = DroneLandRequest()
        req.drone_name = self.drone_name
        timeout_msec = int(timeout_sec * 1000) if timeout_sec > 0 else None
        return self._call("DroneLand", req, timeout_msec=timeout_msec)


__all__ = ["AsyncSharedHakoniwaRpcDroneClient"]
