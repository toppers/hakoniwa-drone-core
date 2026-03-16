#!/usr/bin/env python3
"""
Generate fleet-scale current configs.

Outputs:
- config/drone/fleets/api-current.json
- config/pdudef/drone-pdudef-current.json
- config/drone/fleets/services/api-current-service.json
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate api-current and drone-pdudef-current by drone count.")
    p.add_argument("--drone-count", "-n", type=int, required=True, help="Number of drones (N >= 1)")
    p.add_argument(
        "--fleet-path",
        default="config/drone/fleets/api-current.json",
        help="Output path for fleet config",
    )
    p.add_argument(
        "--pdudef-path",
        default="config/pdudef/drone-pdudef-current.json",
        help="Output path for compact pdudef",
    )
    p.add_argument(
        "--service-config-path",
        default="config/drone/fleets/services/api-current-service.json",
        help="serviceConfigPath written into fleet json",
    )
    p.add_argument(
        "--service-out-path",
        default="config/drone/fleets/services/api-current-service.json",
        help="Output path for generated service config",
    )
    p.add_argument("--type-name", default="api", help="Drone type name in fleet json")
    p.add_argument(
        "--drone-name-prefix",
        default="Drone-",
        help="Drone name prefix. Names become '<prefix><ID>' (ID starts from 1).",
    )
    p.add_argument(
        "--ring-capacity",
        type=int,
        default=8,
        help="Max number of drones per ring (k)",
    )
    p.add_argument(
        "--ring-spacing-meter",
        type=float,
        default=2.0,
        help="Ring spacing in meters (dr)",
    )
    p.add_argument(
        "--layout",
        choices=["legacy-rings", "packed-rings"],
        default="legacy-rings",
        help="Spawn layout strategy. 'packed-rings' keeps swarm compact (center + 8r per ring).",
    )
    p.add_argument("--center-x", type=float, default=0.0)
    p.add_argument("--center-y", type=float, default=0.0)
    p.add_argument("--center-z", type=float, default=0.0)
    p.add_argument(
        "--angle-degree",
        nargs=3,
        type=float,
        metavar=("ROLL", "PITCH", "YAW"),
        default=[0.0, 0.0, 0.0],
        help="Initial angle_degree for each drone",
    )
    p.add_argument("--dry-run", action="store_true", help="Print generated JSON and do not write files")
    return p.parse_args()


def normalize_number(v: float) -> Any:
    if abs(v - round(v)) < 1e-12:
        return int(round(v))
    return float(v)


def build_positions(
    drone_count: int,
    layout: str,
    ring_capacity: int,
    ring_spacing: float,
    cx: float,
    cy: float,
    cz: float,
) -> list[list[Any]]:
    positions: list[list[Any]] = []

    if layout == "legacy-rings":
        for i in range(drone_count):
            ring_index = (i // ring_capacity) + 1
            slot_index = i % ring_capacity
            ring_first = (ring_index - 1) * ring_capacity
            slot_count = min(ring_capacity, drone_count - ring_first)
            if slot_count <= 0:
                slot_count = 1
            theta = 2.0 * math.pi * (slot_index / slot_count)
            r = ring_index * ring_spacing
            x = cx + r * math.cos(theta)
            y = cy + r * math.sin(theta)
            z = cz
            positions.append([normalize_number(x), normalize_number(y), normalize_number(z)])
        return positions

    # packed-rings:
    # - drone#1 at center
    # - ring r has capacity 8*r
    # This keeps high-density placement while avoiding too-large outer radius.
    if drone_count >= 1:
        positions.append([normalize_number(cx), normalize_number(cy), normalize_number(cz)])
    placed = 1
    ring_index = 1
    while placed < drone_count:
        slot_count = min(8 * ring_index, drone_count - placed)
        r = ring_index * ring_spacing
        for slot_index in range(slot_count):
            theta = 2.0 * math.pi * (slot_index / slot_count)
            x = cx + r * math.cos(theta)
            y = cy + r * math.sin(theta)
            z = cz
            positions.append([normalize_number(x), normalize_number(y), normalize_number(z)])
        placed += slot_count
        ring_index += 1
    return positions


def build_fleet_json(args: argparse.Namespace) -> dict[str, Any]:
    positions = build_positions(
        args.drone_count,
        args.layout,
        args.ring_capacity,
        args.ring_spacing_meter,
        args.center_x,
        args.center_y,
        args.center_z,
    )
    drones: list[dict[str, Any]] = []
    for i in range(args.drone_count):
        drone_id = i + 1
        drones.append(
            {
                "name": f"{args.drone_name_prefix}{drone_id}",
                "type": args.type_name,
                "position_meter": positions[i],
                "angle_degree": [normalize_number(v) for v in args.angle_degree],
            }
        )
    return {
        "serviceConfigPath": args.service_config_path,
        "types": {
            args.type_name: "config/drone/fleets/types/api.json",
        },
        "drones": drones,
    }


def build_pdudef_json(args: argparse.Namespace) -> dict[str, Any]:
    robots = [
        {
            "name": f"{args.drone_name_prefix}{i + 1}",
            "pdutypes_id": "drone_type",
        }
        for i in range(args.drone_count)
    ]
    return {
        "paths": [
            {"id": "drone_type", "path": "drone-pdutypes.json"},
        ],
        "robots": robots,
    }


def build_service_json(args: argparse.Namespace) -> dict[str, Any]:
    def service(
        drone_name: str,
        name: str,
        type_name: str,
        server_base: int,
        client_base: int,
    ) -> dict[str, Any]:
        return {
            "name": f"DroneService/{name}/{drone_name}",
            "type": type_name,
            "maxClients": 1,
            "pduSize": {
                "server": {"heapSize": 0, "baseSize": server_base},
                "client": {"heapSize": 0, "baseSize": client_base},
            },
        }

    services: list[dict[str, Any]] = []
    for i in range(args.drone_count):
        drone_name = f"{args.drone_name_prefix}{i + 1}"
        services.extend(
            [
                service(drone_name, "DroneSetReady", "drone_srv_msgs/DroneSetReady", 408, 408),
                service(drone_name, "DroneTakeOff", "drone_srv_msgs/DroneTakeOff", 416, 408),
                service(drone_name, "DroneGoTo", "drone_srv_msgs/DroneGoTo", 448, 408),
                service(drone_name, "DroneGetState", "drone_srv_msgs/DroneGetState", 408, 632),
                service(drone_name, "DroneLand", "drone_srv_msgs/DroneLand", 408, 408),
            ]
        )

    return {
        "pduMetaDataSize": 24,
        "pdu_config_path": str(args.pdudef_path),
        "services": services,
        "nodes": [],
    }


def write_json(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=True, indent=2) + "\n")


def main() -> int:
    args = parse_args()
    if args.drone_count < 1:
        raise SystemExit("--drone-count must be >= 1")
    if args.ring_capacity < 1:
        raise SystemExit("--ring-capacity must be >= 1")
    if args.ring_spacing_meter < 0:
        raise SystemExit("--ring-spacing-meter must be >= 0")

    fleet = build_fleet_json(args)
    pdudef = build_pdudef_json(args)
    service = build_service_json(args)

    if args.dry_run:
        print("# fleet")
        print(json.dumps(fleet, ensure_ascii=True, indent=2))
        print("# pdudef")
        print(json.dumps(pdudef, ensure_ascii=True, indent=2))
        print("# service")
        print(json.dumps(service, ensure_ascii=True, indent=2))
        return 0

    fleet_path = Path(args.fleet_path)
    pdudef_path = Path(args.pdudef_path)
    service_path = Path(args.service_out_path)
    write_json(fleet_path, fleet)
    write_json(pdudef_path, pdudef)
    write_json(service_path, service)
    print(f"[gen_fleet_scale_config] wrote fleet: {fleet_path}")
    print(f"[gen_fleet_scale_config] wrote pdudef: {pdudef_path}")
    print(f"[gen_fleet_scale_config] wrote service: {service_path}")
    print(f"[gen_fleet_scale_config] drones: {args.drone_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
