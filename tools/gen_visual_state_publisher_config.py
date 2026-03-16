#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate runtime config for visual-state-publisher.")
    p.add_argument(
        "--base-config",
        default="config/assets/visual_state_publisher/visual_state_publisher.json",
        help="Base visual-state-publisher config path",
    )
    p.add_argument(
        "--out",
        default="config/assets/visual_state_publisher/visual_state_publisher.runtime.json",
        help="Output runtime config path",
    )
    p.add_argument("--global-drone-count", type=int, default=0)
    p.add_argument("--global-start-index", type=int, default=0)
    p.add_argument("--local-start-index", type=int, default=0)
    p.add_argument("--local-drone-count", type=int, default=0)
    p.add_argument("--output-chunk-base-index", type=int, default=0)
    p.add_argument("--max-drones-per-packet", type=int, default=0)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    base_path = Path(args.base_config)
    out_path = Path(args.out)

    root = json.loads(base_path.read_text(encoding="utf-8"))
    root["global_drone_count"] = args.global_drone_count
    root["global_start_index"] = args.global_start_index
    root["local_start_index"] = args.local_start_index
    root["local_drone_count"] = args.local_drone_count
    root["output_chunk_base_index"] = args.output_chunk_base_index
    if args.max_drones_per_packet > 0:
        root["max_drones_per_packet"] = args.max_drones_per_packet

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(root, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print(f"[gen_visual_state_publisher_config] wrote: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
