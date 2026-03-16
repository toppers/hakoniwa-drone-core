#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DRONE_COUNT="${1:-}"
PROC_COUNT="${2:-4}"

if [[ -z "${DRONE_COUNT}" ]]; then
  cat <<'EOF' >&2
Usage:
  bash tools/launch-fleets-dist-simple-server.bash DRONE_COUNT [PROC_COUNT]

Examples:
  bash tools/launch-fleets-dist-simple-server.bash 200 4
  bash tools/launch-fleets-dist-simple-server.bash 400 8
EOF
  exit 1
fi

CONDUCTOR_ROLE="${CONDUCTOR_ROLE:-server}"
CONDUCTOR_CONFIG_ROOT="${CONDUCTOR_CONFIG_ROOT:-work/hakoniwa-conductor-pro/eu-config/generated-fleets}"
CONDUCTOR_NODE_ID="${CONDUCTOR_NODE_ID:-1}"
CONDUCTOR_CONFIG_ID="${CONDUCTOR_CONFIG_ID:-${CONDUCTOR_NODE_ID}}"
CONDUCTOR_MODE="${CONDUCTOR_MODE:-simple}"
ENABLE_VISUAL_STATE_PUBLISHER="${ENABLE_VISUAL_STATE_PUBLISHER:-1}"
VISUAL_STATE_MAX_DRONES_PER_PACKET="${VISUAL_STATE_MAX_DRONES_PER_PACKET:-512}"
SHOW_ASSET_JSON="${SHOW_ASSET_JSON:-}"
SHOW_ASSET_ASSIGN_MODE="${SHOW_ASSET_ASSIGN_MODE:-nearest}"
SHOW_ASSET_SPEED="${SHOW_ASSET_SPEED:-14.0}"
SHOW_ASSET_TIMEOUT_SEC="${SHOW_ASSET_TIMEOUT_SEC:-120.0}"
SHOW_ASSET_DELTA_TIME_MSEC="${SHOW_ASSET_DELTA_TIME_MSEC:-20}"
SHOW_ASSET_FINAL_HOLD_EXTRA_SEC="${SHOW_ASSET_FINAL_HOLD_EXTRA_SEC:-5.0}"
SHOW_ASSET_Z_OFFSET_M="${SHOW_ASSET_Z_OFFSET_M:-0.0}"
SHOW_ASSET_NAME="${SHOW_ASSET_NAME:-ShowRunnerAsset}"
SHOW_ASSET_SUMMARY_JSON="${SHOW_ASSET_SUMMARY_JSON:-}"
VISUAL_STATE_GLOBAL_DRONE_COUNT="${VISUAL_STATE_GLOBAL_DRONE_COUNT:-${DRONE_COUNT}}"
VISUAL_STATE_GLOBAL_START_INDEX="${VISUAL_STATE_GLOBAL_START_INDEX:-0}"
VISUAL_STATE_LOCAL_START_INDEX="${VISUAL_STATE_LOCAL_START_INDEX:-0}"
VISUAL_STATE_LOCAL_DRONE_COUNT="${VISUAL_STATE_LOCAL_DRONE_COUNT:-${DRONE_COUNT}}"
VISUAL_STATE_OUTPUT_CHUNK_BASE_INDEX="${VISUAL_STATE_OUTPUT_CHUNK_BASE_INDEX:-0}"

case "${CONDUCTOR_ROLE}" in
  server)
    CONDUCTOR_SERVER_SCRIPT="${CONDUCTOR_SERVER_SCRIPT:-work/hakoniwa-conductor-pro/srv.bash}"
    LAUNCHER_MODE="${LAUNCHER_MODE:-immediate}"
    ENABLE_WEB_BRIDGE="${ENABLE_WEB_BRIDGE:-1}"
    ENABLE_VIEWER_WEBSERVER="${ENABLE_VIEWER_WEBSERVER:-1}"
    ;;
  client)
    CONDUCTOR_SERVER_SCRIPT="${CONDUCTOR_SERVER_SCRIPT:-work/hakoniwa-conductor-pro/cli.bash}"
    LAUNCHER_MODE="${LAUNCHER_MODE:-activate-only}"
    ENABLE_WEB_BRIDGE="${ENABLE_WEB_BRIDGE:-0}"
    ENABLE_VIEWER_WEBSERVER="${ENABLE_VIEWER_WEBSERVER:-0}"
    SHOW_ASSET_JSON="${SHOW_ASSET_JSON:-}"
    ;;
  *)
    echo "ERROR: unsupported CONDUCTOR_ROLE='${CONDUCTOR_ROLE}' (expected server|client)" >&2
    exit 1
    ;;
esac

