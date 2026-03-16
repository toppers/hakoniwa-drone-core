#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

export HAKO_DRONE_PROJECT_PATH="${HAKO_DRONE_PROJECT_PATH:-${PROJECT_ROOT}}"
if [[ -z "${HAKO_THREEJS_VIEWER_PATH:-}" ]]; then
  if [[ -d "/opt/hakoniwa-threejs-drone" ]]; then
    export HAKO_THREEJS_VIEWER_PATH="/opt/hakoniwa-threejs-drone"
  else
    export HAKO_THREEJS_VIEWER_PATH="${PROJECT_ROOT}/work/hakoniwa-threejs-drone"
  fi
fi
export HAKO_CONFIG_PATH="${HAKO_CONFIG_PATH:-/etc/hakoniwa/cpp_core_config.json}"

UNAME_S="${UNAME_S:-$(uname -s)}"
case "${UNAME_S}" in
  Darwin)
    DEFAULT_HAKO_DRONE_SERVICE_BIN="${PROJECT_ROOT}/mac/mac-main_hako_drone_service"
    DEFAULT_HAKO_VISUAL_STATE_PUBLISHER_BIN="${PROJECT_ROOT}/mac/mac-drone_visual_state_publisher"
    DEFAULT_HAKO_DRONE_SERVICE_MONITOR_PATTERN="mac-main_hako_drone_service"
    ;;
  Linux)
    DEFAULT_HAKO_DRONE_SERVICE_BIN="${PROJECT_ROOT}/lnx/linux-main_hako_drone_service"
    DEFAULT_HAKO_VISUAL_STATE_PUBLISHER_BIN="${PROJECT_ROOT}/lnx/linux-drone_visual_state_publisher"
    which linux-main_hako_drone_service >/dev/null 2>&1 && DEFAULT_HAKO_DRONE_SERVICE_BIN="$(which linux-main_hako_drone_service)"
    which linux-drone_visual_state_publisher >/dev/null 2>&1 && DEFAULT_HAKO_VISUAL_STATE_PUBLISHER_BIN="$(which linux-drone_visual_state_publisher)"
    DEFAULT_HAKO_DRONE_SERVICE_MONITOR_PATTERN="linux-main_hako_drone_service"
    ;;
  *)
    echo "Unsupported OS for auto-detecting drone service binary: ${UNAME_S}" >&2
    echo "Set HAKO_DRONE_SERVICE_BIN, HAKO_VISUAL_STATE_PUBLISHER_BIN, and HAKO_DRONE_SERVICE_MONITOR_PATTERN explicitly." >&2
    exit 1
    ;;
esac
export HAKO_DRONE_SERVICE_BIN="${HAKO_DRONE_SERVICE_BIN:-${DEFAULT_HAKO_DRONE_SERVICE_BIN}}"
export HAKO_VISUAL_STATE_PUBLISHER_BIN="${HAKO_VISUAL_STATE_PUBLISHER_BIN:-${DEFAULT_HAKO_VISUAL_STATE_PUBLISHER_BIN}}"
export HAKO_DRONE_SERVICE_MONITOR_PATTERN="${HAKO_DRONE_SERVICE_MONITOR_PATTERN:-${DEFAULT_HAKO_DRONE_SERVICE_MONITOR_PATTERN}}"

