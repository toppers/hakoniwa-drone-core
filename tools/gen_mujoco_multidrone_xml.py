#!/usr/bin/env python3
"""Generate a multi-drone MuJoCo XML from a scene template and a drone body template."""

from __future__ import annotations

import argparse
from pathlib import Path
import textwrap


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate a multi-drone MuJoCo XML.")
    p.add_argument("--drone-count", "-n", type=int, required=True, help="Number of drones (N >= 1)")
    p.add_argument(
        "--drone-template-path",
        default="config/drone/fleets/types/mujoco-drone.xml.template",
        help="Input one-drone MuJoCo body fragment template",
    )
    p.add_argument(
        "--scene-template-path",
        default="config/drone/fleets/types/mujoco-scene.xml.template",
        help="Input MuJoCo scene template containing __DRONE_BODIES__",
    )
    p.add_argument(
        "--output-path",
        default="config/drone/fleets/types/mujoco-drone.generated.xml",
        help="Output path for generated MuJoCo XML",
    )
    p.add_argument("--dry-run", action="store_true", help="Print generated XML and do not write files")
    return p.parse_args()


def build_name_map(drone_id: int) -> dict[str, str]:
    prefix = f"d{drone_id}"
    mapping = {
        "__DRONE_BASE_NAME__": f"{prefix}_b_drone_base",
        "__FREEJOINT_NAME__": f"{prefix}_j_free",
        "__BASE_GEOM_NAME__": f"{prefix}_g_base",
    }

    for idx in range(1, 5):
        mapping[f"__ARM{idx}_BODY_NAME__"] = f"{prefix}_b_arm{idx}"
        mapping[f"__ARM{idx}_GEOM_NAME__"] = f"{prefix}_g_arm{idx}"
        mapping[f"__P{idx}_BODY_NAME__"] = f"{prefix}_b_p{idx}"
        mapping[f"__PROP{idx}_DISK_GEOM_NAME__"] = f"{prefix}_g_prop{idx}"
        mapping[f"__PROP{idx}_BODY_NAME__"] = f"{prefix}_b_prop{idx}"
        mapping[f"__PROP{idx}_BODY_GEOM_NAME__"] = f"{prefix}_g_p{idx}"
        mapping[f"__REG{idx}_BODY_NAME__"] = f"{prefix}_b_reg{idx}"
        mapping[f"__REG{idx}_GEOM_NAME__"] = f"{prefix}_g_reg{idx}"

    for idx in range(1, 3):
        mapping[f"__REG_BOTTOM{idx}_BODY_NAME__"] = f"{prefix}_b_reg_bottom{idx}"
        mapping[f"__REG_BOTTOM{idx}_GEOM_NAME__"] = f"{prefix}_g_reg_bottom{idx}"

    return mapping


def expand_template(template: str, drone_id: int) -> str:
    expanded = template
    for placeholder, value in build_name_map(drone_id).items():
        expanded = expanded.replace(placeholder, value)
    return expanded


def build_drone_bodies(template: str, drone_count: int) -> str:
    blocks = []
    for drone_id in range(1, drone_count + 1):
        blocks.append(f"    <!-- ========= Drone #{drone_id} ========= -->")
        blocks.append(textwrap.indent(expand_template(template, drone_id), "    "))
        blocks.append("")
    return "\n".join(blocks).rstrip() + "\n"


def generate_xml(scene_template: str, drone_template: str, drone_count: int) -> str:
    drone_bodies = build_drone_bodies(drone_template, drone_count)
    if "__DRONE_BODIES__" not in scene_template:
        raise SystemExit("scene template must contain __DRONE_BODIES__ placeholder")
    return scene_template.replace("__DRONE_BODIES__", drone_bodies.rstrip())


def main() -> int:
    args = parse_args()
    if args.drone_count < 1:
        raise SystemExit("--drone-count must be >= 1")

    drone_template_path = Path(args.drone_template_path)
    scene_template_path = Path(args.scene_template_path)
    drone_template = drone_template_path.read_text(encoding="utf-8").strip()
    scene_template = scene_template_path.read_text(encoding="utf-8").strip() + "\n"
    xml = generate_xml(scene_template, drone_template, args.drone_count)

    if args.dry_run:
        print(xml, end="")
        return 0

    output_path = Path(args.output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(xml, encoding="utf-8")
    print(f"[gen_mujoco_multidrone_xml] wrote xml: {output_path}")
    print(f"[gen_mujoco_multidrone_xml] drones: {args.drone_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
