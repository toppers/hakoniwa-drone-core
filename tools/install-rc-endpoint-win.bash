#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DEFAULT_INSTALL_DIR_WIN='__USE_WINDOWS_LOCALAPPDATA__\Hakoniwa\rc-endpoint'
INSTALL_DIR_WIN="${INSTALL_DIR_WIN:-${DEFAULT_INSTALL_DIR_WIN}}"
INSTALL_PYTHON_DEPS="${INSTALL_PYTHON_DEPS:-1}"
HAKO_PDU_ENDPOINT_VERSION="${HAKO_PDU_ENDPOINT_VERSION:-v1.0.0}"
HAKO_PDU_ENDPOINT_RUNTIME_ZIP="${HAKO_PDU_ENDPOINT_RUNTIME_ZIP:-hakoniwa-pdu-endpoint-windows-x64-cp312.zip}"
HAKO_PDU_ENDPOINT_RUNTIME_URL="${HAKO_PDU_ENDPOINT_RUNTIME_URL:-https://github.com/hakoniwalab/hakoniwa-pdu-endpoint/releases/download/${HAKO_PDU_ENDPOINT_VERSION}/${HAKO_PDU_ENDPOINT_RUNTIME_ZIP}}"
HAKO_PDU_ENDPOINT_REPO="${HAKO_PDU_ENDPOINT_REPO:-${PROJECT_ROOT}/../hakoniwa-pdu-endpoint}"
INSTALL_ENDPOINT_DEPS="${INSTALL_ENDPOINT_DEPS:-1}"

