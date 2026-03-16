#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Split fleet/service config into N parts.")
    p.add_argument(
        "--fleet-in",
        default="config/drone/fleets/api-current.json",
        help="Input fleet json",
    )
    p.add_argument(
        "--service-in",
        default="config/drone/fleets/services/api-current-service.json",
        help="Input service json",
    )
    p.add_argument(
        "--fleet-out-template",
        default="config/drone/fleets/api-current-part{part}.json",
        help="Output fleet path template with {part}",
    )
    p.add_argument(
        "--service-out-template",
        default="config/drone/fleets/services/api-current-service-part{part}.json",
        help="Output service path template with {part}",
    )
    p.add_argument(
        "--parts",
        type=int,
        default=2,
        help="Number of split parts (N >= 2)",
    )
    p.add_argument(
        "--part1-count",
        type=int,
        default=0,
        help="Drone count in part1 (backward compatibility for 2 parts only)",
    )
    p.add_argument(
        "--shared-service-config-path",
        default="config/drone/fleets/services/api-current-service.json",
        help="serviceConfigPath written into split fleet jsons. "
        "Use shared full service config to keep global service_id mapping across processes.",
    )
    return p.parse_args()


def write_json(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    fleet_path = Path(args.fleet_in)
    service_path = Path(args.service_in)
    fleet = json.loads(fleet_path.read_text(encoding="utf-8"))
    service = json.loads(service_path.read_text(encoding="utf-8"))

    drones = list(fleet.get("drones", []))
    if len(drones) < 2:
        raise SystemExit("drone count must be >= 2")
    if args.parts < 2:
        raise SystemExit("--parts must be >= 2")
    if args.parts > len(drones):
        raise SystemExit(f"--parts must be <= drone count ({len(drones)})")

    parts: list[list[dict[str, Any]]] = []
    if args.part1_count > 0:
        if args.parts != 2:
            raise SystemExit("--part1-count can be used only with --parts 2")
        part1_count = args.part1_count
        if part1_count <= 0 or part1_count >= len(drones):
            raise SystemExit(f"invalid --part1-count: {part1_count}")
        parts = [drones[:part1_count], drones[part1_count:]]
    else:
        base = len(drones) // args.parts
        rem = len(drones) % args.parts
        start = 0
        for i in range(args.parts):
            size = base + (1 if i < rem else 0)
            end = start + size
            parts.append(drones[start:end])
            start = end
    service_map = {s["name"]: s for s in service.get("services", [])}
    service_base = {k: v for k, v in service.items() if k != "services"}
    ops = ["DroneSetReady", "DroneTakeOff", "DroneGoTo", "DroneGetState", "DroneLand"]

    for idx, ds in enumerate(parts, start=1):
        out_fleet = dict(fleet)
        out_fleet["serviceConfigPath"] = args.shared_service_config_path
        out_fleet["drones"] = ds

        out_services: list[dict[str, Any]] = []
        for d in ds:
            dname = d["name"]
            for op in ops:
                key = f"DroneService/{op}/{dname}"
                if key not in service_map:
                    raise SystemExit(f"service not found: {key}")
                out_services.append(service_map[key])

        out_service = dict(service_base)
        out_service["services"] = out_services

        out_fleet_path = Path(args.fleet_out_template.format(part=idx))
        out_service_path = Path(args.service_out_template.format(part=idx))
        write_json(out_fleet_path, out_fleet)
        write_json(out_service_path, out_service)
        print(
            f"[gen_fleet_split_config] part={idx} "
            f"drones={len(ds)} services={len(out_services)} "
            f"fleet={out_fleet_path} service={out_service_path}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
