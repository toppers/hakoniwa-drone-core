#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate letter formation points.")
    p.add_argument("--letter", choices=["H", "E", "L", "O", "W", "R", "D", "A"], required=True)
    p.add_argument("--count", type=int, required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--width", type=float, default=8.0)
    p.add_argument("--height", type=float, default=6.0)
    p.add_argument("--stroke", type=float, default=0.0, help="Reserved for future multi-lane stroke")
    return p.parse_args()


def letter_segments(letter: str) -> list[tuple[float, float, float, float]]:
    if letter == "H":
        return [
            (-1.0, -1.0, -1.0, 1.0),  # left vertical
            (1.0, -1.0, 1.0, 1.0),    # right vertical
            (-1.0, 0.0, 1.0, 0.0),    # center bar
        ]
    if letter == "E":
        return [
            (-1.0, -1.0, -1.0, 1.0),
            (-1.0, 1.0, 1.0, 1.0),
            (-1.0, 0.0, 0.6, 0.0),
            (-1.0, -1.0, 1.0, -1.0),
        ]
    if letter == "L":
        return [
            (-1.0, -1.0, -1.0, 1.0),
            (-1.0, -1.0, 1.0, -1.0),
        ]
    if letter == "O":
        return [
            (-1.0, -1.0, -1.0, 1.0),
            (-1.0, 1.0, 1.0, 1.0),
            (1.0, 1.0, 1.0, -1.0),
            (1.0, -1.0, -1.0, -1.0),
        ]
    if letter == "W":
        return [
            (-1.0, 1.0, -0.5, -1.0),
            (-0.5, -1.0, 0.0, 0.2),
            (0.0, 0.2, 0.5, -1.0),
            (0.5, -1.0, 1.0, 1.0),
        ]
    if letter == "R":
        return [
            (-1.0, -1.0, -1.0, 1.0),
            (-1.0, 1.0, 0.6, 1.0),
            (0.6, 1.0, 0.6, 0.2),
            (0.6, 0.2, -1.0, 0.2),
            (-0.2, 0.2, 1.0, -1.0),
        ]
    if letter == "D":
        return [
            (-1.0, -1.0, -1.0, 1.0),
            (-1.0, 1.0, 0.5, 1.0),
            (0.5, 1.0, 1.0, 0.5),
            (1.0, 0.5, 1.0, -0.5),
            (1.0, -0.5, 0.5, -1.0),
            (0.5, -1.0, -1.0, -1.0),
        ]
    # A
    return [
        (-1.0, -1.0, 0.0, 1.0),      # left diagonal
        (0.0, 1.0, 1.0, -1.0),       # right diagonal
        (-0.5, 0.0, 0.5, 0.0),       # cross bar
    ]


def allocate_counts(lengths: list[float], total: int) -> list[int]:
    if total <= 0:
        return [0] * len(lengths)
    n = len(lengths)
    if n == 0:
        return []
    s = sum(lengths)
    if s <= 0:
        base = [total // n] * n
        for i in range(total % n):
            base[i] += 1
        return base
    raw = [(l / s) * total for l in lengths]
    counts = [max(1, int(round(v))) for v in raw]
    diff = total - sum(counts)
    order = sorted(range(n), key=lambda i: raw[i] - math.floor(raw[i]), reverse=(diff > 0))
    idx = 0
    while diff != 0 and n > 0:
        i = order[idx % n]
        if diff > 0:
            counts[i] += 1
            diff -= 1
        else:
            if counts[i] > 1:
                counts[i] -= 1
                diff += 1
        idx += 1
        if idx > 10_000:
            break
    return counts


def sample_points(letter: str, count: int, width: float, height: float):
    segs = letter_segments(letter)
    lengths = [math.hypot(s[2] - s[0], s[3] - s[1]) for s in segs]
    seg_counts = allocate_counts(lengths, count)
    points: list[list[float]] = []

    for (ax, ay, bx, by), c in zip(segs, seg_counts):
        if c <= 0:
            continue
        if c == 1:
            ts = [0.5]
        else:
            ts = [i / (c - 1) for i in range(c)]
        for t in ts:
            x = ax + (bx - ax) * t
            y = ay + (by - ay) * t
            points.append([x * (width / 2.0), y * (height / 2.0), 0.0])

    # exact count clamp
    if len(points) > count:
        points = points[:count]
    elif len(points) < count:
        last = points[-1] if points else [0.0, 0.0, 0.0]
        while len(points) < count:
            points.append(list(last))
    return points


def main() -> int:
    args = parse_args()
    if args.count <= 0:
        raise SystemExit("--count must be > 0")
    points = sample_points(
        letter=args.letter,
        count=args.count,
        width=args.width,
        height=args.height,
    )
    out = {"id": args.letter, "points": points}
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print(f"[gen-letter-formation] wrote: {out_path} points={len(points)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
