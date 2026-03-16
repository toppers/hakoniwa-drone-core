#!/usr/bin/env python3
"""
Plot scale-performance graphs from aggregate summary CSV.
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Plot scale-performance graphs from summary CSV.")
    p.add_argument("--input", required=True, help="Input summary CSV from aggregate_metrics.py")
    p.add_argument("--output-dir", required=True, help="Output directory for PNG files")
    p.add_argument(
        "--targets",
        nargs="+",
        default=["sim", "vsp", "bridge", "host"],
        help="Target names to plot (default: sim vsp bridge host)",
    )
    return p.parse_args()


def safe_float(v: str) -> float:
    try:
        return float(v)
    except Exception:
        return float("nan")


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open() as fp:
        return list(csv.DictReader(fp))


def build_series(rows: list[dict[str, str]], targets: list[str]) -> dict[str, dict[str, list[tuple[int, float]]]]:
    out: dict[str, dict[str, list[tuple[int, float]]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        target = row.get("target_name", "")
        if target not in targets:
            continue
        n = int(row.get("drone_count", "0"))
        out[target]["cpu_avg"].append((n, safe_float(row.get("cpu_avg", ""))))
        out[target]["cpu_p95"].append((n, safe_float(row.get("cpu_p95", ""))))
        out[target]["rss_mb_avg"].append((n, safe_float(row.get("rss_mb_avg", ""))))
    for target in out:
        for metric in out[target]:
            out[target][metric].sort(key=lambda x: x[0])
    return out


def plot_metric(
    series: dict[str, dict[str, list[tuple[int, float]]]],
    metric: str,
    title: str,
    ylabel: str,
    output_path: Path,
) -> None:
    plt.figure(figsize=(9, 5))
    for target, metrics in series.items():
        points = metrics.get(metric, [])
        if not points:
            continue
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        plt.plot(xs, ys, marker="o", label=target)
    plt.title(title)
    plt.xlabel("Drone Count")
    plt.ylabel(ylabel)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=140)
    plt.close()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = load_rows(input_path)
    series = build_series(rows, args.targets)

    plot_metric(
        series,
        "cpu_avg",
        "CPU Average vs Drone Count",
        "CPU [%]",
        output_dir / "cpu_avg_vs_drone_count.png",
    )
    plot_metric(
        series,
        "cpu_p95",
        "CPU p95 vs Drone Count",
        "CPU p95 [%]",
        output_dir / "cpu_p95_vs_drone_count.png",
    )
    plot_metric(
        series,
        "rss_mb_avg",
        "RSS Average vs Drone Count",
        "RSS [MB]",
        output_dir / "rss_avg_vs_drone_count.png",
    )

    print(f"[plot-summary] wrote: {output_dir / 'cpu_avg_vs_drone_count.png'}")
    print(f"[plot-summary] wrote: {output_dir / 'cpu_p95_vs_drone_count.png'}")
    print(f"[plot-summary] wrote: {output_dir / 'rss_avg_vs_drone_count.png'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
