#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate drone icon formation points.")
    p.add_argument("--count", type=int, required=True, help="Total points")
    p.add_argument("--out", required=True, help="Output formation json path")
    p.add_argument("--id", default="DRONE_ICON", help="Formation id")
    p.add_argument("--size", type=float, default=8.0, help="Overall icon size")
    p.add_argument("--rotor-radius", type=float, default=0.25, help="Rotor radius ratio")
    p.add_argument(
        "--min-seg-points",
        type=int,
        default=8,
        help="Minimum points per segment",
    )
    return p.parse_args()


def sample_line(ax: float, ay: float, bx: float, by: float, n: int) -> list[list[float]]:
    if n <= 0:
        return []
    if n == 1:
        return [[(ax + bx) * 0.5, (ay + by) * 0.5, 0.0]]
    pts: list[list[float]] = []
    for i in range(n):
        t = i / (n - 1)
        pts.append([ax + (bx - ax) * t, ay + (by - ay) * t, 0.0])
    return pts


def sample_circle(cx: float, cy: float, r: float, n: int) -> list[list[float]]:
    if n <= 0:
        return []
    pts: list[list[float]] = []
    for i in range(n):
        th = (2.0 * math.pi * i) / n
        pts.append([cx + r * math.cos(th), cy + r * math.sin(th), 0.0])
    return pts


def allocate_counts(lengths: list[float], total: int, min_points: int) -> list[int]:
    if total <= 0:
        return [0] * len(lengths)
    if min_points < 1:
        min_points = 1
    required_min = len(lengths) * min_points
    if total < required_min:
        raise ValueError(
            f"point budget too small: total={total}, segments={len(lengths)}, "
            f"min_seg_points={min_points} requires >= {required_min}"
        )
    s = sum(lengths)
    if s <= 0:
        n = len(lengths)
        base = [min_points] * n
        remain = total - required_min
        for i in range(remain):
            base[i] += 1
        return base
    remain = total - required_min
    raw = [(l / s) * remain for l in lengths]
    counts = [min_points + int(round(v)) for v in raw]
    diff = total - sum(counts)
    n = len(counts)
    idx = 0
    while diff != 0 and idx < 10000:
        i = idx % n
        if diff > 0:
            counts[i] += 1
            diff -= 1
        else:
            if counts[i] > min_points:
                counts[i] -= 1
                diff += 1
        idx += 1
    return counts


def main() -> int:
    args = parse_args()
    if args.count <= 0:
        raise SystemExit("--count must be > 0")

    half = args.size * 0.5
    rotor_offset = half * 0.7
    rotor_r = half * args.rotor_radius

    line_defs = [
        (-rotor_offset, rotor_offset, rotor_offset, -rotor_offset),
        (-rotor_offset, -rotor_offset, rotor_offset, rotor_offset),
        (-rotor_offset, 0.0, rotor_offset, 0.0),
        (0.0, -rotor_offset, 0.0, rotor_offset),
    ]
    line_lengths = [math.hypot(x1 - x0, y1 - y0) for x0, y0, x1, y1 in line_defs]

    circle_centers = [
        (-rotor_offset, rotor_offset),
        (rotor_offset, rotor_offset),
        (-rotor_offset, -rotor_offset),
        (rotor_offset, -rotor_offset),
    ]
    circle_circ = 2.0 * math.pi * rotor_r
    geom_lengths = line_lengths + [circle_circ] * len(circle_centers)
    counts = allocate_counts(geom_lengths, args.count, args.min_seg_points)
    line_counts = counts[: len(line_defs)]
    circle_counts = counts[len(line_defs) :]

    points: list[list[float]] = []

    for (x0, y0, x1, y1), c in zip(line_defs, line_counts):
        points.extend(sample_line(x0, y0, x1, y1, c))
    for (cx, cy), c in zip(circle_centers, circle_counts):
        points.extend(sample_circle(cx, cy, rotor_r, c))

    if len(points) > args.count:
        points = points[: args.count]
    while len(points) < args.count:
        points.append(points[-1] if points else [0.0, 0.0, 0.0])

    out = {"id": args.id, "points": points}
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print(f"[gen-drone-icon] wrote: {out_path} points={len(points)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
