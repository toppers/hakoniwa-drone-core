#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DRONE_COUNT="${1:-1}"
LABEL="${2:-host_scale_n${DRONE_COUNT}}"
DURATION_SEC="${3:-${PERF_DURATION_SEC:-86400}}"
OUTPUT="${PROJECT_ROOT}/logs/perf/raw_host_${LABEL}.csv"

mkdir -p "${PROJECT_ROOT}/logs/perf"

echo "[start-host-perf-monitor] drone_count=${DRONE_COUNT}"
echo "[start-host-perf-monitor] label=${LABEL}"
echo "[start-host-perf-monitor] duration_sec=${DURATION_SEC}"
echo "[start-host-perf-monitor] output=${OUTPUT}"
echo "[start-host-perf-monitor] stop with Ctrl+C"

exec python3 "${PROJECT_ROOT}/tools/perf/monitor_host.py" \
  --drone-count "${DRONE_COUNT}" \
  --label "${LABEL}" \
  --duration-sec "${DURATION_SEC}" \
  --interval-sec 1 \
  --output "${OUTPUT}"
