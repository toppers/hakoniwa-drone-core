#!/usr/bin/env python3
"""
Aggregate monitor CSV files by (label, drone_count, target_name).
"""

from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Aggregate perf monitor CSV files.")
    p.add_argument("--input", action="append", required=True, help="CSV file or directory (repeatable)")
    p.add_argument("--output", required=True, help="Output summary CSV")
    return p.parse_args()


def percentile(values: List[float], p: float) -> float:
    if not values:
        return float("nan")
    xs = sorted(values)
    if len(xs) == 1:
        return xs[0]
    idx = (len(xs) - 1) * p
    lo = math.floor(idx)
    hi = math.ceil(idx)
    if lo == hi:
        return xs[lo]
    return xs[lo] + (xs[hi] - xs[lo]) * (idx - lo)


def collect_csv_files(inputs: List[str]) -> List[Path]:
    files: List[Path] = []
    for raw in inputs:
        p = Path(raw)
        if p.is_file():
            files.append(p)
        elif p.is_dir():
            files.extend(sorted(p.rglob("*.csv")))
    return files


def safe_float(v: str) -> float:
    try:
        return float(v)
    except Exception:
        return float("nan")


def main() -> int:
    args = parse_args()
    files = collect_csv_files(args.input)
    groups: Dict[Tuple[str, int, str], Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))

    for f in files:
        with f.open() as fp:
            reader = csv.DictReader(fp)
            for row in reader:
                label = row.get("label", "unknown")
                drone_count = int(row.get("drone_count", "0"))
                target_name = row.get("target_name", "unknown")
                key = (label, drone_count, target_name)
                groups[key]["cpu_percent"].append(safe_float(row.get("cpu_percent", "")))
                groups[key]["rss_kb"].append(safe_float(row.get("rss_kb", "")))
                groups[key]["vsz_kb"].append(safe_float(row.get("vsz_kb", "")))
                groups[key]["thread_count"].append(safe_float(row.get("thread_count", "")))

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as fp:
        fieldnames = [
            "label",
            "drone_count",
            "target_name",
            "samples",
            "cpu_avg",
            "cpu_p95",
            "cpu_max",
            "rss_mb_avg",
            "rss_mb_p95",
            "vsz_mb_avg",
            "thread_avg",
        ]
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
        for (label, drone_count, target_name), metrics in sorted(groups.items(), key=lambda x: (x[0][0], x[0][1], x[0][2])):
            cpu = [v for v in metrics["cpu_percent"] if not math.isnan(v)]
            rss = [v for v in metrics["rss_kb"] if not math.isnan(v)]
            vsz = [v for v in metrics["vsz_kb"] if not math.isnan(v)]
            th = [v for v in metrics["thread_count"] if not math.isnan(v)]
            if not cpu:
                continue
            writer.writerow(
                {
                    "label": label,
                    "drone_count": drone_count,
                    "target_name": target_name,
                    "samples": len(cpu),
                    "cpu_avg": f"{sum(cpu)/len(cpu):.3f}",
                    "cpu_p95": f"{percentile(cpu, 0.95):.3f}",
                    "cpu_max": f"{max(cpu):.3f}",
                    "rss_mb_avg": f"{(sum(rss)/len(rss))/1024.0:.3f}" if rss else "",
                    "rss_mb_p95": f"{(percentile(rss, 0.95))/1024.0:.3f}" if rss else "",
                    "vsz_mb_avg": f"{(sum(vsz)/len(vsz))/1024.0:.3f}" if vsz else "",
                    "thread_avg": f"{sum(th)/len(th):.3f}" if th else "",
                }
            )
    print(f"[aggregate] wrote: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

