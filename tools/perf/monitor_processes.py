#!/usr/bin/env python3
"""
Cross-platform process monitor (macOS/Linux).

Outputs CSV with sampled process metrics:
- cpu_percent
- rss_kb
- vsz_kb
- thread_count
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import os
import platform
import shlex
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class Target:
    name: str
    pid: int
    spec: str


def run_cmd(cmd: List[str]) -> str:
    return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL).strip()


def detect_thread_field() -> str:
    for field in ("thcount", "nlwp"):
        try:
            out = run_cmd(["ps", "-p", str(os.getpid()), "-o", f"{field}="])
            if out:
                return field
        except Exception:
            pass
    return ""


def detect_cpu_field() -> str:
    for field in ("pcpu", "%cpu"):
        try:
            out = run_cmd(["ps", "-p", str(os.getpid()), "-o", f"{field}="])
            if out:
                return field
        except Exception:
            pass
    return "pcpu"


def find_pid_by_pattern(pattern: str) -> Optional[int]:
    try:
        out = run_cmd(["pgrep", "-f", pattern])
    except Exception:
        return None
    if not out:
        return None
    candidates: List[int] = []
    self_pid = os.getpid()
    for line in out.splitlines():
        s = line.strip()
        if not s.isdigit():
            continue
        pid = int(s)
        if pid == self_pid:
            continue
        candidates.append(pid)
    if not candidates:
        return None
    # `pgrep -f` can match short-lived wrapper/shell processes first.
    # Pick the newest match (last line) to improve stability.
    return candidates[-1]


def parse_target(raw: str) -> Tuple[str, str]:
    if "=" not in raw:
        raise ValueError(f"Invalid --target '{raw}'. expected format: name=PID_OR_PATTERN")
    name, spec = raw.split("=", 1)
    name = name.strip()
    spec = spec.strip()
    if not name or not spec:
        raise ValueError(f"Invalid --target '{raw}'. empty name/spec")
    return name, spec


def resolve_targets(raw_targets: List[str]) -> List[Target]:
    resolved: List[Target] = []
    for raw in raw_targets:
        name, spec = parse_target(raw)
        if spec.isdigit():
            resolved.append(Target(name=name, pid=int(spec), spec=spec))
            continue
        pid = find_pid_by_pattern(spec)
        if pid is None:
            raise RuntimeError(f"Could not resolve PID for target '{name}' pattern='{spec}'")
        print(f"[monitor] target resolved: name={name} pattern='{spec}' pid={pid}")
        resolved.append(Target(name=name, pid=pid, spec=spec))
    return resolved


def sample_pid(pid: int, cpu_field: str, thread_field: str) -> Optional[Dict[str, str]]:
    def field(name: str) -> Optional[str]:
        try:
            out = run_cmd(["ps", "-p", str(pid), "-o", f"{name}="])
        except Exception:
            return None
        s = out.strip()
        return s if s else None

    cpu = field(cpu_field)
    rss = field("rss")
    vsz = field("vsz")
    th = field(thread_field) if thread_field else ""
    comm = field("comm")
    if cpu is None or rss is None:
        return None
    return {
        "cpu_percent": cpu,
        "rss_kb": rss,
        "vsz_kb": vsz or "",
        "thread_count": th or "",
        "command": comm or "",
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Sample process metrics into CSV.")
    p.add_argument("--target", action="append", required=True, help="name=PID_OR_PATTERN (repeatable)")
    p.add_argument("--drone-count", type=int, required=True)
    p.add_argument("--label", default="baseline")
    p.add_argument("--duration-sec", type=float, required=True)
    p.add_argument("--interval-sec", type=float, default=1.0)
    p.add_argument("--output", required=True)
    return p.parse_args()


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def main() -> int:
    args = parse_args()
    output = Path(args.output)
    ensure_parent(output)
    thread_field = detect_thread_field()
    cpu_field = detect_cpu_field()
    print(f"[monitor] ps fields: cpu_field={cpu_field} thread_field={thread_field}")
    targets = resolve_targets(args.target)
    start = time.time()
    end = start + args.duration_sec
    stop_requested = False

    def _on_signal(signum, _frame):
        nonlocal stop_requested
        stop_requested = True

    signal.signal(signal.SIGINT, _on_signal)
    signal.signal(signal.SIGTERM, _on_signal)
    sample_count = 0

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
            ts = dt.datetime.now(dt.UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")
            elapsed = now - start
            for t in targets:
                metrics = sample_pid(t.pid, cpu_field, thread_field)
                if metrics is None:
                    if not t.spec.isdigit():
                        new_pid = find_pid_by_pattern(t.spec)
                        if new_pid is not None and new_pid != t.pid:
                            print(f"[monitor] target re-resolved: name={t.name} old_pid={t.pid} new_pid={new_pid}")
                            t.pid = new_pid
                            metrics = sample_pid(t.pid, cpu_field, thread_field)
                    if metrics is None:
                        continue
                writer.writerow(
                    {
                        "timestamp_utc": ts,
                        "elapsed_sec": f"{elapsed:.3f}",
                        "host": platform.node(),
                        "platform": platform.platform(),
                        "label": args.label,
                        "drone_count": args.drone_count,
                        "target_name": t.name,
                        "pid": t.pid,
                        **metrics,
                    }
                )
                sample_count += 1
            f.flush()
            if stop_requested:
                break
            time.sleep(max(args.interval_sec, 0.05))

    print(f"[monitor] wrote: {output} rows={sample_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
