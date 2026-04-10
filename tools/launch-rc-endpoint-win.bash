#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

if ! command -v powershell.exe >/dev/null 2>&1; then
  echo "[launch-rc-endpoint-win] Error: powershell.exe not found" >&2
  exit 1
fi

DEFAULT_INSTALL_DIR_WIN="$(powershell.exe -NoProfile -Command '$dir = Join-Path $env:LOCALAPPDATA "Hakoniwa\rc-endpoint"; Write-Output $dir' | tr -d '\r')"
DEFAULT_LAUNCHER_WIN="${DEFAULT_INSTALL_DIR_WIN}\\launch-rc-endpoint-win.ps1"
FALLBACK_INSTALL_DIR_WIN='C:\project\rc-endpoint'
FALLBACK_LAUNCHER_WIN="${FALLBACK_INSTALL_DIR_WIN}\\launch-rc-endpoint-win.ps1"
RC_ENDPOINT_INSTALL_DIR_WIN="${RC_ENDPOINT_INSTALL_DIR_WIN:-}"
RC_ENDPOINT_LAUNCHER_WIN="${RC_ENDPOINT_LAUNCHER_WIN:-}"
RC_ENDPOINT_RC_CONFIG="${RC_ENDPOINT_RC_CONFIG:-drone_api/rc/rc_config/ps4-control.json}"
RC_ENDPOINT_ROBOT_NAME="${RC_ENDPOINT_ROBOT_NAME:-Drone}"
RC_ENDPOINT_JOYSTICK_INDEX="${RC_ENDPOINT_JOYSTICK_INDEX:-0}"
RC_ENDPOINT_PERIOD_SEC="${RC_ENDPOINT_PERIOD_SEC:-0.02}"

win_path_exists() {
  local path_win="$1"
  powershell.exe -NoProfile -Command "if (Test-Path '${path_win}') { exit 0 } else { exit 1 }" >/dev/null 2>&1
}

if [[ -z "${RC_ENDPOINT_LAUNCHER_WIN}" ]]; then
  if [[ -n "${RC_ENDPOINT_INSTALL_DIR_WIN}" ]]; then
    RC_ENDPOINT_LAUNCHER_WIN="${RC_ENDPOINT_INSTALL_DIR_WIN}\\launch-rc-endpoint-win.ps1"
  elif win_path_exists "${DEFAULT_LAUNCHER_WIN}"; then
    RC_ENDPOINT_INSTALL_DIR_WIN="${DEFAULT_INSTALL_DIR_WIN}"
    RC_ENDPOINT_LAUNCHER_WIN="${DEFAULT_LAUNCHER_WIN}"
  elif win_path_exists "${FALLBACK_LAUNCHER_WIN}"; then
    RC_ENDPOINT_INSTALL_DIR_WIN="${FALLBACK_INSTALL_DIR_WIN}"
    RC_ENDPOINT_LAUNCHER_WIN="${FALLBACK_LAUNCHER_WIN}"
  else
    RC_ENDPOINT_INSTALL_DIR_WIN="${DEFAULT_INSTALL_DIR_WIN}"
    RC_ENDPOINT_LAUNCHER_WIN="${DEFAULT_LAUNCHER_WIN}"
  fi
fi

if [[ -z "${RC_ENDPOINT_INSTALL_DIR_WIN}" ]]; then
  RC_ENDPOINT_INSTALL_DIR_WIN="${RC_ENDPOINT_LAUNCHER_WIN%\\launch-rc-endpoint-win.ps1}"
fi

if ! win_path_exists "${RC_ENDPOINT_LAUNCHER_WIN}"; then
  echo "[launch-rc-endpoint-win] Error: launcher not found: ${RC_ENDPOINT_LAUNCHER_WIN}" >&2
  echo "[launch-rc-endpoint-win] Hint: set RC_ENDPOINT_INSTALL_DIR_WIN or RC_ENDPOINT_LAUNCHER_WIN" >&2
  exit 1
fi

echo "[launch-rc-endpoint-win] install_dir_win=${RC_ENDPOINT_INSTALL_DIR_WIN}"
echo "[launch-rc-endpoint-win] launcher_win=${RC_ENDPOINT_LAUNCHER_WIN}"
echo "[launch-rc-endpoint-win] rc_config=${RC_ENDPOINT_RC_CONFIG}"
echo "[launch-rc-endpoint-win] robot_name=${RC_ENDPOINT_ROBOT_NAME}"
echo "[launch-rc-endpoint-win] joystick_index=${RC_ENDPOINT_JOYSTICK_INDEX}"
echo "[launch-rc-endpoint-win] period_sec=${RC_ENDPOINT_PERIOD_SEC}"

exec powershell.exe -NoProfile -ExecutionPolicy Bypass -File "${RC_ENDPOINT_LAUNCHER_WIN}" \
  -RcConfig "${RC_ENDPOINT_RC_CONFIG}" \
  -RobotName "${RC_ENDPOINT_ROBOT_NAME}" \
  -JoystickIndex "${RC_ENDPOINT_JOYSTICK_INDEX}" \
  -PeriodSec "${RC_ENDPOINT_PERIOD_SEC}"
