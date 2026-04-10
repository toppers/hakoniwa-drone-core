#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

export HAKO_DRONE_PROJECT_PATH="${HAKO_DRONE_PROJECT_PATH:-${PROJECT_ROOT}}"
if [[ -z "${HAKO_DRONE_SERVICE_BIN:-}" ]]; then
  if [[ -x "/usr/local/bin/hakoniwa/linux-main_hako_drone_service" ]]; then
    export HAKO_DRONE_SERVICE_BIN="/usr/local/bin/hakoniwa/linux-main_hako_drone_service"
  else
    export HAKO_DRONE_SERVICE_BIN="${PROJECT_ROOT}/lnx/linux-main_hako_drone_service"
  fi
fi
export HAKO_WEB_BRIDGE_RUNNER="${HAKO_WEB_BRIDGE_RUNNER:-/usr/local/hakoniwa/bin/run-web-bridge.bash}"
export HAKO_WEB_BRIDGE_CONFIG_BASE="${HAKO_WEB_BRIDGE_CONFIG_BASE:-/usr/local/hakoniwa/share/hakoniwa-pdu-bridge/config}"

if [[ -n "${VIRTUAL_ENV:-}" && -x "${VIRTUAL_ENV}/bin/python" ]]; then
  DEFAULT_PYTHON_BIN="${VIRTUAL_ENV}/bin/python"
else
  DEFAULT_PYTHON_BIN="$(command -v python3)"
fi
PYTHON_BIN="${PYTHON_BIN:-${DEFAULT_PYTHON_BIN}}"
LAUNCHER_MODE="${LAUNCHER_MODE:-immediate}"
LAUNCH_FILE="${LAUNCH_FILE:-${PROJECT_ROOT}/config/launcher/drone-mujoco-web-bridge-ubuntu.launch.json}"

echo "[launch-mujoco-web-bridge-ubuntu] hako_drone_project_path=${HAKO_DRONE_PROJECT_PATH}"
echo "[launch-mujoco-web-bridge-ubuntu] hako_drone_service_bin=${HAKO_DRONE_SERVICE_BIN}"
echo "[launch-mujoco-web-bridge-ubuntu] hako_web_bridge_runner=${HAKO_WEB_BRIDGE_RUNNER}"
echo "[launch-mujoco-web-bridge-ubuntu] hako_web_bridge_config_base=${HAKO_WEB_BRIDGE_CONFIG_BASE}"
echo "[launch-mujoco-web-bridge-ubuntu] python_bin=${PYTHON_BIN}"
echo "[launch-mujoco-web-bridge-ubuntu] launcher_mode=${LAUNCHER_MODE}"
echo "[launch-mujoco-web-bridge-ubuntu] launch_file=${LAUNCH_FILE}"

exec env -u PYTHONPATH "${PYTHON_BIN}" -m hakoniwa_pdu.apps.launcher.hako_launcher --mode "${LAUNCHER_MODE}" "${LAUNCH_FILE}"
