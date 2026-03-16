#!/usr/bin/env python3
"""
Load and validate drone-show configuration JSON.

Supports:
- inline formations:   { "formations": { "A": { "points": [...] }, ... } }
- referenced files:    { "formation_files": [ { "id": "A", "path": "..." } ] }

Typical usage:
  python3 tools/drone-show/load_show_config.py \
    --input config/drone-show-config/show-h-a-16-ref.json \
    --output /tmp/show-resolved.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Load/validate/resolve drone-show JSON config.")
    p.add_argument("--input", required=True, help="Path to show JSON")
    p.add_argument("--output", help="Write resolved JSON to this path")
    p.add_argument(
        "--no-enforce-drone-count",
        action="store_true",
        help="Do not require each formation point count to equal meta.drone_count",
    )
    p.add_argument(
        "--print-resolved",
        action="store_true",
        help="Print resolved JSON to stdout",
    )
    return p.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        raise ValueError(f"File not found: {path}") from e
    try:
        obj = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {path}: {e}") from e
    if not isinstance(obj, dict):
        raise ValueError(f"Top-level JSON must be object: {path}")
    return obj


def _is_number(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _validate_points(points: Any, context: str) -> list[list[float]]:
    if not isinstance(points, list) or len(points) == 0:
        raise ValueError(f"{context}: points must be non-empty array")
    out: list[list[float]] = []
    for i, p in enumerate(points):
        if not isinstance(p, list) or len(p) != 3:
            raise ValueError(f"{context}: points[{i}] must be [x,y,z]")
        if not all(_is_number(v) for v in p):
            raise ValueError(f"{context}: points[{i}] must contain numeric x,y,z")
        out.append([float(p[0]), float(p[1]), float(p[2])])
    return out


def _validate_meta(meta: Any) -> int:
    if not isinstance(meta, dict):
        raise ValueError("meta must be object")
    drone_count = meta.get("drone_count")
    if not isinstance(drone_count, int) or drone_count <= 0:
        raise ValueError("meta.drone_count must be integer > 0")
    return drone_count


def _validate_timeline(timeline: Any, formation_ids: set[str]) -> list[dict[str, Any]]:
    if not isinstance(timeline, list) or len(timeline) == 0:
        raise ValueError("timeline must be non-empty array")
    out: list[dict[str, Any]] = []
    for i, step in enumerate(timeline):
        if not isinstance(step, dict):
            raise ValueError(f"timeline[{i}] must be object")
        formation = step.get("formation")
        duration = step.get("duration_sec")
        hold = step.get("hold_sec", 0.0)
        if not isinstance(formation, str) or formation == "":
            raise ValueError(f"timeline[{i}].formation must be non-empty string")
        if formation not in formation_ids:
            raise ValueError(f"timeline[{i}].formation '{formation}' not found in formations")
        if not _is_number(duration) or float(duration) <= 0:
            raise ValueError(f"timeline[{i}].duration_sec must be > 0")
        if not _is_number(hold) or float(hold) < 0:
            raise ValueError(f"timeline[{i}].hold_sec must be >= 0")
        out.append(
            {
                "formation": formation,
                "duration_sec": float(duration),
                "hold_sec": float(hold),
            }
        )
    return out


def _resolve_inline_formations(raw: Any) -> dict[str, list[list[float]]]:
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ValueError("formations must be object")
    out: dict[str, list[list[float]]] = {}
    for fid, body in raw.items():
        if not isinstance(fid, str) or fid == "":
            raise ValueError("formations key must be non-empty string")
        if not isinstance(body, dict):
            raise ValueError(f"formations['{fid}'] must be object")
        points = _validate_points(body.get("points"), f"formations['{fid}']")
        out[fid] = points
    return out


def _resolve_formation_files(raw: Any, base_dir: Path) -> dict[str, list[list[float]]]:
    if raw is None:
        return {}
    if not isinstance(raw, list):
        raise ValueError("formation_files must be array")
    out: dict[str, list[list[float]]] = {}
    for i, entry in enumerate(raw):
        if not isinstance(entry, dict):
            raise ValueError(f"formation_files[{i}] must be object")
        fid = entry.get("id")
        rel = entry.get("path")
        if not isinstance(fid, str) or fid == "":
            raise ValueError(f"formation_files[{i}].id must be non-empty string")
        if not isinstance(rel, str) or rel == "":
            raise ValueError(f"formation_files[{i}].path must be non-empty string")
        if fid in out:
            raise ValueError(f"Duplicate formation id in formation_files: {fid}")
        form_path = (base_dir / rel).resolve()
        form_obj = _load_json(form_path)
        form_id = form_obj.get("id", fid)
        if not isinstance(form_id, str) or form_id == "":
            raise ValueError(f"{form_path}: id must be non-empty string")
        if form_id != fid:
            raise ValueError(f"{form_path}: id mismatch (expected '{fid}', got '{form_id}')")
        out[fid] = _validate_points(form_obj.get("points"), f"{form_path}")
    return out


def resolve_show_config(show_path: Path, *, enforce_drone_count: bool = True) -> dict[str, Any]:
    root = _load_json(show_path)
    drone_count = _validate_meta(root.get("meta"))

    inline_formations = _resolve_inline_formations(root.get("formations"))
    file_formations = _resolve_formation_files(root.get("formation_files"), show_path.parent)

    formations: dict[str, list[list[float]]] = {}
    for fid, points in inline_formations.items():
        formations[fid] = points
    for fid, points in file_formations.items():
        if fid in formations:
            raise ValueError(f"Duplicate formation id across formations/formation_files: {fid}")
        formations[fid] = points

    if not formations:
        raise ValueError("No formations defined (formations and formation_files are both empty)")

    if enforce_drone_count:
        for fid, points in formations.items():
            if len(points) != drone_count:
                raise ValueError(
                    f"Formation '{fid}' point count ({len(points)}) != meta.drone_count ({drone_count})"
                )

    timeline = _validate_timeline(root.get("timeline"), set(formations.keys()))

    resolved_formations = {fid: {"points": points} for fid, points in formations.items()}

    resolved = dict(root)
    resolved["formations"] = resolved_formations
    resolved["timeline"] = timeline
    resolved.pop("formation_files", None)
    return resolved


def main() -> int:
    args = parse_args()
    show_path = Path(args.input).resolve()
    try:
        resolved = resolve_show_config(
            show_path, enforce_drone_count=not args.no_enforce_drone_count
        )
    except ValueError as e:
        print(f"[show-loader] ERROR: {e}", file=sys.stderr)
        return 1

    formations = resolved.get("formations", {})
    timeline = resolved.get("timeline", [])
    drone_count = resolved.get("meta", {}).get("drone_count")
    print(
        "[show-loader] OK: "
        f"name={resolved.get('meta', {}).get('name', 'unknown')} "
        f"drone_count={drone_count} "
        f"formations={len(formations)} "
        f"timeline_steps={len(timeline)}"
    )

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(resolved, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
        print(f"[show-loader] wrote: {out_path}")

    if args.print_resolved:
        print(json.dumps(resolved, ensure_ascii=True, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

