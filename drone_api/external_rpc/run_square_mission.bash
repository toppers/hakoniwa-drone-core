#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

SERVICE_CONFIG="${REPO_ROOT}/config/drone/fleets/services/api-current-service.json"
DRONE_NAME="Drone-1"
DRONES_CSV=""
DRONE_COUNT=""
ALT_M="0.5"
CENTER_X="0.0"
CENTER_Y="0.0"
Z_M="0.5"
LAYER_SIZE="8"
LAYER_STEP="1.0"
SIDE_M="4.0"
SPEED_M_S="1.0"
TOLERANCE_M="0.5"
TIMEOUT_SEC="30.0"
TIMEOUT_SEC_EXPLICIT="0"
YAW_DEG="0.0"
PHASE_STEP="0"
DO_LAND="0"
SERIAL_MODE="0"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --service-config) SERVICE_CONFIG="$2"; shift 2 ;;
    --drone) DRONE_NAME="$2"; shift 2 ;;
    --drones) DRONES_CSV="$2"; shift 2 ;;
    --drone-count) DRONE_COUNT="$2"; shift 2 ;;
    --alt) ALT_M="$2"; shift 2 ;;
    --center-x) CENTER_X="$2"; shift 2 ;;
    --center-y) CENTER_Y="$2"; shift 2 ;;
    --z) Z_M="$2"; shift 2 ;;
    --layer-size) LAYER_SIZE="$2"; shift 2 ;;
    --layer-step) LAYER_STEP="$2"; shift 2 ;;
    --side) SIDE_M="$2"; shift 2 ;;
    --speed) SPEED_M_S="$2"; shift 2 ;;
    --tolerance) TOLERANCE_M="$2"; shift 2 ;;
    --timeout-sec) TIMEOUT_SEC="$2"; TIMEOUT_SEC_EXPLICIT="1"; shift 2 ;;
    --yaw) YAW_DEG="$2"; shift 2 ;;
    --phase-step) PHASE_STEP="$2"; shift 2 ;;
    --land) DO_LAND="1"; shift 1 ;;
    --serial) SERIAL_MODE="1"; shift 1 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

HALF_SIDE=$(python3 - <<PY
side = float("${SIDE_M}")
print(side / 2.0)
PY
)

P1_X=$(python3 - <<PY
print(float("${CENTER_X}") - float("${HALF_SIDE}"))
PY
)
P1_Y=$(python3 - <<PY
print(float("${CENTER_Y}") - float("${HALF_SIDE}"))
PY
)
P2_X=$(python3 - <<PY
print(float("${CENTER_X}") + float("${HALF_SIDE}"))
PY
)
P2_Y="${P1_Y}"
P3_X="${P2_X}"
P3_Y=$(python3 - <<PY
print(float("${CENTER_Y}") + float("${HALF_SIDE}"))
PY
)
P4_X="${P1_X}"
P4_Y="${P3_Y}"

echo "[square-mission] service_config=${SERVICE_CONFIG}"
echo "[square-mission] square center=(${CENTER_X}, ${CENTER_Y}) side=${SIDE_M} z=${Z_M}"

if [[ -z "${DRONES_CSV}" && -n "${DRONE_COUNT}" ]]; then
  if ! [[ "${DRONE_COUNT}" =~ ^[0-9]+$ ]] || [[ "${DRONE_COUNT}" -lt 1 ]]; then
    echo "Invalid --drone-count: ${DRONE_COUNT} (must be integer >= 1)" >&2
    exit 1
  fi
  DRONES_CSV="$(seq -s, -f "Drone-%g" 1 "${DRONE_COUNT}")"
fi

if [[ -n "${DRONES_CSV}" ]]; then
  IFS=',' read -r -a DRONES <<< "${DRONES_CSV}"
  DRONE_TOTAL="${#DRONES[@]}"
  if [[ "${TIMEOUT_SEC_EXPLICIT}" == "0" ]]; then
    if (( DRONE_TOTAL >= 200 )); then
      TIMEOUT_SEC="120.0"
    elif (( DRONE_TOTAL >= 128 )); then
      TIMEOUT_SEC="90.0"
    elif (( DRONE_TOTAL >= 64 )); then
      TIMEOUT_SEC="60.0"
    fi
  fi
  echo "[square-mission] drones=${DRONES[*]}"
  echo "[square-mission] timeout_sec=${TIMEOUT_SEC}"
  CMD=(
    python3 "${SCRIPT_DIR}/fleet_square_mission.py"
    --service-config "${SERVICE_CONFIG}"
    --drones "${DRONES[@]}"
    --alt "${ALT_M}"
    --center-x "${CENTER_X}" --center-y "${CENTER_Y}"
    --side "${SIDE_M}" --z "${Z_M}"
    --layer-size "${LAYER_SIZE}" --layer-step "${LAYER_STEP}"
    --phase-step "${PHASE_STEP}"
    --speed "${SPEED_M_S}" --tolerance "${TOLERANCE_M}" --timeout-sec "${TIMEOUT_SEC}"
    --yaw "${YAW_DEG}"
  )
  if [[ "${DO_LAND}" == "1" ]]; then
    CMD+=(--land)
  fi
  if [[ "${SERIAL_MODE}" == "1" ]]; then
    CMD+=(--serial)
  fi
  "${CMD[@]}"
  echo "[square-mission] done"
  exit 0
fi

echo "[square-mission] drone=${DRONE_NAME}"

python3 "${SCRIPT_DIR}/set_ready_client.py" "${SERVICE_CONFIG}" "${DRONE_NAME}"
python3 "${SCRIPT_DIR}/takeoff_client.py" "${SERVICE_CONFIG}" "${DRONE_NAME}" "${ALT_M}"

goto_point() {
  local x="$1"
  local y="$2"
  python3 "${SCRIPT_DIR}/goto_client.py" \
    --service-config "${SERVICE_CONFIG}" \
    --drone "${DRONE_NAME}" \
    --speed "${SPEED_M_S}" \
    --tolerance "${TOLERANCE_M}" \
    --timeout-sec "${TIMEOUT_SEC}" \
    "${x}" "${y}" "${Z_M}" "${YAW_DEG}"
}

goto_point "${P1_X}" "${P1_Y}"
goto_point "${P2_X}" "${P2_Y}"
goto_point "${P3_X}" "${P3_Y}"
goto_point "${P4_X}" "${P4_Y}"
goto_point "${P1_X}" "${P1_Y}"

if [[ "${DO_LAND}" == "1" ]]; then
  python3 "${SCRIPT_DIR}/land_client.py" "${SERVICE_CONFIG}" "${DRONE_NAME}"
fi

echo "[square-mission] done"