DRONE_COUNT="${1:-1}"
LAUNCH_FILE="${2:-${PROJECT_ROOT}/config/launcher/fleets-scale-perf.launch.json}"
PROC_COUNT="${3:-${FLEET_PROC_COUNT:-1}}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
LAYOUT="${LAYOUT:-legacy-rings}"
RING_SPACING_METER="${RING_SPACING_METER:-2.0}"
RING_CAPACITY="${RING_CAPACITY:-8}"
SPLIT_FLEET="${SPLIT_FLEET:-0}"
SHOW_ASSET_JSON="${SHOW_ASSET_JSON:-}"
SHOW_ASSET_ASSIGN_MODE="${SHOW_ASSET_ASSIGN_MODE:-nearest}"
SHOW_ASSET_SPEED="${SHOW_ASSET_SPEED:-14.0}"
SHOW_ASSET_TIMEOUT_SEC="${SHOW_ASSET_TIMEOUT_SEC:-120.0}"
SHOW_ASSET_DELTA_TIME_MSEC="${SHOW_ASSET_DELTA_TIME_MSEC:-20}"
SHOW_ASSET_FINAL_HOLD_EXTRA_SEC="${SHOW_ASSET_FINAL_HOLD_EXTRA_SEC:-5.0}"
SHOW_ASSET_Z_OFFSET_M="${SHOW_ASSET_Z_OFFSET_M:-0.0}"
SHOW_ASSET_NAME="${SHOW_ASSET_NAME:-ShowRunnerAsset}"
SHOW_ASSET_SUMMARY_JSON="${SHOW_ASSET_SUMMARY_JSON:-${PROJECT_ROOT}/logs/perf/show_asset_summary_n${DRONE_COUNT}_p${PROC_COUNT}.json}"
CONDUCTOR_SERVER_SCRIPT="${CONDUCTOR_SERVER_SCRIPT:-}"
CONDUCTOR_SERVER_ID="${CONDUCTOR_SERVER_ID:-1}"
CONDUCTOR_MODE="${CONDUCTOR_MODE:-simple}"
CONDUCTOR_CONFIG_ROOT="${CONDUCTOR_CONFIG_ROOT:-}"
LAUNCHER_MODE="${LAUNCHER_MODE:-immediate}"
VISUAL_STATE_GLOBAL_DRONE_COUNT="${VISUAL_STATE_GLOBAL_DRONE_COUNT:-${DRONE_COUNT}}"
VISUAL_STATE_GLOBAL_START_INDEX="${VISUAL_STATE_GLOBAL_START_INDEX:-0}"
VISUAL_STATE_LOCAL_START_INDEX="${VISUAL_STATE_LOCAL_START_INDEX:-0}"
VISUAL_STATE_LOCAL_DRONE_COUNT="${VISUAL_STATE_LOCAL_DRONE_COUNT:-${DRONE_COUNT}}"
VISUAL_STATE_OUTPUT_CHUNK_BASE_INDEX="${VISUAL_STATE_OUTPUT_CHUNK_BASE_INDEX:-0}"
VISUAL_STATE_MAX_DRONES_PER_PACKET="${VISUAL_STATE_MAX_DRONES_PER_PACKET:-512}"
VISUAL_STATE_PUBLISHER_RUNTIME_CONFIG="${VISUAL_STATE_PUBLISHER_RUNTIME_CONFIG:-${PROJECT_ROOT}/config/assets/visual_state_publisher/visual_state_publisher.runtime.json}"
ENABLE_VIEWER_WEBSERVER="${ENABLE_VIEWER_WEBSERVER:-1}"
ENABLE_WEB_BRIDGE="${ENABLE_WEB_BRIDGE:-1}"
ENABLE_VISUAL_STATE_PUBLISHER="${ENABLE_VISUAL_STATE_PUBLISHER:-1}"
export FLEET_DRONE_COUNT="${DRONE_COUNT}"
export FLEET_PROC_COUNT="${PROC_COUNT}"
export PERF_LABEL="${PERF_LABEL:-fleets_scale_n${DRONE_COUNT}_p${PROC_COUNT}}"

