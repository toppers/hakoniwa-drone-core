#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate fleets-scale-perf launcher config for N drone-service processes.")
    p.add_argument("--proc-count", type=int, required=True, help="Number of drone-service processes (N >= 1)")
    p.add_argument(
        "--out",
        default="config/launcher/fleets-scale-perf-nproc.generated.launch.json",
        help="Output launcher json path",
    )
    p.add_argument(
        "--fleet-part-template",
        default="config/drone/fleets/api-current-part{part}.json",
        help="Fleet split path template with {part}",
    )
    p.add_argument(
        "--single-fleet",
        default="config/drone/fleets/api-current.json",
        help="Fleet path when proc-count=1",
    )
    p.add_argument(
        "--pdudef-path",
        default="config/pdudef/drone-pdudef-current.json",
        help="PDU def path argument for drone service",
    )
    p.add_argument(
        "--drone-service-command",
        default="${HAKO_DRONE_SERVICE_BIN}",
        help="Drone service executable path written into launch json",
    )
    p.add_argument(
        "--show-asset-json",
        default="",
        help="Optional show JSON path for asset-based show runner",
    )
    p.add_argument(
        "--show-asset-drone-count",
        type=int,
        default=0,
        help="Drone count passed to show asset runner",
    )
    p.add_argument(
        "--show-asset-assign-mode",
        default="nearest",
        help="Assign mode for show asset runner",
    )
    p.add_argument(
        "--show-asset-speed",
        type=float,
        default=14.0,
        help="GoTo speed for show asset runner",
    )
    p.add_argument(
        "--show-asset-timeout-sec",
        type=float,
        default=120.0,
        help="Per-command timeout for show asset runner",
    )
    p.add_argument(
        "--show-asset-delta-time-msec",
        type=int,
        default=20,
        help="Manual timing control interval for show asset runner",
    )
    p.add_argument(
        "--show-asset-final-hold-extra-sec",
        type=float,
        default=5.0,
        help="Extra hold time added only to the last formation",
    )
    p.add_argument(
        "--show-asset-z-offset-m",
        type=float,
        default=0.0,
        help="Additional Z offset applied to all formation points",
    )
    p.add_argument(
        "--show-asset-name",
        default="ShowRunnerAsset",
        help="Hakoniwa asset name for show asset runner",
    )
    p.add_argument(
        "--show-asset-summary-json",
        default="",
        help="Optional summary JSON output path for show asset runner",
    )
    p.add_argument(
        "--disable-viewer-webserver",
        action="store_true",
        help="Do not add threejs-viewer-webserver asset",
    )
    p.add_argument(
        "--disable-web-bridge",
        action="store_true",
        help="Do not add web-bridge-fleets asset",
    )
    p.add_argument(
        "--disable-visual-state-publisher",
        action="store_true",
        help="Do not add visual-state-publisher asset",
    )
    p.add_argument(
        "--visual-state-publisher-config",
        default="config/assets/visual_state_publisher/visual_state_publisher.json",
        help="visual-state-publisher config path written into launch json",
    )
    p.add_argument(
        "--visual-state-publisher-command",
        default="${HAKO_VISUAL_STATE_PUBLISHER_BIN}",
        help="visual-state-publisher executable path written into launch json",
    )
    p.add_argument(
        "--conductor-server-script",
        default="",
        help="Optional conductor server launcher script path",
    )
    p.add_argument(
        "--conductor-server-id",
        default="1",
        help="Server node id passed to conductor server launcher script",
    )
    p.add_argument(
        "--conductor-mode",
        default="simple",
        help="Conductor mode passed to conductor launcher script",
    )
    p.add_argument(
        "--conductor-config-root",
        default="",
        help="Optional conductor generated config root passed to conductor launcher script",
    )
    return p.parse_args()


