#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

SERVICE_CONFIG="${REPO_ROOT}/config/drone/fleets/services/api-current-service.json"
SHOW_JSON="${REPO_ROOT}/config/drone-show-config/show-h-a-100-ref.json"
PDU_CONFIG=""
DRONES_CSV=""
DRONE_COUNT=""
ASSET_NAME="ShowRunnerAsset"
PROC_COUNT="1"
SUMMARY_JSON=""
ASSIGN_MODE="index"
TAKEOFF_ALT=""
Z_OFFSET_M="0.0"
SPEED_M_S="1.5"
TOLERANCE_M="0.5"
TIMEOUT_SEC="90.0"
DELTA_TIME_MSEC="20"
FINAL_HOLD_EXTRA_SEC="5.0"
DO_LAND="0"

usage() {
  cat <<'EOF'
Usage:
  bash drone_api/external_rpc/apps/run_show_asset.bash [options]

Options:
  --service-config PATH
  --show-json PATH
  --show-config PATH   # alias of --show-json
  --pdu-config PATH
  --drones CSV
  --drone-count N
  --asset-name NAME
  --proc-count N
  --summary-json PATH
  --assign-mode index|nearest
  --takeoff-alt M
  --z-offset-m M
  --speed MPS
  --tolerance M
  --timeout-sec SEC
  --delta-time-msec MSEC
  --final-hold-extra-sec SEC
  --land
  -h, --help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    --service-config) SERVICE_CONFIG="$2"; shift 2 ;;
    --show-json|--show-config) SHOW_JSON="$2"; shift 2 ;;
    --pdu-config) PDU_CONFIG="$2"; shift 2 ;;
    --drones) DRONES_CSV="$2"; shift 2 ;;
    --drone-count) DRONE_COUNT="$2"; shift 2 ;;
    --asset-name) ASSET_NAME="$2"; shift 2 ;;
    --proc-count) PROC_COUNT="$2"; shift 2 ;;
    --summary-json) SUMMARY_JSON="$2"; shift 2 ;;
    --assign-mode) ASSIGN_MODE="$2"; shift 2 ;;
    --takeoff-alt) TAKEOFF_ALT="$2"; shift 2 ;;
    --z-offset-m) Z_OFFSET_M="$2"; shift 2 ;;
    --speed) SPEED_M_S="$2"; shift 2 ;;
    --tolerance) TOLERANCE_M="$2"; shift 2 ;;
    --timeout-sec) TIMEOUT_SEC="$2"; shift 2 ;;
    --delta-time-msec) DELTA_TIME_MSEC="$2"; shift 2 ;;
    --final-hold-extra-sec) FINAL_HOLD_EXTRA_SEC="$2"; shift 2 ;;
    --land) DO_LAND="1"; shift 1 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "${DRONES_CSV}" && -n "${DRONE_COUNT}" ]]; then
  if ! [[ "${DRONE_COUNT}" =~ ^[0-9]+$ ]] || [[ "${DRONE_COUNT}" -lt 1 ]]; then
    echo "Invalid --drone-count: ${DRONE_COUNT} (must be integer >= 1)" >&2
    exit 1
  fi
  DRONES_CSV="$(seq -s, -f "Drone-%g" 1 "${DRONE_COUNT}")"
fi

if [[ -z "${DRONES_CSV}" ]]; then
  echo "--drones or --drone-count is required" >&2
  exit 1
fi

IFS=',' read -r -a DRONES <<< "${DRONES_CSV}"

echo "[show-asset-runner] service_config=${SERVICE_CONFIG}"
echo "[show-asset-runner] show_json=${SHOW_JSON}"
echo "[show-asset-runner] drones=${DRONES[*]}"
echo "[show-asset-runner] assign_mode=${ASSIGN_MODE} timeout_sec=${TIMEOUT_SEC}"
echo "[show-asset-runner] asset_name=${ASSET_NAME} delta_time_msec=${DELTA_TIME_MSEC}"
echo "[show-asset-runner] z_offset_m=${Z_OFFSET_M}"
echo "[show-asset-runner] final_hold_extra_sec=${FINAL_HOLD_EXTRA_SEC}"
echo "[show-asset-runner] proc_count=${PROC_COUNT}"
[[ -n "${SUMMARY_JSON}" ]] && echo "[show-asset-runner] summary_json=${SUMMARY_JSON}"

CMD=(
  python3 "${SCRIPT_DIR}/show_asset_runner.py"
  --service-config "${SERVICE_CONFIG}"
  --show-json "${SHOW_JSON}"
  --drones "${DRONES[@]}"
  --asset-name "${ASSET_NAME}"
  --proc-count "${PROC_COUNT}"
  --assign-mode "${ASSIGN_MODE}"
  --z-offset-m "${Z_OFFSET_M}"
  --speed "${SPEED_M_S}"
  --tolerance "${TOLERANCE_M}"
  --timeout-sec "${TIMEOUT_SEC}"
  --delta-time-msec "${DELTA_TIME_MSEC}"
  --final-hold-extra-sec "${FINAL_HOLD_EXTRA_SEC}"
)

if [[ -n "${PDU_CONFIG}" ]]; then
  CMD+=(--pdu-config-path "${PDU_CONFIG}")
fi
if [[ -n "${SUMMARY_JSON}" ]]; then
  CMD+=(--summary-json "${SUMMARY_JSON}")
fi
if [[ -n "${TAKEOFF_ALT}" ]]; then
  CMD+=(--takeoff-alt "${TAKEOFF_ALT}")
fi
if [[ "${DO_LAND}" == "1" ]]; then
  CMD+=(--land)
fi

"${CMD[@]}"
echo "[show-asset-runner] done"