echo "[launch-fleets-dist-simple-server] drone_count=${DRONE_COUNT}"
echo "[launch-fleets-dist-simple-server] proc_count=${PROC_COUNT}"
echo "[launch-fleets-dist-simple-server] conductor_role=${CONDUCTOR_ROLE}"
echo "[launch-fleets-dist-simple-server] conductor_server_script=${CONDUCTOR_SERVER_SCRIPT}"
echo "[launch-fleets-dist-simple-server] conductor_node_id=${CONDUCTOR_NODE_ID}"
echo "[launch-fleets-dist-simple-server] conductor_config_id=${CONDUCTOR_CONFIG_ID}"
echo "[launch-fleets-dist-simple-server] conductor_mode=${CONDUCTOR_MODE}"
echo "[launch-fleets-dist-simple-server] conductor_config_root=${CONDUCTOR_CONFIG_ROOT}"
echo "[launch-fleets-dist-simple-server] launcher_mode=${LAUNCHER_MODE}"
echo "[launch-fleets-dist-simple-server] enable_visual_state_publisher=${ENABLE_VISUAL_STATE_PUBLISHER}"
echo "[launch-fleets-dist-simple-server] visual_state_max_drones_per_packet=${VISUAL_STATE_MAX_DRONES_PER_PACKET}"
echo "[launch-fleets-dist-simple-server] enable_web_bridge=${ENABLE_WEB_BRIDGE}"
echo "[launch-fleets-dist-simple-server] enable_viewer_webserver=${ENABLE_VIEWER_WEBSERVER}"
echo "[launch-fleets-dist-simple-server] visual_state_global_drone_count=${VISUAL_STATE_GLOBAL_DRONE_COUNT}"
echo "[launch-fleets-dist-simple-server] visual_state_global_start_index=${VISUAL_STATE_GLOBAL_START_INDEX}"
echo "[launch-fleets-dist-simple-server] visual_state_local_start_index=${VISUAL_STATE_LOCAL_START_INDEX}"
echo "[launch-fleets-dist-simple-server] visual_state_local_drone_count=${VISUAL_STATE_LOCAL_DRONE_COUNT}"
echo "[launch-fleets-dist-simple-server] visual_state_output_chunk_base_index=${VISUAL_STATE_OUTPUT_CHUNK_BASE_INDEX}"
if [[ -n "${SHOW_ASSET_JSON}" ]]; then
  echo "[launch-fleets-dist-simple-server] show_asset_json=${SHOW_ASSET_JSON}"
  echo "[launch-fleets-dist-simple-server] show_asset_assign_mode=${SHOW_ASSET_ASSIGN_MODE}"
  echo "[launch-fleets-dist-simple-server] show_asset_speed=${SHOW_ASSET_SPEED}"
  echo "[launch-fleets-dist-simple-server] show_asset_timeout_sec=${SHOW_ASSET_TIMEOUT_SEC}"
  echo "[launch-fleets-dist-simple-server] show_asset_delta_time_msec=${SHOW_ASSET_DELTA_TIME_MSEC}"
  echo "[launch-fleets-dist-simple-server] show_asset_final_hold_extra_sec=${SHOW_ASSET_FINAL_HOLD_EXTRA_SEC}"
  echo "[launch-fleets-dist-simple-server] show_asset_z_offset_m=${SHOW_ASSET_Z_OFFSET_M}"
fi

exec env \
  CONDUCTOR_SERVER_SCRIPT="${CONDUCTOR_SERVER_SCRIPT}" \
  CONDUCTOR_SERVER_ID="${CONDUCTOR_CONFIG_ID}" \
  CONDUCTOR_MODE="${CONDUCTOR_MODE}" \
  CONDUCTOR_CONFIG_ROOT="${CONDUCTOR_CONFIG_ROOT}" \
  LAUNCHER_MODE="${LAUNCHER_MODE}" \
  ENABLE_VISUAL_STATE_PUBLISHER="${ENABLE_VISUAL_STATE_PUBLISHER}" \
  VISUAL_STATE_MAX_DRONES_PER_PACKET="${VISUAL_STATE_MAX_DRONES_PER_PACKET}" \
  VISUAL_STATE_GLOBAL_DRONE_COUNT="${VISUAL_STATE_GLOBAL_DRONE_COUNT}" \
  VISUAL_STATE_GLOBAL_START_INDEX="${VISUAL_STATE_GLOBAL_START_INDEX}" \
  VISUAL_STATE_LOCAL_START_INDEX="${VISUAL_STATE_LOCAL_START_INDEX}" \
  VISUAL_STATE_LOCAL_DRONE_COUNT="${VISUAL_STATE_LOCAL_DRONE_COUNT}" \
  VISUAL_STATE_OUTPUT_CHUNK_BASE_INDEX="${VISUAL_STATE_OUTPUT_CHUNK_BASE_INDEX}" \
  ENABLE_WEB_BRIDGE="${ENABLE_WEB_BRIDGE}" \
  ENABLE_VIEWER_WEBSERVER="${ENABLE_VIEWER_WEBSERVER}" \
  SHOW_ASSET_JSON="${SHOW_ASSET_JSON}" \
  SHOW_ASSET_ASSIGN_MODE="${SHOW_ASSET_ASSIGN_MODE}" \
  SHOW_ASSET_SPEED="${SHOW_ASSET_SPEED}" \
  SHOW_ASSET_TIMEOUT_SEC="${SHOW_ASSET_TIMEOUT_SEC}" \
  SHOW_ASSET_DELTA_TIME_MSEC="${SHOW_ASSET_DELTA_TIME_MSEC}" \
  SHOW_ASSET_FINAL_HOLD_EXTRA_SEC="${SHOW_ASSET_FINAL_HOLD_EXTRA_SEC}" \
  SHOW_ASSET_Z_OFFSET_M="${SHOW_ASSET_Z_OFFSET_M}" \
  SHOW_ASSET_NAME="${SHOW_ASSET_NAME}" \
  SHOW_ASSET_SUMMARY_JSON="${SHOW_ASSET_SUMMARY_JSON}" \
  bash "${PROJECT_ROOT}/tools/launch-fleets-scale-perf.bash" "${DRONE_COUNT}" "" "${PROC_COUNT}"
