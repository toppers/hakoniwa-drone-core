#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HAKO_PDU_PYTHON_SRC = REPO_ROOT / "work" / "hakoniwa-pdu-python" / "src"
if str(HAKO_PDU_PYTHON_SRC) not in sys.path:
    sys.path.insert(0, str(HAKO_PDU_PYTHON_SRC))

import hakopy
from hakoniwa_pdu.rpc.auto_wire import _load_protocol_components
from hakoniwa_pdu.rpc.async_shared import AsyncRpcClientHandle, SharedRpcRuntime
from hakoniwa_pdu.pdu_msgs.drone_srv_msgs.pdu_pytype_DroneGoToRequest import (
    DroneGoToRequest,
)
from hakoniwa_pdu.pdu_msgs.drone_srv_msgs.pdu_pytype_DroneGetStateRequest import (
    DroneGetStateRequest,
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
    DEFAULT_SERVICE_CONFIG_PATH,
    quaternion_to_euler_deg,
)
from service_config_loader import create_runtime_service_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="async_shared smoke test")
    parser.add_argument(
        "--service-config",
        dest="service_config_path",
        type=Path,
        default=DEFAULT_SERVICE_CONFIG_PATH,
    )
    parser.add_argument("--drone-name", default="Drone-1")
    parser.add_argument(
        "--op",
        choices=["get-state", "set-ready", "takeoff", "goto"],
        default="get-state",
    )
    parser.add_argument("--wall-timeout-sec", type=float, default=10.0)
    parser.add_argument("--poll-sleep-sec", type=float, default=0.001)
    parser.add_argument("--alt-m", type=float, default=0.5)
    parser.add_argument("--x", type=float, default=0.0)
    parser.add_argument("--y", type=float, default=0.0)
    parser.add_argument("--z", type=float, default=0.5)
    parser.add_argument("--yaw-deg", type=float, default=0.0)
    parser.add_argument("--speed-m-s", type=float, default=1.0)
    parser.add_argument("--tolerance-m", type=float, default=0.5)
    parser.add_argument("--timeout-sec", type=float, default=30.0)
    return parser.parse_args()


def build_runtime(service_config_path: Path) -> tuple[SharedRpcRuntime, Path]:
    runtime_service_config_path = create_runtime_service_config(service_config_path)
    runtime_service = json.loads(runtime_service_config_path.read_text())
    pdu_config_path = Path(runtime_service["pdu_config_path"]).resolve()
    runtime = SharedRpcRuntime(
        asset_name=DEFAULT_ASSET_NAME,
        pdu_config_path=pdu_config_path,
        service_config_path=runtime_service_config_path,
        offset_path=DEFAULT_OFFSET_PATH,
        delta_time_usec=DEFAULT_DELTA_TIME_USEC,
    )
    return runtime, runtime_service_config_path


def build_client(runtime: SharedRpcRuntime, drone_name: str, op: str) -> AsyncRpcClientHandle:
    if op == "get-state":
        service_type = "DroneGetState"
    elif op == "set-ready":
        service_type = "DroneSetReady"
    elif op == "takeoff":
        service_type = "DroneTakeOff"
    elif op == "goto":
        service_type = "DroneGoTo"
    else:
        raise ValueError(f"unsupported op: {op}")

    req_packet, res_packet, req_encoder, req_decoder, res_encoder, res_decoder = (
        _load_protocol_components(
            service_type, "hakoniwa_pdu.pdu_msgs.drone_srv_msgs"
        )
    )
    return AsyncRpcClientHandle(
        runtime=runtime,
        service_name=f"DroneService/{service_type}/{drone_name}",
        client_name=f"{service_type}AsyncSharedClient_{drone_name.replace('-', '_')}",
        cls_req_packet=req_packet,
        req_encoder=req_encoder,
        req_decoder=req_decoder,
        cls_res_packet=res_packet,
        res_encoder=res_encoder,
        res_decoder=res_decoder,
    )


def build_request(args: argparse.Namespace):
    drone_name = args.drone_name
    op = args.op
    if op == "get-state":
        req = DroneGetStateRequest()
    elif op == "set-ready":
        req = DroneSetReadyRequest()
    elif op == "takeoff":
        req = DroneTakeOffRequest()
        req.alt_m = args.alt_m
    elif op == "goto":
        req = DroneGoToRequest()
        req.target_pose = Vector3()
        req.target_pose.x = args.x
        req.target_pose.y = args.y
        req.target_pose.z = args.z
        req.speed_m_s = args.speed_m_s
        req.yaw_deg = args.yaw_deg
        req.tolerance_m = args.tolerance_m
        req.timeout_sec = args.timeout_sec
    else:
        raise ValueError(f"unsupported op: {op}")
    req.drone_name = drone_name
    return req


def print_response(op: str, response) -> None:
    if op == "get-state":
        pos = response.current_pose.position
        roll_deg, pitch_deg, yaw_deg = quaternion_to_euler_deg(
            response.current_pose.orientation.w,
            response.current_pose.orientation.x,
            response.current_pose.orientation.y,
            response.current_pose.orientation.z,
        )
        print(
            "INFO: response "
            f"ok={response.ok} "
            f"is_ready={response.is_ready} "
            f"mode={response.mode} "
            f"message={response.message} "
            f"position=({pos.x}, {pos.y}, {pos.z}) "
            f"angle_deg=({roll_deg}, {pitch_deg}, {yaw_deg})"
        )
        return
    if op == "set-ready":
        print(f"INFO: response ok={response.ok} message={response.message}")
        return
    if op == "takeoff":
        print(f"INFO: response ok={response.ok} message={response.message}")
        return
    if op == "goto":
        print(f"INFO: response ok={response.ok} message={response.message}")
        return
    raise ValueError(f"unsupported op: {op}")


def main() -> int:
    args = parse_args()
    ret = hakopy.init_for_external()
    if ret is False:
        raise RuntimeError("hakopy.init_for_external() failed")
    service_config_path = args.service_config_path.resolve()
    runtime, runtime_service_config_path = build_runtime(service_config_path)
    client = build_client(runtime, args.drone_name, args.op)
    client.register()
    request = build_request(args)

    print(f"INFO: runtime_service_config={runtime_service_config_path}")
    print(f"INFO: request op={args.op} drone={args.drone_name}")
    future = client.call_async(request)

    deadline = time.monotonic() + args.wall_timeout_sec
    polls = 0
    while not future.done():
        runtime.poll_once()
        polls += 1
        if time.monotonic() >= deadline:
            raise TimeoutError(
                f"future did not complete within wall timeout: {args.wall_timeout_sec} sec"
            )
        if args.poll_sleep_sec > 0:
            time.sleep(args.poll_sleep_sec)

    print(f"INFO: future_done polls={polls}")
    response = future.result(timeout=0.0)
    print_response(args.op, response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
