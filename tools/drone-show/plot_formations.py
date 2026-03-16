#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Plot formation JSON files.")
    p.add_argument(
        "--inputs",
        nargs="+",
        required=True,
        help="Formation JSON files (e.g. formation-H-100.json formation-A-100.json)",
    )
    p.add_argument("--out-dir", required=True, help="Output directory for PNG files")
    p.add_argument("--mode", choices=["2d", "3d"], default="2d")
    p.add_argument("--show-labels", action="store_true")
    p.add_argument("--elev", type=float, default=25.0, help="3D elevation")
    p.add_argument("--azim", type=float, default=45.0, help="3D azimuth")
    return p.parse_args()


def load_formation(path: Path) -> tuple[str, list[list[float]]]:
    obj: Any = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError(f"{path}: top-level must be object")
    fid = obj.get("id")
    points = obj.get("points")
    if not isinstance(fid, str) or fid == "":
        raise ValueError(f"{path}: id must be non-empty string")
    if not isinstance(points, list) or not points:
        raise ValueError(f"{path}: points must be non-empty list")
    out: list[list[float]] = []
    for i, p in enumerate(points):
        if not isinstance(p, list) or len(p) != 3:
            raise ValueError(f"{path}: points[{i}] must be [x,y,z]")
        out.append([float(p[0]), float(p[1]), float(p[2])])
    return fid, out


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    for raw in args.inputs:
        path = Path(raw).resolve()
        fid, points = load_formation(path)

        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        zs = [p[2] for p in points]

        fig = plt.figure(figsize=(8, 6))
        if args.mode == "3d":
            ax = fig.add_subplot(111, projection="3d")
            ax.scatter(xs, ys, zs, s=25)
            if args.show_labels:
                for idx, (x, y, z) in enumerate(points, start=1):
                    ax.text(x, y, z, str(idx), fontsize=6)
            ax.set_xlabel("X [m]")
            ax.set_ylabel("Y [m]")
            ax.set_zlabel("Z [m]")
            ax.view_init(elev=args.elev, azim=args.azim)
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            min_z, max_z = min(zs), max(zs)
            span = max(max_x - min_x, max_y - min_y, max_z - min_z, 1.0)
            cx = (max_x + min_x) / 2.0
            cy = (max_y + min_y) / 2.0
            cz = (max_z + min_z) / 2.0
            half = span / 2.0
            ax.set_xlim(cx - half, cx + half)
            ax.set_ylim(cy - half, cy + half)
            ax.set_zlim(cz - half, cz + half)
        else:
            ax = fig.add_subplot(111)
            ax.scatter(xs, ys, s=25)
            if args.show_labels:
                for idx, (x, y, _z) in enumerate(points, start=1):
                    ax.text(x, y, str(idx), fontsize=6)
            ax.set_xlabel("X [m]")
            ax.set_ylabel("Y [m]")
            ax.set_aspect("equal", adjustable="box")
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            span = max(max_x - min_x, max_y - min_y, 1.0)
            cx = (max_x + min_x) / 2.0
            cy = (max_y + min_y) / 2.0
            half = span / 2.0 + 0.5
            ax.set_xlim(cx - half, cx + half)
            ax.set_ylim(cy - half, cy + half)
            ax.grid(True, linestyle="--", alpha=0.3)

        ax.set_title(f"formation={fid} points={len(points)}")
        out_path = out_dir / f"formation-{fid}.png"
        fig.tight_layout()
        fig.savefig(out_path, dpi=140)
        plt.close(fig)
        print(f"[plot-formations] wrote: {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

