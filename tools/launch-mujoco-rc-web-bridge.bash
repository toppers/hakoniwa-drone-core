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

OS="$(uname)"
if [[ -z "${HAKO_DRONE_SERVICE_BIN:-}" ]]; then
  if [[ "${OS}" == "Darwin" ]]; then
    if [[ -x "/usr/local/bin/hakoniwa/mac-main_hako_drone_service" ]]; then
      export HAKO_DRONE_SERVICE_BIN="/usr/local/bin/hakoniwa/mac-main_hako_drone_service"
    else
      export HAKO_DRONE_SERVICE_BIN="${PROJECT_ROOT}/mac/mac-main_hako_drone_service"
    fi
  else
    if [[ -x "/usr/local/bin/hakoniwa/linux-main_hako_drone_service" ]]; then
      export HAKO_DRONE_SERVICE_BIN="/usr/local/bin/hakoniwa/linux-main_hako_drone_service"
    else
      export HAKO_DRONE_SERVICE_BIN="${PROJECT_ROOT}/lnx/linux-main_hako_drone_service"
    fi
  fi
fi

if [[ -z "${HAKO_VISUAL_STATE_PUBLISHER_BIN:-}" ]]; then
  if [[ "${OS}" == "Darwin" ]]; then
    if [[ -x "/usr/local/bin/hakoniwa/mac-drone_visual_state_publisher" ]]; then
      export HAKO_VISUAL_STATE_PUBLISHER_BIN="/usr/local/bin/hakoniwa/mac-drone_visual_state_publisher"
    else
      export HAKO_VISUAL_STATE_PUBLISHER_BIN="${PROJECT_ROOT}/src/cmake-build/assets/visual_state_publisher/drone_visual_state_publisher"
    fi
  else
    if [[ -x "/usr/local/bin/hakoniwa/linux-drone_visual_state_publisher" ]]; then
      export HAKO_VISUAL_STATE_PUBLISHER_BIN="/usr/local/bin/hakoniwa/linux-drone_visual_state_publisher"
    else
      export HAKO_VISUAL_STATE_PUBLISHER_BIN="${PROJECT_ROOT}/src/cmake-build/assets/visual_state_publisher/drone_visual_state_publisher"
    fi
  fi
fi
export HAKO_VISUAL_STATE_PUBLISHER_CONFIG="${HAKO_VISUAL_STATE_PUBLISHER_CONFIG:-config/assets/visual_state_publisher/visual_state_publisher-1.json}"

if [[ -z "${HAKO_WEB_BRIDGE_RUNNER:-}" ]]; then
  if [[ -x "${PROJECT_ROOT}/work/hakoniwa-pdu-bridge-core/tools/run-web-bridge.bash" ]]; then
    export HAKO_WEB_BRIDGE_RUNNER="${PROJECT_ROOT}/work/hakoniwa-pdu-bridge-core/tools/run-web-bridge.bash"
  else
    export HAKO_WEB_BRIDGE_RUNNER="/usr/local/hakoniwa/bin/run-web-bridge.bash"
  fi
fi
if [[ -z "${HAKO_WEB_BRIDGE_CONFIG_BASE:-}" ]]; then
  if [[ -d "${PROJECT_ROOT}/work/hakoniwa-pdu-bridge-core/config" ]]; then
    export HAKO_WEB_BRIDGE_CONFIG_BASE="${PROJECT_ROOT}/work/hakoniwa-pdu-bridge-core/config"
  else
    export HAKO_WEB_BRIDGE_CONFIG_BASE="/usr/local/hakoniwa/share/hakoniwa-pdu-bridge/config"
  fi
fi

if [[ -n "${VIRTUAL_ENV:-}" && -x "${VIRTUAL_ENV}/bin/python" ]]; then
  DEFAULT_PYTHON_BIN="${VIRTUAL_ENV}/bin/python"
elif [[ "${OS}" == "Darwin" && -x "${HOME}/.pyenv/versions/3.12.3/bin/python" ]]; then
  DEFAULT_PYTHON_BIN="${HOME}/.pyenv/versions/3.12.3/bin/python"
else
  DEFAULT_PYTHON_BIN="$(command -v python3)"
fi

PYTHON_BIN="${PYTHON_BIN:-${DEFAULT_PYTHON_BIN}}"
export PYTHON_PATH="${PYTHON_PATH:-${PYTHON_BIN}}"
LAUNCHER_MODE="${LAUNCHER_MODE:-immediate}"
LAUNCH_FILE="${LAUNCH_FILE:-${PROJECT_ROOT}/config/launcher/drone-mujoco-rc-web-bridge.launch.json}"

echo "[launch-mujoco-rc-web-bridge] hako_drone_project_path=${HAKO_DRONE_PROJECT_PATH}"
echo "[launch-mujoco-rc-web-bridge] hako_threejs_viewer_path=${HAKO_THREEJS_VIEWER_PATH}"
echo "[launch-mujoco-rc-web-bridge] hako_drone_service_bin=${HAKO_DRONE_SERVICE_BIN}"
echo "[launch-mujoco-rc-web-bridge] hako_visual_state_publisher_bin=${HAKO_VISUAL_STATE_PUBLISHER_BIN}"
echo "[launch-mujoco-rc-web-bridge] hako_visual_state_publisher_config=${HAKO_VISUAL_STATE_PUBLISHER_CONFIG}"
echo "[launch-mujoco-rc-web-bridge] hako_web_bridge_runner=${HAKO_WEB_BRIDGE_RUNNER}"
echo "[launch-mujoco-rc-web-bridge] hako_web_bridge_config_base=${HAKO_WEB_BRIDGE_CONFIG_BASE}"
echo "[launch-mujoco-rc-web-bridge] python_bin=${PYTHON_BIN}"
echo "[launch-mujoco-rc-web-bridge] python_path=${PYTHON_PATH}"
echo "[launch-mujoco-rc-web-bridge] launcher_mode=${LAUNCHER_MODE}"
echo "[launch-mujoco-rc-web-bridge] launch_file=${LAUNCH_FILE}"

exec env -u PYTHONPATH "${PYTHON_BIN}" -m hakoniwa_pdu.apps.launcher.hako_launcher --mode "${LAUNCHER_MODE}" "${LAUNCH_FILE}"