def write_json(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def build_drone_service_assets(args: argparse.Namespace) -> list[dict[str, Any]]:
    assets: list[dict[str, Any]] = []
    n = args.proc_count
    force_disable_conductor = bool(args.conductor_server_script)
    for i in range(1, n + 1):
        name = f"drone-service-{i}"
        fleet_path = args.single_fleet if n == 1 else args.fleet_part_template.format(part=i)
        asset_args = [
            fleet_path,
            args.pdudef_path,
        ]
        if n >= 2 or force_disable_conductor:
            asset_args += ["--asset-name", f"drone-{i}"]
            if force_disable_conductor or i >= 2:
                asset_args += ["--disable-conductor"]
        asset: dict[str, Any] = {
            "name": name,
            "activation_timing": "before_start",
            "command": args.drone_service_command,
            "args": asset_args,
            "cwd": "${HAKO_DRONE_PROJECT_PATH}",
            "delay_sec": 2 if i == 1 else 1,
        }
        if i >= 2:
            asset["depends_on"] = [f"drone-service-{i-1}"]
        assets.append(asset)
    return assets


def build_launch(args: argparse.Namespace) -> dict[str, Any]:
    drone_assets = build_drone_service_assets(args)
    drone_names = [a["name"] for a in drone_assets]
    before_start_assets: list[dict[str, Any]] = []

    if args.conductor_server_script:
        conductor_args = [
            args.conductor_server_script,
            str(args.conductor_server_id),
            args.conductor_mode,
        ]
        if args.conductor_config_root:
            conductor_args.append(args.conductor_config_root)
        before_start_assets.append(
            {
                "name": "conductor-server",
                "activation_timing": "before_start",
                "command": "bash",
                "args": conductor_args,
                "cwd": "${HAKO_DRONE_PROJECT_PATH}",
                "delay_sec": 1,
            }
        )

    if args.conductor_server_script:
        for i, asset in enumerate(drone_assets):
            patched = dict(asset)
            if i == 0:
                patched["depends_on"] = ["conductor-server"]
            before_start_assets.append(patched)
    else:
        before_start_assets.extend(drone_assets)

    if args.show_asset_json:
        show_asset_args = [
            "drone_api/external_rpc/run_show_asset.bash",
            "--service-config",
            "config/drone/fleets/services/api-current-service.json",
            "--show-json",
            args.show_asset_json,
            "--drone-count",
            str(args.show_asset_drone_count),
            "--asset-name",
            args.show_asset_name,
            "--proc-count",
            str(args.proc_count),
            "--assign-mode",
            args.show_asset_assign_mode,
            "--speed",
            str(args.show_asset_speed),
            "--timeout-sec",
            str(args.show_asset_timeout_sec),
            "--delta-time-msec",
            str(args.show_asset_delta_time_msec),
            "--final-hold-extra-sec",
            str(args.show_asset_final_hold_extra_sec),
            "--z-offset-m",
            str(args.show_asset_z_offset_m),
        ]
        if args.show_asset_summary_json:
            show_asset_args += ["--summary-json", args.show_asset_summary_json]
        before_start_assets.append(
            {
                "name": "show-asset-runner",
                "activation_timing": "before_start",
                "command": "bash",
                "args": show_asset_args,
                "cwd": "${HAKO_DRONE_PROJECT_PATH}",
                "env": {
                    "prepend": {
                        "PYTHONPATH": [
                            "${HAKO_DRONE_PROJECT_PATH}/work/hakoniwa-pdu-python/src"
                        ]
                    }
                },
                "depends_on": [before_start_assets[-1]["name"]],
                "delay_sec": 1,
            }
        )

    before_start_tail = before_start_assets[-1]["name"]
    before_start_follow = before_start_tail
    after_start_follow = before_start_tail

    visual_assets: list[dict[str, Any]] = []
    if not args.disable_visual_state_publisher:
        visual_assets.append(
            {
                    "name": "visual-state-publisher",
                    "activation_timing": "before_start",
                    "command": args.visual_state_publisher_command,
                    "args": [
                    args.visual_state_publisher_config
                    ],
                    "cwd": "${HAKO_DRONE_PROJECT_PATH}",
                    "depends_on": [before_start_follow],
                    "delay_sec": 2,
                }
        )
        before_start_follow = "visual-state-publisher"
        after_start_follow = "visual-state-publisher"

    if not args.disable_web_bridge:
        bridge_dep = "visual-state-publisher" if not args.disable_visual_state_publisher else before_start_follow
        visual_assets.append(
            {
                "name": "web-bridge-fleets",
                "activation_timing": "before_start",
                "command": "/usr/local/hakoniwa/bin/hakoniwa-pdu-web-bridge",
                "args": [
                    "--config-root",
                    "/usr/local/hakoniwa/share/hakoniwa-pdu-bridge/config/web_bridge_fleets",
                    "--node-name",
                    "web_bridge_fleets_node1",
                    "--delta-time-step-usec",
                    "20000",
                    "--enable-ondemand",
                ],
                "cwd": "${HAKO_DRONE_PROJECT_PATH}",
                "depends_on": [bridge_dep],
            }
        )
        before_start_follow = "web-bridge-fleets"
        after_start_follow = "web-bridge-fleets"

    after_start_assets: list[dict[str, Any]] = []
    if not args.disable_viewer_webserver:
        after_start_assets.append(
            {
                "name": "threejs-viewer-webserver",
                "activation_timing": "after_start",
                "command": "python3",
                "args": ["-m", "http.server", "8000"],
                "cwd": "${HAKO_THREEJS_VIEWER_PATH}",
                "depends_on": [after_start_follow],
            }
        )

    launch: dict[str, Any] = {
        "version": "0.1",
        "defaults": {
            "cwd": ".",
            "stdout": "logs/${asset}.out",
            "stderr": "logs/${asset}.err",
            "start_grace_sec": 1,
            "delay_sec": 1,
            "env": {
                "set": {
                    "HAKO_PROFILE_SERVICE_CLIENT": "${HAKO_PROFILE_SERVICE_CLIENT:-0}",
                },
                "prepend": {
                    "lib_path": ["/usr/local/hakoniwa/lib"],
                    "PATH": ["/usr/local/hakoniwa/bin"],
                }
            },
        },
        "assets": before_start_assets
        + visual_assets
        + after_start_assets
        + [
            {
                "name": "perf-monitor",
                "activation_timing": "after_start",
                "command": "bash",
                "args": [
                    "tools/start-perf-monitor.bash",
                    "${FLEET_DRONE_COUNT:-1}",
                    "${PERF_LABEL:-fleets_scale_n1}",
                    "${PERF_DURATION_SEC:-86400}",
                ],
                "cwd": "${HAKO_DRONE_PROJECT_PATH}",
                "depends_on": [after_start_follow],
            },
            {
                "name": "host-perf-monitor",
                "activation_timing": "after_start",
                "command": "bash",
                "args": [
                    "tools/start-host-perf-monitor.bash",
                    "${FLEET_DRONE_COUNT:-1}",
                    "${PERF_LABEL:-fleets_scale_n1}",
                    "${PERF_DURATION_SEC:-86400}",
                ],
                "cwd": "${HAKO_DRONE_PROJECT_PATH}",
                "depends_on": [after_start_follow],
            },
        ],
    }
    return launch


def main() -> int:
    args = parse_args()
    if args.proc_count < 1:
        raise SystemExit("--proc-count must be >= 1")
    launch = build_launch(args)
    out_path = Path(args.out)
    write_json(out_path, launch)
    print(f"[gen_fleet_nproc_launch] wrote: {out_path} (proc_count={args.proc_count})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