echo "[launch-fleets-scale-perf] HAKO_DRONE_PROJECT_PATH=${HAKO_DRONE_PROJECT_PATH}"
echo "[launch-fleets-scale-perf] HAKO_THREEJS_VIEWER_PATH=${HAKO_THREEJS_VIEWER_PATH}"
echo "[launch-fleets-scale-perf] HAKO_CONFIG_PATH=${HAKO_CONFIG_PATH}"
echo "[launch-fleets-scale-perf] uname_s=${UNAME_S}"
echo "[launch-fleets-scale-perf] hako_drone_service_bin=${HAKO_DRONE_SERVICE_BIN}"
echo "[launch-fleets-scale-perf] hako_visual_state_publisher_bin=${HAKO_VISUAL_STATE_PUBLISHER_BIN}"
echo "[launch-fleets-scale-perf] hako_drone_service_monitor_pattern=${HAKO_DRONE_SERVICE_MONITOR_PATTERN}"
echo "[launch-fleets-scale-perf] drone_count=${DRONE_COUNT}"
echo "[launch-fleets-scale-perf] proc_count=${PROC_COUNT}"
echo "[launch-fleets-scale-perf] perf_label=${PERF_LABEL}"
echo "[launch-fleets-scale-perf] launch_file=${LAUNCH_FILE}"
echo "[launch-fleets-scale-perf] layout=${LAYOUT}"
echo "[launch-fleets-scale-perf] ring_spacing_meter=${RING_SPACING_METER}"
echo "[launch-fleets-scale-perf] ring_capacity=${RING_CAPACITY}"
echo "[launch-fleets-scale-perf] split_fleet=${SPLIT_FLEET}"
echo "[launch-fleets-scale-perf] conductor_server_script=${CONDUCTOR_SERVER_SCRIPT}"
echo "[launch-fleets-scale-perf] conductor_server_id=${CONDUCTOR_SERVER_ID}"
echo "[launch-fleets-scale-perf] conductor_mode=${CONDUCTOR_MODE}"
echo "[launch-fleets-scale-perf] conductor_config_root=${CONDUCTOR_CONFIG_ROOT}"
echo "[launch-fleets-scale-perf] launcher_mode=${LAUNCHER_MODE}"
echo "[launch-fleets-scale-perf] enable_visual_state_publisher=${ENABLE_VISUAL_STATE_PUBLISHER}"
echo "[launch-fleets-scale-perf] enable_web_bridge=${ENABLE_WEB_BRIDGE}"
echo "[launch-fleets-scale-perf] enable_viewer_webserver=${ENABLE_VIEWER_WEBSERVER}"
echo "[launch-fleets-scale-perf] visual_state_global_drone_count=${VISUAL_STATE_GLOBAL_DRONE_COUNT}"
echo "[launch-fleets-scale-perf] visual_state_global_start_index=${VISUAL_STATE_GLOBAL_START_INDEX}"
echo "[launch-fleets-scale-perf] visual_state_local_start_index=${VISUAL_STATE_LOCAL_START_INDEX}"
echo "[launch-fleets-scale-perf] visual_state_local_drone_count=${VISUAL_STATE_LOCAL_DRONE_COUNT}"
echo "[launch-fleets-scale-perf] visual_state_output_chunk_base_index=${VISUAL_STATE_OUTPUT_CHUNK_BASE_INDEX}"
echo "[launch-fleets-scale-perf] visual_state_max_drones_per_packet=${VISUAL_STATE_MAX_DRONES_PER_PACKET}"
echo "[launch-fleets-scale-perf] visual_state_publisher_runtime_config=${VISUAL_STATE_PUBLISHER_RUNTIME_CONFIG}"
if [[ -n "${SHOW_ASSET_JSON}" ]]; then
  echo "[launch-fleets-scale-perf] show_asset_json=${SHOW_ASSET_JSON}"
  echo "[launch-fleets-scale-perf] show_asset_summary_json=${SHOW_ASSET_SUMMARY_JSON}"
  echo "[launch-fleets-scale-perf] show_asset_final_hold_extra_sec=${SHOW_ASSET_FINAL_HOLD_EXTRA_SEC}"
  echo "[launch-fleets-scale-perf] show_asset_z_offset_m=${SHOW_ASSET_Z_OFFSET_M}"
fi

"${PYTHON_BIN}" "${PROJECT_ROOT}/tools/gen_fleet_scale_config.py" \
  -n "${DRONE_COUNT}" \
  --layout "${LAYOUT}" \
  --ring-spacing-meter "${RING_SPACING_METER}" \
  --ring-capacity "${RING_CAPACITY}"

"${PYTHON_BIN}" "${PROJECT_ROOT}/tools/gen_visual_state_publisher_config.py" \
  --base-config "${PROJECT_ROOT}/config/assets/visual_state_publisher/visual_state_publisher.json" \
  --out "${VISUAL_STATE_PUBLISHER_RUNTIME_CONFIG}" \
  --global-drone-count "${VISUAL_STATE_GLOBAL_DRONE_COUNT}" \
  --global-start-index "${VISUAL_STATE_GLOBAL_START_INDEX}" \
  --local-start-index "${VISUAL_STATE_LOCAL_START_INDEX}" \
  --local-drone-count "${VISUAL_STATE_LOCAL_DRONE_COUNT}" \
  --output-chunk-base-index "${VISUAL_STATE_OUTPUT_CHUNK_BASE_INDEX}" \
  --max-drones-per-packet "${VISUAL_STATE_MAX_DRONES_PER_PACKET}"

