#!/usr/bin/env python3
"""
Render drone-show formations from a show JSON using matplotlib.

Outputs one PNG per timeline step.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt

from load_show_config import resolve_show_config


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Plot drone-show formations from show JSON.")
    p.add_argument("--input", required=True, help="Path to show JSON")
    p.add_argument("--out-dir", required=True, help="Output directory for PNG files")
    p.add_argument("--mode", choices=["2d", "3d"], default="2d", help="Plot mode")
    p.add_argument("--elev", type=float, default=25.0, help="3D view elevation")
    p.add_argument("--azim", type=float, default=45.0, help="3D view azimuth")
    p.add_argument("--show-labels", action="store_true", help="Show drone index labels")
    return p.parse_args()


def apply_transform(points, center, scale, base_alt):
    out = []
    for x, y, z in points:
        out.append(
            (
                center[0] + (x * scale),
                center[1] + (y * scale),
                center[2] + base_alt + (z * scale),
            )
        )
    return out


def main() -> int:
    args = parse_args()
    show_path = Path(args.input).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    resolved = resolve_show_config(show_path, enforce_drone_count=True)
    options = resolved.get("options", {})
    center = options.get("center", [0.0, 0.0, 0.0])
    scale = float(options.get("scale", 1.0))
    base_alt = float(options.get("base_alt", 0.0))
    formations = resolved["formations"]
    timeline = resolved["timeline"]

    for i, step in enumerate(timeline, start=1):
        fid = step["formation"]
        raw_points = formations[fid]["points"]
        points = apply_transform(raw_points, center, scale, base_alt)
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

            # Keep aspect roughly balanced
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
            # square limits with margin
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            span = max(max_x - min_x, max_y - min_y, 1.0)
            cx = (max_x + min_x) / 2.0
            cy = (max_y + min_y) / 2.0
            half = span / 2.0 + 0.5
            ax.set_xlim(cx - half, cx + half)
            ax.set_ylim(cy - half, cy + half)
            ax.grid(True, linestyle="--", alpha=0.3)

        ax.set_title(
            f"{resolved.get('meta', {}).get('name', 'show')} step={i} formation={fid} "
            f"dur={step['duration_sec']}s hold={step['hold_sec']}s"
        )

        out_path = out_dir / f"step-{i:02d}-{fid}.png"
        fig.tight_layout()
        fig.savefig(out_path, dpi=140)
        plt.close(fig)
        print(f"[plot-show] wrote: {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
