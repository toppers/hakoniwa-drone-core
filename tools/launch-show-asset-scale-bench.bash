#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

VIEW_MODE=0
POSITIONAL=()
for arg in "$@"; do
  case "${arg}" in
    --view)
      VIEW_MODE=1
      ;;
    *)
      POSITIONAL+=("${arg}")
      ;;
  esac
done

DRONE_COUNT="${POSITIONAL[0]:-}"
PROC_COUNT="${POSITIONAL[1]:-4}"

if [[ -z "${DRONE_COUNT}" ]]; then
  cat <<'EOF' >&2
Usage:
  bash tools/launch-show-asset-scale-bench.bash [--view] DRONE_COUNT [PROC_COUNT]

Examples:
  bash tools/launch-show-asset-scale-bench.bash 100 4
  bash tools/launch-show-asset-scale-bench.bash 200 4
  bash tools/launch-show-asset-scale-bench.bash 400 4
  bash tools/launch-show-asset-scale-bench.bash 512 8
  bash tools/launch-show-asset-scale-bench.bash --view 200 4
EOF
  exit 1
fi

case "${DRONE_COUNT}" in
  100)
    SHOW_ASSET_JSON="config/drone-show-config/show-hakoniwa-100-ref.json"
    ;;
  200)
    SHOW_ASSET_JSON="config/drone-show-config/show-hakoniwa-drone-icon-drone-show-3step-200-ref.json"
    ;;
  400)
    SHOW_ASSET_JSON="config/drone-show-config/show-hakoniwa-drone-icon-drone-show-3step-400-ref.json"
    ;;
  512)
    SHOW_ASSET_JSON="config/drone-show-config/show-hakoniwa-drone-icon-drone-show-3step-512-ref.json"
    ;;
  *)
    echo "Unsupported DRONE_COUNT: ${DRONE_COUNT} (supported: 100, 200, 400, 512)" >&2
    exit 1
    ;;
esac

SHOW_ASSET_ASSIGN_MODE="${SHOW_ASSET_ASSIGN_MODE:-nearest}"
SHOW_ASSET_SPEED="${SHOW_ASSET_SPEED:-14.0}"
SHOW_ASSET_TIMEOUT_SEC="${SHOW_ASSET_TIMEOUT_SEC:-120.0}"
SHOW_ASSET_DELTA_TIME_MSEC="${SHOW_ASSET_DELTA_TIME_MSEC:-20}"
SHOW_ASSET_FINAL_HOLD_EXTRA_SEC="${SHOW_ASSET_FINAL_HOLD_EXTRA_SEC:-5.0}"
SHOW_ASSET_Z_OFFSET_M="${SHOW_ASSET_Z_OFFSET_M:-0.0}"
SHOW_ASSET_NAME="${SHOW_ASSET_NAME:-ShowRunnerAsset}"
VISUAL_STATE_GLOBAL_DRONE_COUNT="${VISUAL_STATE_GLOBAL_DRONE_COUNT:-${DRONE_COUNT}}"
VISUAL_STATE_LOCAL_START_INDEX="${VISUAL_STATE_LOCAL_START_INDEX:-0}"
VISUAL_STATE_GLOBAL_START_INDEX="${VISUAL_STATE_GLOBAL_START_INDEX:-0}"
VISUAL_STATE_LOCAL_DRONE_COUNT="${VISUAL_STATE_LOCAL_DRONE_COUNT:-${DRONE_COUNT}}"
VISUAL_STATE_OUTPUT_CHUNK_BASE_INDEX="${VISUAL_STATE_OUTPUT_CHUNK_BASE_INDEX:-0}"
VISUAL_STATE_MAX_DRONES_PER_PACKET="${VISUAL_STATE_MAX_DRONES_PER_PACKET:-512}"
LAYOUT="${LAYOUT:-packed-rings}"
RING_SPACING_METER="${RING_SPACING_METER:-0.55}"
ENABLE_VIEWER_WEBSERVER="${ENABLE_VIEWER_WEBSERVER:-0}"
ENABLE_WEB_BRIDGE="${ENABLE_WEB_BRIDGE:-0}"
ENABLE_VISUAL_STATE_PUBLISHER="${ENABLE_VISUAL_STATE_PUBLISHER:-1}"
if [[ "${VIEW_MODE}" == "1" ]]; then
  ENABLE_WEB_BRIDGE=1
  ENABLE_VIEWER_WEBSERVER=1
fi

