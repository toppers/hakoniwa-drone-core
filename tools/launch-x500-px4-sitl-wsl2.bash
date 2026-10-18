#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

export HAKO_DRONE_PROJECT_PATH="${HAKO_DRONE_PROJECT_PATH:-${PROJECT_ROOT}}"
export HAKO_DRONE_SERVICE_BIN="${HAKO_DRONE_SERVICE_BIN:-/usr/local/bin/hakoniwa/linux-main_hako_aircraft_service_px4}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
LAUNCH_FILE="${LAUNCH_FILE:-${PROJECT_ROOT}/config/launcher/x500-px4-sitl-wsl2.launch.json}"

exec env -u PYTHONPATH "${PYTHON_BIN}" -m hakoniwa_pdu.apps.launcher.hako_launcher \
  --mode "${LAUNCHER_MODE:-immediate}" "${LAUNCH_FILE}"
