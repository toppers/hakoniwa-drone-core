#!/usr/bin/env python3
"""
Estimate max drone count by linear approximation from summary CSV.
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Estimate max drone count from aggregated metrics.")
    p.add_argument("--input", required=True, help="aggregated CSV from aggregate_metrics.py")
    p.add_argument("--metric", default="cpu_p95", choices=["cpu_avg", "cpu_p95", "cpu_max"])
    p.add_argument("--limit", type=float, default=85.0, help="Threshold for metric (e.g., CPU percent)")
    p.add_argument("--output", required=True)
    return p.parse_args()


def linear_fit(xs: List[float], ys: List[float]) -> Tuple[float, float]:
    n = len(xs)
    if n < 2:
        return 0.0, ys[0] if ys else 0.0
    sx = sum(xs)
    sy = sum(ys)
    sxx = sum(x * x for x in xs)
    sxy = sum(x * y for x, y in zip(xs, ys))
    denom = n * sxx - sx * sx
    if denom == 0:
        return 0.0, sy / n
    a = (n * sxy - sx * sy) / denom
    b = (sy - a * sx) / n
    return a, b


def main() -> int:
    args = parse_args()
    rows: Dict[Tuple[str, str], List[Tuple[int, float]]] = defaultdict(list)
    with Path(args.input).open() as fp:
        reader = csv.DictReader(fp)
        for r in reader:
            label = r["label"]
            target = r["target_name"]
            x = int(r["drone_count"])
            y = float(r[args.metric])
            rows[(label, target)].append((x, y))

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as fp:
        writer = csv.DictWriter(
            fp,
            fieldnames=[
                "label",
                "target_name",
                "metric",
                "limit",
                "slope_per_drone",
                "intercept",
                "estimated_max_drones",
            ],
        )
        writer.writeheader()
        for (label, target), pts in sorted(rows.items(), key=lambda x: (x[0][0], x[0][1])):
            pts = sorted(pts, key=lambda p: p[0])
            xs = [float(p[0]) for p in pts]
            ys = [float(p[1]) for p in pts]
            a, b = linear_fit(xs, ys)
            if a <= 0:
                est = ""
            else:
                est_val = int((args.limit - b) / a)
                est = str(max(est_val, 0))
            writer.writerow(
                {
                    "label": label,
                    "target_name": target,
                    "metric": args.metric,
                    "limit": args.limit,
                    "slope_per_drone": f"{a:.6f}",
                    "intercept": f"{b:.6f}",
                    "estimated_max_drones": est,
                }
            )
    print(f"[estimate] wrote: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

