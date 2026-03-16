#!/usr/bin/env python3
"""
Host-level performance monitor (macOS/Linux).

Outputs CSV rows compatible with aggregate_metrics.py:
- target_name is fixed to "host"
- cpu_percent: total host CPU usage (%)
- rss_kb: host used memory (kB)
- vsz_kb/thread_count: empty
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import platform
import re
import signal
import subprocess
import time
from pathlib import Path
from typing import Dict, Optional


def run_cmd(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL).strip()


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Sample host CPU/memory into CSV.")
    p.add_argument("--drone-count", type=int, required=True)
    p.add_argument("--label", default="host")
    p.add_argument("--duration-sec", type=float, required=True)
    p.add_argument("--interval-sec", type=float, default=1.0)
    p.add_argument("--output", required=True)
    return p.parse_args()


def parse_linux_cpu_percent() -> Optional[float]:
    try:
        out = run_cmd(["top", "-bn1"])
    except Exception:
        return None
    # Example:
    # %Cpu(s):  2.1 us,  0.5 sy,  0.0 ni, 97.1 id, ...
    m = re.search(r"Cpu\(s\):.*?([0-9]+(?:\.[0-9]+)?)\s*id", out)
    if not m:
        return None
    idle = float(m.group(1))
    return max(0.0, min(100.0, 100.0 - idle))


def parse_macos_cpu_percent() -> Optional[float]:
    try:
        out = run_cmd(["top", "-l", "1", "-n", "0"])
    except Exception:
        return None
    # Example:
    # CPU usage: 5.12% user, 7.41% sys, 87.45% idle
    m = re.search(r"CPU usage:.*?([0-9]+(?:\.[0-9]+)?)%\s*idle", out)
    if not m:
        return None
    idle = float(m.group(1))
    return max(0.0, min(100.0, 100.0 - idle))


def parse_linux_used_mem_kb() -> Optional[int]:
    try:
        text = Path("/proc/meminfo").read_text()
    except Exception:
        return None
    total = None
    avail = None
    for line in text.splitlines():
        if line.startswith("MemTotal:"):
            total = int(line.split()[1])
        elif line.startswith("MemAvailable:"):
            avail = int(line.split()[1])
    if total is None or avail is None:
        return None
    used = total - avail
    return max(0, used)


def parse_macos_used_mem_kb() -> Optional[int]:
    try:
        total_bytes = int(run_cmd(["sysctl", "-n", "hw.memsize"]))
        vm = run_cmd(["vm_stat"])
    except Exception:
        return None

    page_size = 4096
    m_page = re.search(r"page size of (\d+) bytes", vm)
    if m_page:
        page_size = int(m_page.group(1))

    def get_pages(key: str) -> int:
        m = re.search(rf"{re.escape(key)}:\s*([0-9]+)\.", vm)
        return int(m.group(1)) if m else 0

    free_pages = get_pages("Pages free") + get_pages("Pages speculative")
    free_bytes = free_pages * page_size
    used_bytes = max(0, total_bytes - free_bytes)
    return used_bytes // 1024


def sample_host_metrics() -> Optional[Dict[str, str]]:
    system = platform.system().lower()
    if system == "linux":
        cpu = parse_linux_cpu_percent()
        used_kb = parse_linux_used_mem_kb()
    elif system == "darwin":
        cpu = parse_macos_cpu_percent()
        used_kb = parse_macos_used_mem_kb()
    else:
        return None

    if cpu is None or used_kb is None:
        return None
    return {
        "cpu_percent": f"{cpu:.3f}",
        "rss_kb": str(used_kb),
        "vsz_kb": "",
        "thread_count": "",
        "command": "host",
    }


def main() -> int:
    args = parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    start = time.time()
    end = start + args.duration_sec
    stop_requested = False
    sample_count = 0

    def _on_signal(_signum, _frame):
        nonlocal stop_requested
        stop_requested = True

    signal.signal(signal.SIGINT, _on_signal)
    signal.signal(signal.SIGTERM, _on_signal)

    with output.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "timestamp_utc",
                "elapsed_sec",
                "host",
                "platform",
                "label",
                "drone_count",
                "target_name",
                "pid",
                "cpu_percent",
                "rss_kb",
                "vsz_kb",
                "thread_count",
                "command",
            ],
        )
        writer.writeheader()

        while True:
            now = time.time()
            if now > end:
                break
            metrics = sample_host_metrics()
            if metrics is not None:
                ts = dt.datetime.now(dt.UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")
                elapsed = now - start
                writer.writerow(
                    {
                        "timestamp_utc": ts,
                        "elapsed_sec": f"{elapsed:.3f}",
                        "host": platform.node(),
                        "platform": platform.platform(),
                        "label": args.label,
                        "drone_count": args.drone_count,
                        "target_name": "host",
                        "pid": "",
                        **metrics,
                    }
                )
                sample_count += 1
                f.flush()
            if stop_requested:
                break
            time.sleep(max(args.interval_sec, 0.2))

    print(f"[host-monitor] wrote: {output} rows={sample_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

