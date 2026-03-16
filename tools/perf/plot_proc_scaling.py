#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt


def load_rows(path: Path) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(
                {
                    "proc_count": float(row["proc_count"]),
                    "real_sec": float(row["real_sec"]),
                    "user_sec": float(row["user_sec"]),
                    "sys_sec": float(row["sys_sec"]),
                }
            )
    rows.sort(key=lambda r: r["proc_count"])
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Plot show-runner proc scaling result.")
    parser.add_argument(
        "--in-csv",
        default="logs/perf/proc_scaling_200_showrunner.csv",
        help="Input CSV path",
    )
    parser.add_argument(
        "--out-png",
        default="logs/perf/proc_scaling_200_showrunner.png",
        help="Output PNG path",
    )
    args = parser.parse_args()

    in_csv = Path(args.in_csv)
    out_png = Path(args.out_png)
    rows = load_rows(in_csv)

    x = [r["proc_count"] for r in rows]
    y_real = [r["real_sec"] for r in rows]
    y_user = [r["user_sec"] for r in rows]
    y_sys = [r["sys_sec"] for r in rows]

    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    ax.plot(x, y_real, marker="o", linewidth=2.2, label="real")
    ax.plot(x, y_user, marker="s", linewidth=1.8, label="user")
    ax.plot(x, y_sys, marker="^", linewidth=1.8, label="sys")

    best_idx = min(range(len(y_real)), key=lambda i: y_real[i])
    ax.scatter([x[best_idx]], [y_real[best_idx]], color="red", zorder=5)
    ax.annotate(
        f"best={int(x[best_idx])}proc ({y_real[best_idx]:.2f}s)",
        (x[best_idx], y_real[best_idx]),
        xytext=(8, -18),
        textcoords="offset points",
        color="red",
    )

    ax.set_title("Show Runner Proc Scaling (200 drones)")
    ax.set_xlabel("proc_count")
    ax.set_ylabel("seconds")
    ax.set_xticks(x)
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()

    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=140)
    print(f"saved: {out_png}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
