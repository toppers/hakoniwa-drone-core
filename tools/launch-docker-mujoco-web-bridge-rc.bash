#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

export HAKO_DRONE_PROJECT_PATH="${HAKO_DRONE_PROJECT_PATH:-${PROJECT_ROOT}}"

if [[ -n "${VIRTUAL_ENV:-}" && -x "${VIRTUAL_ENV}/bin/python" ]]; then
  DEFAULT_PYTHON_BIN="${VIRTUAL_ENV}/bin/python"
else
  DEFAULT_PYTHON_BIN="$(command -v python3)"
fi

PYTHON_BIN="${PYTHON_BIN:-${DEFAULT_PYTHON_BIN}}"
LAUNCHER_MODE="${LAUNCHER_MODE:-immediate}"
LAUNCH_FILE="${LAUNCH_FILE:-${PROJECT_ROOT}/config/launcher/docker-mujoco-web-bridge-rc-win.launch.json}"

echo "[launch-docker-mujoco-web-bridge-rc] hako_drone_project_path=${HAKO_DRONE_PROJECT_PATH}"
echo "[launch-docker-mujoco-web-bridge-rc] python_bin=${PYTHON_BIN}"
echo "[launch-docker-mujoco-web-bridge-rc] launcher_mode=${LAUNCHER_MODE}"
echo "[launch-docker-mujoco-web-bridge-rc] launch_file=${LAUNCH_FILE}"

exec env -u PYTHONPATH "${PYTHON_BIN}" -m hakoniwa_pdu.apps.launcher.hako_launcher --mode "${LAUNCHER_MODE}" "${LAUNCH_FILE}"
