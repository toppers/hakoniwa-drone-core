#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DRONE_COUNT="${1:-1}"
LABEL="${2:-fleets_scale_n${DRONE_COUNT}}"
DURATION_SEC="${3:-${PERF_DURATION_SEC:-86400}}"
OUTPUT="${PROJECT_ROOT}/logs/perf/raw_${LABEL}.csv"
ENABLE_WEB_BRIDGE="${ENABLE_WEB_BRIDGE:-1}"
UNAME_S="${UNAME_S:-$(uname -s)}"
case "${UNAME_S}" in
  Darwin)
    DEFAULT_DRONE_SERVICE_MONITOR_PATTERN="mac-main_hako_drone_service"
    ;;
  Linux)
    DEFAULT_DRONE_SERVICE_MONITOR_PATTERN="linux-main_hako_drone_service"
    ;;
  *)
    DEFAULT_DRONE_SERVICE_MONITOR_PATTERN="mac-main_hako_drone_service"
    ;;
esac
DRONE_SERVICE_MONITOR_PATTERN="${HAKO_DRONE_SERVICE_MONITOR_PATTERN:-${DEFAULT_DRONE_SERVICE_MONITOR_PATTERN}}"

mkdir -p "${PROJECT_ROOT}/logs/perf"

echo "[start-perf-monitor] drone_count=${DRONE_COUNT}"
echo "[start-perf-monitor] label=${LABEL}"
echo "[start-perf-monitor] duration_sec=${DURATION_SEC}"
echo "[start-perf-monitor] output=${OUTPUT}"
echo "[start-perf-monitor] enable_web_bridge=${ENABLE_WEB_BRIDGE}"
echo "[start-perf-monitor] drone_service_monitor_pattern=${DRONE_SERVICE_MONITOR_PATTERN}"
echo "[start-perf-monitor] stop with Ctrl+C"

ARGS=(
  "${PROJECT_ROOT}/tools/perf/monitor_processes.py"
  --target "sim=${DRONE_SERVICE_MONITOR_PATTERN}"
  --target "vsp=drone_visual_state_publisher"
  --drone-count "${DRONE_COUNT}"
  --label "${LABEL}"
  --duration-sec "${DURATION_SEC}"
  --interval-sec 1
  --output "${OUTPUT}"
)

if [[ "${ENABLE_WEB_BRIDGE}" == "1" ]]; then
  ARGS+=(--target "bridge=hakoniwa-pdu-web-bridge")
fi

exec python3 "${ARGS[@]}"
