#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

export HAKO_DRONE_PROJECT_PATH="${HAKO_DRONE_PROJECT_PATH:-${PROJECT_ROOT}}"
export HAKO_DRONE_SERVICE_BIN="${HAKO_DRONE_SERVICE_BIN:-/usr/local/bin/hakoniwa/linux-main_hako_aircraft_service_px4}"
export HAKO_VISUAL_STATE_PUBLISHER_BIN="${HAKO_VISUAL_STATE_PUBLISHER_BIN:-/usr/local/bin/hakoniwa/linux-drone_visual_state_publisher}"
export HAKO_WEB_BRIDGE_RUNNER="${HAKO_WEB_BRIDGE_RUNNER:-/usr/local/hakoniwa/bin/hakoniwa-pdu-web-bridge}"
export HAKO_WEB_BRIDGE_CONFIG_BASE="${HAKO_WEB_BRIDGE_CONFIG_BASE:-/usr/local/hakoniwa/share/hakoniwa-pdu-bridge/config}"
export HAKO_THREEJS_VIEWER_PATH="${HAKO_THREEJS_VIEWER_PATH:-/opt/hakoniwa-threejs-drone}"

PYTHON_BIN="${PYTHON_BIN:-python3}"
LAUNCH_FILE="${LAUNCH_FILE:-${PROJECT_ROOT}/config/launcher/mujoco-px4-web-bridge-wsl2.launch.json}"

exec env -u PYTHONPATH "${PYTHON_BIN}" -m hakoniwa_pdu.apps.launcher.hako_launcher \
  --mode "${LAUNCHER_MODE:-immediate}" "${LAUNCH_FILE}"