if ! [[ "${PROC_COUNT}" =~ ^[0-9]+$ ]] || [[ "${PROC_COUNT}" -lt 1 ]]; then
  echo "Invalid proc count: ${PROC_COUNT} (must be integer >= 1)" >&2
  exit 1
fi

if [[ "${SPLIT_FLEET}" == "1" || "${LAUNCH_FILE}" == *"2proc"* || "${PROC_COUNT}" -gt 1 ]]; then
  if [[ "${PROC_COUNT}" -gt 1 ]]; then
    "${PYTHON_BIN}" "${PROJECT_ROOT}/tools/gen_fleet_split_config.py" --parts "${PROC_COUNT}"
  else
    "${PYTHON_BIN}" "${PROJECT_ROOT}/tools/gen_fleet_split_config.py"
  fi
fi

if [[ "${PROC_COUNT}" -gt 1 || -n "${SHOW_ASSET_JSON}" || "${ENABLE_VISUAL_STATE_PUBLISHER}" == "1" ]]; then
  GENERATED_LAUNCH="${PROJECT_ROOT}/config/launcher/fleets-scale-perf-nproc.generated.launch.json"
  GEN_ARGS=(
    "${PROJECT_ROOT}/tools/gen_fleet_nproc_launch.py"
    --proc-count "${PROC_COUNT}" \
    --drone-service-command "${HAKO_DRONE_SERVICE_BIN}" \
    --visual-state-publisher-command "${HAKO_VISUAL_STATE_PUBLISHER_BIN}" \
    --visual-state-publisher-config "${VISUAL_STATE_PUBLISHER_RUNTIME_CONFIG}" \
    --out "${GENERATED_LAUNCH}"
  )
  if [[ -n "${CONDUCTOR_SERVER_SCRIPT}" ]]; then
    GEN_ARGS+=(
      --conductor-server-script "${CONDUCTOR_SERVER_SCRIPT}"
      --conductor-server-id "${CONDUCTOR_SERVER_ID}"
      --conductor-mode "${CONDUCTOR_MODE}"
    )
    if [[ -n "${CONDUCTOR_CONFIG_ROOT}" ]]; then
      GEN_ARGS+=(
        --conductor-config-root "${CONDUCTOR_CONFIG_ROOT}"
      )
    fi
  fi
  if [[ -n "${SHOW_ASSET_JSON}" ]]; then
    GEN_ARGS+=(
      --show-asset-json "${SHOW_ASSET_JSON}"
      --show-asset-drone-count "${DRONE_COUNT}"
      --show-asset-assign-mode "${SHOW_ASSET_ASSIGN_MODE}"
      --show-asset-speed "${SHOW_ASSET_SPEED}"
      --show-asset-timeout-sec "${SHOW_ASSET_TIMEOUT_SEC}"
      --show-asset-delta-time-msec "${SHOW_ASSET_DELTA_TIME_MSEC}"
      --show-asset-final-hold-extra-sec "${SHOW_ASSET_FINAL_HOLD_EXTRA_SEC}"
      --show-asset-z-offset-m "${SHOW_ASSET_Z_OFFSET_M}"
      --show-asset-name "${SHOW_ASSET_NAME}"
      --show-asset-summary-json "${SHOW_ASSET_SUMMARY_JSON}"
    )
  fi
  if [[ "${ENABLE_VIEWER_WEBSERVER}" != "1" ]]; then
    GEN_ARGS+=(--disable-viewer-webserver)
  fi
  if [[ "${ENABLE_WEB_BRIDGE}" != "1" ]]; then
    GEN_ARGS+=(--disable-web-bridge)
  fi
  if [[ "${ENABLE_VISUAL_STATE_PUBLISHER}" != "1" ]]; then
    GEN_ARGS+=(--disable-visual-state-publisher)
  fi
  "${PYTHON_BIN}" "${GEN_ARGS[@]}"
  LAUNCH_FILE="${GENERATED_LAUNCH}"
fi

exec "${PYTHON_BIN}" -m hakoniwa_pdu.apps.launcher.hako_launcher --mode "${LAUNCHER_MODE}" "${LAUNCH_FILE}"
