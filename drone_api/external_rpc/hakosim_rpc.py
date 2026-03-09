#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import os
import sys
import threading
import time
from pathlib import Path

import hakopy

REPO_ROOT = Path(__file__).resolve().parents[2]
HAKO_PDU_PYTHON_SRC = REPO_ROOT / "work" / "hakoniwa-pdu-python" / "src"
if str(HAKO_PDU_PYTHON_SRC) not in sys.path:
    sys.path.insert(0, str(HAKO_PDU_PYTHON_SRC))

from hakoniwa_pdu.rpc.auto_wire import make_protocol_client
from hakoniwa_pdu.rpc.protocol_client import ProtocolClientImmediate
from hakoniwa_pdu.rpc.shm.shm_pdu_service_client_manager import (
    ShmPduServiceClientManager,
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

from service_config_loader import create_runtime_service_config


DEFAULT_SERVICE_CONFIG_PATH = (
    REPO_ROOT / "config" / "drone" / "fleets" / "services" / "api-1-service.json"
)
DEFAULT_OFFSET_PATH = (
    REPO_ROOT
    / "thirdparty"
    / "hakoniwa-core-pro"
    / "hakoniwa-pdu-registry"
    / "pdu"
    / "offset"
)
DEFAULT_ASSET_NAME = "DroneExternalClient"
DEFAULT_DELTA_TIME_USEC = 100 * 1000
DEFAULT_TIMEOUT_MSEC = -1
DEFAULT_POLL_INTERVAL_SEC = -1
DEFAULT_REGISTER_RETRY_COUNT = int(os.getenv("HAKO_RPC_REGISTER_RETRY_COUNT", "60"))
DEFAULT_REGISTER_RETRY_INTERVAL_SEC = float(
    os.getenv("HAKO_RPC_REGISTER_RETRY_INTERVAL_SEC", "0.2")
)
DEFAULT_TRACE_ENABLED = os.getenv("HAKO_RPC_TRACE", "0").lower() in {
    "1",
    "true",
    "yes",
    "on",
}
DEFAULT_TRACE_VERBOSE = os.getenv("HAKO_RPC_TRACE_VERBOSE", "0").lower() in {
    "1",
    "true",
    "yes",
    "on",
}


def quaternion_to_euler_deg(
    w: float, x: float, y: float, z: float
) -> tuple[float, float, float]:
    t0 = 2.0 * (w * x + y * z)
    t1 = 1.0 - 2.0 * (x * x + y * y)
    roll = math.atan2(t0, t1)

    t2 = 2.0 * (w * y - z * x)
    t2 = 1.0 if t2 > 1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    pitch = math.asin(t2)

    t3 = 2.0 * (w * z + x * y)
    t4 = 1.0 - 2.0 * (y * y + z * z)
    yaw = math.atan2(t3, t4)
    return (math.degrees(roll), math.degrees(pitch), math.degrees(yaw))


class HakoniwaRpcDroneClient:
    _external_init_lock = threading.Lock()
    _external_initialized = False

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
        register_retry_count: int = DEFAULT_REGISTER_RETRY_COUNT,
        register_retry_interval_sec: float = DEFAULT_REGISTER_RETRY_INTERVAL_SEC,
    ) -> None:
        self.drone_name = drone_name
        self.service_config_path = Path(service_config_path).resolve()
        self.asset_name = asset_name
        self.offset_path = str(Path(offset_path))
        self.delta_time_usec = delta_time_usec
        self.timeout_msec = timeout_msec
        self.poll_interval_sec = poll_interval_sec
        self.register_retry_count = register_retry_count
        self.register_retry_interval_sec = register_retry_interval_sec
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
        self._initialized = False
        self._init_lock = threading.Lock()
        self._pdu_manager: ShmPduServiceClientManager | None = None
        self._clients: dict[str, object] = {}

    def _trace(self, message: str) -> None:
        if self.trace_enabled:
            print(f"TRACE_RPC: {message}")

    def _ensure_initialized(self) -> None:
        if self._initialized:
            return
        with self._init_lock:
            if self._initialized:
                return
            with HakoniwaRpcDroneClient._external_init_lock:
                if not HakoniwaRpcDroneClient._external_initialized:
                    ret = hakopy.init_for_external()
                    if ret is False:
                        raise RuntimeError("hakopy.init_for_external() failed")
                    HakoniwaRpcDroneClient._external_initialized = True
            self._pdu_manager = ShmPduServiceClientManager(
                asset_name=self.asset_name,
                pdu_config_path=self.pdu_config_path,
                offset_path=self.offset_path,
            )
            if (
                self._pdu_manager.initialize_services(
                    str(self.runtime_service_config_path), self.delta_time_usec
                )
                < 0
            ):
                raise RuntimeError("initialize_services() failed")
            self._initialized = True

    def _service_name(self, service_type: str) -> str:
        return f"DroneService/{service_type}/{self.drone_name}"

    def _client_name(self, service_type: str) -> str:
        safe_drone = "".join(ch if ch.isalnum() else "_" for ch in self.drone_name)
        return f"{service_type}Client_{safe_drone}"

    def _get_protocol_client(self, service_type: str):
        self._ensure_initialized()
        client = self._clients.get(service_type)
        if client is not None:
            return client
        assert self._pdu_manager is not None
        client = make_protocol_client(
            pdu_manager=self._pdu_manager,
            service_name=self._service_name(service_type),
            client_name=self._client_name(service_type),
            srv=service_type,
            pkg="hakoniwa_pdu.pdu_msgs.drone_srv_msgs",
            ProtocolClientClass=ProtocolClientImmediate,
        )
        t0 = time.time()
        self._trace(
            "register_start "
            f"drone={self.drone_name} service={service_type} "
            f"retry_max={self.register_retry_count}"
        )
        for attempt in range(self.register_retry_count):
            if client.register():
                self._clients[service_type] = client
                self._trace(
                    "register_ok "
                    f"drone={self.drone_name} service={service_type} "
                    f"attempt={attempt + 1} elapsed_sec={time.time() - t0:.3f}"
                )
                return client
            if self.trace_enabled and self.trace_verbose:
                self._trace(
                    "register_retry "
                    f"drone={self.drone_name} service={service_type} "
                    f"attempt={attempt + 1}/{self.register_retry_count}"
                )
            if attempt + 1 < self.register_retry_count:
                time.sleep(self.register_retry_interval_sec)
        self._trace(
            "register_fail "
            f"drone={self.drone_name} service={service_type} "
            f"elapsed_sec={time.time() - t0:.3f}"
        )
        raise RuntimeError(
            "Failed to register service client after retries: "
            f"{self._service_name(service_type)} "
            f"(retry_count={self.register_retry_count}, "
            f"retry_interval_sec={self.register_retry_interval_sec})"
        )

    def _call(self, service_type: str, request):
        t0 = time.time()
        self._trace(
            "call_start "
            f"drone={self.drone_name} service={service_type}"
        )
        client = self._get_protocol_client(service_type)
        response = client.call(
            request,
            timeout_msec=self.timeout_msec,
            poll_interval=self.poll_interval_sec,
        )
        if response is None:
            self._trace(
                "call_no_response "
                f"drone={self.drone_name} service={service_type} "
                f"elapsed_sec={time.time() - t0:.3f}"
            )
            raise RuntimeError(f"Service call returned no response: {service_type}")
        self._trace(
            "call_done "
            f"drone={self.drone_name} service={service_type} "
            f"elapsed_sec={time.time() - t0:.3f}"
        )
        return response

    def set_ready(self):
        req = DroneSetReadyRequest()
        req.drone_name = self.drone_name
        return self._call("DroneSetReady", req)

    def takeoff(self, alt_m: float):
        req = DroneTakeOffRequest()
        req.drone_name = self.drone_name
        req.alt_m = alt_m
        return self._call("DroneTakeOff", req)

    def get_state(self):
        req = DroneGetStateRequest()
        req.drone_name = self.drone_name
        return self._call("DroneGetState", req)

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

    def land(self):
        req = DroneLandRequest()
        req.drone_name = self.drone_name
        return self._call("DroneLand", req)


def print_response_elapsed(prefix: str, start_time: float) -> None:
    elapsed_sec = time.time() - start_time
    print(f"INFO: {prefix} elapsed_sec={elapsed_sec:.3f}")
