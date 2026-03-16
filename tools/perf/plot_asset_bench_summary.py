#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


def safe_float(value: str) -> float:
    try:
        return float(value)
    except Exception:
        return float("nan")


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def build_total_series(rows: list[dict[str, str]]) -> dict[int, list[tuple[int, float]]]:
    out: dict[int, list[tuple[int, float]]] = defaultdict(list)
    for row in rows:
        if row.get("status") != "done":
            continue
        drone_count = int(row["drone_count"])
        proc_count = int(row["proc_count"])
        total_sec = safe_float(row["total_sec"])
        out[drone_count].append((proc_count, total_sec))
    for drone_count in out:
        out[drone_count].sort(key=lambda x: x[0])
    return out


def plot_total_vs_proc(series: dict[int, list[tuple[int, float]]], output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    for drone_count, points in sorted(series.items()):
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        ax.plot(xs, ys, marker="o", linewidth=2.0, label=f"{drone_count} drones")
        best_idx = min(range(len(points)), key=lambda i: ys[i])
        ax.scatter([xs[best_idx]], [ys[best_idx]], color="red", zorder=5)
        ax.annotate(
            f"best={xs[best_idx]}p {ys[best_idx]:.1f}s",
            (xs[best_idx], ys[best_idx]),
            xytext=(6, -14),
            textcoords="offset points",
            color="red",
            fontsize=9,
        )
    ax.set_title("Asset Bench: Total Time vs Process Count")
    ax.set_xlabel("proc_count")
    ax.set_ylabel("total_sec")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=140)
    plt.close(fig)


def plot_phase_breakdown(rows: list[dict[str, str]], output_dir: Path) -> list[Path]:
    generated: list[Path] = []
    by_drone: dict[int, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if row.get("status") == "done":
            by_drone[int(row["drone_count"])].append(row)

    phase_fields = [
        ("prepare_basic_services_sec", "prepare"),
        ("set_ready_sec", "set_ready"),
        ("takeoff_sec", "takeoff"),
        ("first_goto_sec", "goto#1"),
    ]

    for drone_count, drone_rows in sorted(by_drone.items()):
        drone_rows.sort(key=lambda r: int(r["proc_count"]))
        proc_counts = [int(r["proc_count"]) for r in drone_rows]
        bottoms = [0.0 for _ in proc_counts]
        fig, ax = plt.subplots(figsize=(8.5, 5.0))
        for field, label in phase_fields:
            values = [safe_float(r.get(field, "")) for r in drone_rows]
            ax.bar(proc_counts, values, bottom=bottoms, label=label)
            bottoms = [b + v for b, v in zip(bottoms, values)]
        totals = [safe_float(r["total_sec"]) for r in drone_rows]
        ax.plot(proc_counts, totals, color="black", marker="o", linewidth=1.8, label="total")
        ax.set_title(f"Asset Bench Phase Breakdown ({drone_count} drones)")
        ax.set_xlabel("proc_count")
        ax.set_ylabel("seconds")
        ax.set_xticks(proc_counts)
        ax.grid(True, axis="y", alpha=0.25)
        ax.legend()
        fig.tight_layout()
        out_png = output_dir / f"asset_bench_phase_breakdown_n{drone_count}.png"
        fig.savefig(out_png, dpi=140)
        plt.close(fig)
        generated.append(out_png)
    return generated


def main() -> int:
    parser = argparse.ArgumentParser(description="Plot asset bench summary CSV.")
    parser.add_argument("--input", required=True, help="summary.csv path")
    parser.add_argument(
        "--output-dir",
        default="logs/perf",
        help="directory for PNG outputs",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    rows = load_rows(input_path)
    total_series = build_total_series(rows)

    total_png = output_dir / "asset_bench_total_vs_proc.png"
    plot_total_vs_proc(total_series, total_png)
    print(f"saved: {total_png}")

    for path in plot_phase_breakdown(rows, output_dir):
        print(f"saved: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