echo "[launch-show-asset-scale-bench] show_asset_json=${SHOW_ASSET_JSON}"
echo "[launch-show-asset-scale-bench] drone_count=${DRONE_COUNT}"
echo "[launch-show-asset-scale-bench] proc_count=${PROC_COUNT}"
echo "[launch-show-asset-scale-bench] view_mode=${VIEW_MODE}"
echo "[launch-show-asset-scale-bench] layout=${LAYOUT}"
echo "[launch-show-asset-scale-bench] ring_spacing_meter=${RING_SPACING_METER}"
echo "[launch-show-asset-scale-bench] speed=${SHOW_ASSET_SPEED}"
echo "[launch-show-asset-scale-bench] timeout_sec=${SHOW_ASSET_TIMEOUT_SEC}"
echo "[launch-show-asset-scale-bench] delta_time_msec=${SHOW_ASSET_DELTA_TIME_MSEC}"
echo "[launch-show-asset-scale-bench] final_hold_extra_sec=${SHOW_ASSET_FINAL_HOLD_EXTRA_SEC}"
echo "[launch-show-asset-scale-bench] z_offset_m=${SHOW_ASSET_Z_OFFSET_M}"
echo "[launch-show-asset-scale-bench] enable_visual_state_publisher=${ENABLE_VISUAL_STATE_PUBLISHER}"
echo "[launch-show-asset-scale-bench] enable_web_bridge=${ENABLE_WEB_BRIDGE}"
echo "[launch-show-asset-scale-bench] enable_viewer_webserver=${ENABLE_VIEWER_WEBSERVER}"
echo "[launch-show-asset-scale-bench] visual_state_global_drone_count=${VISUAL_STATE_GLOBAL_DRONE_COUNT}"
echo "[launch-show-asset-scale-bench] visual_state_global_start_index=${VISUAL_STATE_GLOBAL_START_INDEX}"
echo "[launch-show-asset-scale-bench] visual_state_local_start_index=${VISUAL_STATE_LOCAL_START_INDEX}"
echo "[launch-show-asset-scale-bench] visual_state_local_drone_count=${VISUAL_STATE_LOCAL_DRONE_COUNT}"
echo "[launch-show-asset-scale-bench] visual_state_output_chunk_base_index=${VISUAL_STATE_OUTPUT_CHUNK_BASE_INDEX}"
echo "[launch-show-asset-scale-bench] visual_state_max_drones_per_packet=${VISUAL_STATE_MAX_DRONES_PER_PACKET}"

exec env \
  SHOW_ASSET_JSON="${SHOW_ASSET_JSON}" \
  SHOW_ASSET_ASSIGN_MODE="${SHOW_ASSET_ASSIGN_MODE}" \
  SHOW_ASSET_SPEED="${SHOW_ASSET_SPEED}" \
  SHOW_ASSET_TIMEOUT_SEC="${SHOW_ASSET_TIMEOUT_SEC}" \
  SHOW_ASSET_DELTA_TIME_MSEC="${SHOW_ASSET_DELTA_TIME_MSEC}" \
  SHOW_ASSET_FINAL_HOLD_EXTRA_SEC="${SHOW_ASSET_FINAL_HOLD_EXTRA_SEC}" \
  SHOW_ASSET_Z_OFFSET_M="${SHOW_ASSET_Z_OFFSET_M}" \
  SHOW_ASSET_NAME="${SHOW_ASSET_NAME}" \
  VISUAL_STATE_GLOBAL_DRONE_COUNT="${VISUAL_STATE_GLOBAL_DRONE_COUNT}" \
  VISUAL_STATE_GLOBAL_START_INDEX="${VISUAL_STATE_GLOBAL_START_INDEX}" \
  VISUAL_STATE_LOCAL_START_INDEX="${VISUAL_STATE_LOCAL_START_INDEX}" \
  VISUAL_STATE_LOCAL_DRONE_COUNT="${VISUAL_STATE_LOCAL_DRONE_COUNT}" \
  VISUAL_STATE_OUTPUT_CHUNK_BASE_INDEX="${VISUAL_STATE_OUTPUT_CHUNK_BASE_INDEX}" \
  VISUAL_STATE_MAX_DRONES_PER_PACKET="${VISUAL_STATE_MAX_DRONES_PER_PACKET}" \
  ENABLE_VISUAL_STATE_PUBLISHER="${ENABLE_VISUAL_STATE_PUBLISHER}" \
  ENABLE_WEB_BRIDGE="${ENABLE_WEB_BRIDGE}" \
  ENABLE_VIEWER_WEBSERVER="${ENABLE_VIEWER_WEBSERVER}" \
  LAYOUT="${LAYOUT}" \
  RING_SPACING_METER="${RING_SPACING_METER}" \
  bash "${PROJECT_ROOT}/tools/launch-fleets-scale-perf.bash" "${DRONE_COUNT}" "" "${PROC_COUNT}"
