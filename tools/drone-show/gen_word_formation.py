#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate one-shot word formation points.")
    p.add_argument("--word", required=True, help="Word to render (e.g. HELLOWORLD)")
    p.add_argument("--count", type=int, required=True, help="Total points")
    p.add_argument("--out", required=True, help="Output formation json path")
    p.add_argument("--id", help="Optional formation id written to output JSON")
    p.add_argument("--letter-width", type=float, default=1.0, help="Normalized width per letter")
    p.add_argument("--letter-height", type=float, default=2.0, help="Normalized height per letter")
    p.add_argument("--gap", type=float, default=0.45, help="Gap between letters")
    p.add_argument("--scale", type=float, default=1.0, help="Global scale")
    p.add_argument(
        "--min-seg-points",
        type=int,
        default=2,
        help="Minimum points per stroke segment",
    )
    return p.parse_args()


def letter_segments(letter: str) -> list[tuple[float, float, float, float]]:
    if letter == "A":
        return [(-1.0, -1.0, 0.0, 1.0), (0.0, 1.0, 1.0, -1.0), (-0.5, 0.0, 0.5, 0.0)]
    if letter == "H":
        return [(-1.0, -1.0, -1.0, 1.0), (1.0, -1.0, 1.0, 1.0), (-1.0, 0.0, 1.0, 0.0)]
    if letter == "E":
        return [(-1.0, -1.0, -1.0, 1.0), (-1.0, 1.0, 1.0, 1.0), (-1.0, 0.0, 0.6, 0.0), (-1.0, -1.0, 1.0, -1.0)]
    if letter == "L":
        return [(-1.0, -1.0, -1.0, 1.0), (-1.0, -1.0, 1.0, -1.0)]
    if letter == "O":
        return [(-1.0, -1.0, -1.0, 1.0), (-1.0, 1.0, 1.0, 1.0), (1.0, 1.0, 1.0, -1.0), (1.0, -1.0, -1.0, -1.0)]
    if letter == "W":
        return [
            (-1.0, 1.0, -0.6, -1.0),
            (-0.6, -1.0, 0.0, 0.5),
            (0.0, 0.5, 0.6, -1.0),
            (0.6, -1.0, 1.0, 1.0),
        ]
    if letter == "R":
        return [(-1.0, -1.0, -1.0, 1.0), (-1.0, 1.0, 0.6, 1.0), (0.6, 1.0, 0.6, 0.2), (0.6, 0.2, -1.0, 0.2), (-0.2, 0.2, 1.0, -1.0)]
    if letter == "D":
        return [
            (-1.0, -1.0, -1.0, 1.0),
            (-1.0, 1.0, 0.7, 1.0),
            (0.7, 1.0, 0.7, -1.0),
            (0.7, -1.0, -1.0, -1.0),
        ]
    if letter == "I":
        return [(-1.0, 1.0, 1.0, 1.0), (0.0, 1.0, 0.0, -1.0), (-1.0, -1.0, 1.0, -1.0)]
    if letter == "K":
        return [(-1.0, -1.0, -1.0, 1.0), (-1.0, 0.0, 1.0, 1.0), (-1.0, 0.0, 1.0, -1.0)]
    if letter == "N":
        return [(-1.0, -1.0, -1.0, 1.0), (-1.0, 1.0, 1.0, -1.0), (1.0, -1.0, 1.0, 1.0)]
    if letter == "S":
        return [
            (1.0, 1.0, -1.0, 1.0),
            (-1.0, 1.0, -1.0, 0.0),
            (-1.0, 0.0, 1.0, 0.0),
            (1.0, 0.0, 1.0, -1.0),
            (1.0, -1.0, -1.0, -1.0),
        ]
    if letter == "!":
        return [
            (0.0, 1.0, 0.0, -0.2),
            (0.0, -0.8, 0.0, -1.0),
        ]
    raise ValueError(f"unsupported letter: {letter}")


def allocate_counts(lengths: list[float], total: int, min_points: int) -> list[int]:
    if total <= 0:
        return [0] * len(lengths)
    if min_points < 1:
        min_points = 1
    required_min = len(lengths) * min_points
    if total < required_min:
        raise ValueError(
            f"point budget too small: total={total}, segments={len(lengths)}, "
            f"min_seg_points={min_points} requires >= {required_min}"
        )
    s = sum(lengths)
    if s <= 0:
        n = len(lengths)
        base = [min_points] * n
        remain = total - required_min
        for i in range(remain):
            base[i] += 1
        return base
    remain = total - required_min
    raw = [(l / s) * remain for l in lengths]
    counts = [min_points + int(round(v)) for v in raw]
    diff = total - sum(counts)
    n = len(counts)
    idx = 0
    while diff != 0 and idx < 10000:
        i = idx % n
        if diff > 0:
            counts[i] += 1
            diff -= 1
        else:
            if counts[i] > min_points:
                counts[i] -= 1
                diff += 1
        idx += 1
    return counts


def main() -> int:
    args = parse_args()
    word = args.word.strip().upper()
    if not word:
        raise SystemExit("--word must be non-empty")
    if args.count <= 0:
        raise SystemExit("--count must be > 0")

    per_letter_segments: list[list[tuple[float, float, float, float]]] = []
    for ch in word:
        if ch == " ":
            per_letter_segments.append([])
        else:
            per_letter_segments.append(letter_segments(ch))

    # letters are positioned along X, centered
    n = len(word)
    step = args.letter_width + args.gap
    x0 = -((n - 1) * step) / 2.0

    # flatten transformed segments
    transformed: list[tuple[float, float, float, float]] = []
    for i, segs in enumerate(per_letter_segments):
        if not segs:
            continue
        cx = x0 + (i * step)
        for ax, ay, bx, by in segs:
            tx0 = cx + (ax * args.letter_width / 2.0)
            ty0 = ay * args.letter_height / 2.0
            tx1 = cx + (bx * args.letter_width / 2.0)
            ty1 = by * args.letter_height / 2.0
            transformed.append((tx0, ty0, tx1, ty1))

    lengths = [math.hypot(x1 - x0s, y1 - y0s) for x0s, y0s, x1, y1 in transformed]
    seg_counts = allocate_counts(lengths, args.count, args.min_seg_points)

    points: list[list[float]] = []
    for (ax, ay, bx, by), c in zip(transformed, seg_counts):
        if c <= 0:
            continue
        ts = [0.5] if c == 1 else [i / (c - 1) for i in range(c)]
        for t in ts:
            x = (ax + (bx - ax) * t) * args.scale
            y = (ay + (by - ay) * t) * args.scale
            points.append([x, y, 0.0])

    if len(points) > args.count:
        points = points[: args.count]
    while len(points) < args.count:
        points.append(points[-1] if points else [0.0, 0.0, 0.0])

    out_id = args.id if args.id else word.replace(" ", "_")
    out = {"id": out_id, "points": points}
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print(f"[gen-word-formation] wrote: {out_path} points={len(points)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