usage() {
  cat <<'EOF'
Usage:
  bash tools/install-rc-endpoint-win.bash [INSTALL_DIR_WIN]

Env:
  INSTALL_PYTHON_DEPS=1   Install Python packages on Windows side (default: 1)
  INSTALL_ENDPOINT_DEPS=1 Run hakoniwa-pdu-endpoint installer on Windows side (default: 1)
  HAKO_PDU_ENDPOINT_REPO=../hakoniwa-pdu-endpoint
  HAKO_PDU_ENDPOINT_VERSION=v1.0.0
  HAKO_PDU_ENDPOINT_RUNTIME_URL=...

Examples:
  bash tools/install-rc-endpoint-win.bash
  bash tools/install-rc-endpoint-win.bash 'C:\hakoniwa\rc-endpoint'
  INSTALL_PYTHON_DEPS=1 bash tools/install-rc-endpoint-win.bash
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ $# -ge 1 ]]; then
  INSTALL_DIR_WIN="$1"
fi

if ! command -v powershell.exe >/dev/null 2>&1; then
  echo "[install-rc-endpoint-win] Error: powershell.exe not found" >&2
  exit 1
fi

if [[ "${INSTALL_DIR_WIN}" == "${DEFAULT_INSTALL_DIR_WIN}" ]]; then
  INSTALL_DIR_WIN="$(powershell.exe -NoProfile -Command '$dir = Join-Path $env:LOCALAPPDATA "Hakoniwa\rc-endpoint"; Write-Output $dir' | tr -d '\r')"
fi

copy_file() {
  local rel="$1"
  local src="${PROJECT_ROOT}/${rel}"
  local dst_win="${INSTALL_DIR_WIN}\\${rel//\//\\}"
  if [[ ! -f "${src}" ]]; then
    echo "[install-rc-endpoint-win] Error: required file not found: ${src}" >&2
    exit 1
  fi
  powershell.exe -NoProfile -Command "\$dst='${dst_win}'; New-Item -ItemType Directory -Force -Path (Split-Path -Parent \$dst) | Out-Null; Copy-Item -Force '$(wslpath -w "${src}")' \$dst"
  echo "[install-rc-endpoint-win] copied file: ${rel}"
}

copy_dir() {
  local rel="$1"
  local src="${PROJECT_ROOT}/${rel}"
  local dst_win="${INSTALL_DIR_WIN}\\${rel//\//\\}"
  if [[ ! -d "${src}" ]]; then
    echo "[install-rc-endpoint-win] Error: required directory not found: ${src}" >&2
    exit 1
  fi
  powershell.exe -NoProfile -Command "\$src='$(wslpath -w "${src}")'; \$dst='${dst_win}'; New-Item -ItemType Directory -Force -Path (Split-Path -Parent \$dst) | Out-Null; Copy-Item -Recurse -Force \$src \$dst"
  echo "[install-rc-endpoint-win] copied directory: ${rel}"
}

copy_win_file_from_local() {
  local src="$1"
  local dst_win="$2"
  if [[ ! -f "${src}" ]]; then
    echo "[install-rc-endpoint-win] Error: local file not found: ${src}" >&2
    exit 1
  fi
  powershell.exe -NoProfile -Command "\$dst='${dst_win}'; New-Item -ItemType Directory -Force -Path (Split-Path -Parent \$dst) | Out-Null; Copy-Item -Force '$(wslpath -w "${src}")' \$dst"
}

install_python_deps() {
  powershell.exe -NoProfile -Command "if (Get-Command py -ErrorAction SilentlyContinue) { py -3 -m pip install --upgrade pip pygame } elseif (Get-Command python -ErrorAction SilentlyContinue) { python -m pip install --upgrade pip pygame } else { throw 'Python launcher not found. Install Python or add it to PATH.' }"
  echo "[install-rc-endpoint-win] installed Python packages"
}

install_endpoint_deps() {
  local endpoint_repo="${HAKO_PDU_ENDPOINT_REPO}"
  local endpoint_installer="${endpoint_repo}/install-python-win.ps1"
  if [[ ! -f "${endpoint_installer}" ]]; then
    echo "[install-rc-endpoint-win] Error: endpoint installer not found: ${endpoint_installer}" >&2
    exit 1
  fi
  local endpoint_installer_win
  endpoint_installer_win="$(wslpath -w "${endpoint_installer}")"
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File "${endpoint_installer_win}" -Mode bootstrap -Version "${HAKO_PDU_ENDPOINT_VERSION}" -RuntimeArchiveName "${HAKO_PDU_ENDPOINT_RUNTIME_ZIP}" -RuntimeUrl "${HAKO_PDU_ENDPOINT_RUNTIME_URL}"
  echo "[install-rc-endpoint-win] installed hakoniwa-pdu and hakoniwa-pdu-endpoint"
}

echo "[install-rc-endpoint-win] project_root=${PROJECT_ROOT}"
echo "[install-rc-endpoint-win] install_dir_win=${INSTALL_DIR_WIN}"
echo "[install-rc-endpoint-win] endpoint_repo=${HAKO_PDU_ENDPOINT_REPO}"

powershell.exe -NoProfile -Command "New-Item -ItemType Directory -Force -Path '${INSTALL_DIR_WIN}' | Out-Null"

copy_file "drone_api/rc/rc-endpoint.py"
copy_dir "drone_api/rc/rc_utils"
copy_dir "drone_api/rc/rc_config"
copy_file "config/endpoint/drone-game-websocket-client.json"
copy_file "config/endpoint/comm/drone-game-websocket-client.json"
copy_file "config/endpoint/cache/latest.json"
copy_file "config/pdudef/webavatar.json"

LAUNCHER_PS1_WIN="${INSTALL_DIR_WIN}\\launch-rc-endpoint-win.ps1"
TMP_LAUNCHER_PS1="$(mktemp --suffix=.ps1)"
cat > "${TMP_LAUNCHER_PS1}" <<'EOF'
param(
    [string]$RcConfig = "drone_api/rc/rc_config/ps4-control.json",
    [string]$RobotName = "Drone",
    [int]$JoystickIndex = 0,
    [double]$PeriodSec = 0.02
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSCommandPath
Set-Location $Root
$env:PYTHONUNBUFFERED = "1"

if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 -u "drone_api/rc/rc-endpoint.py" --rc_config $RcConfig --name $RobotName --index $JoystickIndex --period-sec $PeriodSec
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python -u "drone_api/rc/rc-endpoint.py" --rc_config $RcConfig --name $RobotName --index $JoystickIndex --period-sec $PeriodSec
} else {
    throw "Python launcher not found. Install Python or add it to PATH."
}
EOF
copy_win_file_from_local "${TMP_LAUNCHER_PS1}" "${LAUNCHER_PS1_WIN}"
rm -f "${TMP_LAUNCHER_PS1}"
echo "[install-rc-endpoint-win] wrote launcher: ${LAUNCHER_PS1_WIN}"

if [[ "${INSTALL_PYTHON_DEPS}" == "1" ]]; then
  install_python_deps
fi
if [[ "${INSTALL_ENDPOINT_DEPS}" == "1" ]]; then
  install_endpoint_deps
fi

echo "[install-rc-endpoint-win] completed"
echo "[install-rc-endpoint-win] start command:"
echo "  powershell.exe -NoProfile -ExecutionPolicy Bypass -File \"${LAUNCHER_PS1_WIN}\""
