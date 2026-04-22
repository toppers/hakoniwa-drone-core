#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
OBSOLETE_DIR="${SCRIPT_DIR}/../obsolete"

SERVICE_CONFIG="${REPO_ROOT}/config/drone/fleets/services/api-current-service.json"
DRONE_NAME="Drone-1"
DRONES_CSV=""
DRONE_COUNT=""
ALT_M="0.5"
TARGET_X="2.0"
TARGET_Y="1.0"
TARGET_Z="0.1"
TARGET_YAW_DEG="-45.0"
SPEED_M_S="1.0"
TOLERANCE_M="0.5"
TIMEOUT_SEC="30.0"
DO_LAND="0"
SERIAL_MODE="0"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --service-config)
      SERVICE_CONFIG="$2"
      shift 2
      ;;
    --drone)
      DRONE_NAME="$2"
      shift 2
      ;;
    --drones)
      DRONES_CSV="$2"
      shift 2
      ;;
    --drone-count)
      DRONE_COUNT="$2"
      shift 2
      ;;
    --alt)
      ALT_M="$2"
      shift 2
      ;;
    --x)
      TARGET_X="$2"
      shift 2
      ;;
    --y)
      TARGET_Y="$2"
      shift 2
      ;;
    --z)
      TARGET_Z="$2"
      shift 2
      ;;
    --yaw)
      TARGET_YAW_DEG="$2"
      shift 2
      ;;
    --speed)
      SPEED_M_S="$2"
      shift 2
      ;;
    --tolerance)
      TOLERANCE_M="$2"
      shift 2
      ;;
    --timeout-sec)
      TIMEOUT_SEC="$2"
      shift 2
      ;;
    --land)
      DO_LAND="1"
      shift 1
      ;;
    --serial)
      SERIAL_MODE="1"
      shift 1
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

echo "[single-mission] service_config=${SERVICE_CONFIG}"
echo "[single-mission] takeoff_alt=${ALT_M}"
echo "[single-mission] goto=(${TARGET_X}, ${TARGET_Y}, ${TARGET_Z}, yaw=${TARGET_YAW_DEG})"

if [[ -z "${DRONES_CSV}" && -n "${DRONE_COUNT}" ]]; then
  if ! [[ "${DRONE_COUNT}" =~ ^[0-9]+$ ]] || [[ "${DRONE_COUNT}" -lt 1 ]]; then
    echo "Invalid --drone-count: ${DRONE_COUNT} (must be integer >= 1)" >&2
    exit 1
  fi
  DRONES_CSV="$(seq -s, -f "Drone-%g" 1 "${DRONE_COUNT}")"
fi

if [[ -n "${DRONES_CSV}" ]]; then
  IFS=',' read -r -a DRONES <<< "${DRONES_CSV}"
  echo "[single-mission] drones=${DRONES[*]}"
  CMD=(
    python3 "${SCRIPT_DIR}/fleet_single_mission.py"
    --service-config "${SERVICE_CONFIG}"
    --drones "${DRONES[@]}"
    --alt "${ALT_M}"
    --x "${TARGET_X}" --y "${TARGET_Y}" --z "${TARGET_Z}" --yaw "${TARGET_YAW_DEG}"
    --speed "${SPEED_M_S}"
    --tolerance "${TOLERANCE_M}"
    --timeout-sec "${TIMEOUT_SEC}"
  )
  if [[ "${DO_LAND}" == "1" ]]; then
    CMD+=(--land)
  fi
  if [[ "${SERIAL_MODE}" == "1" ]]; then
    CMD+=(--serial)
  fi
  "${CMD[@]}"
  echo "[single-mission] done"
  exit 0
fi

echo "[single-mission] drone=${DRONE_NAME}"
python3 "${OBSOLETE_DIR}/set_ready_client.py" "${SERVICE_CONFIG}" "${DRONE_NAME}"
python3 "${OBSOLETE_DIR}/takeoff_client.py" "${SERVICE_CONFIG}" "${DRONE_NAME}" "${ALT_M}"
python3 "${OBSOLETE_DIR}/goto_client.py" \
  --service-config "${SERVICE_CONFIG}" \
  --drone "${DRONE_NAME}" \
  --speed "${SPEED_M_S}" \
  --tolerance "${TOLERANCE_M}" \
  --timeout-sec "${TIMEOUT_SEC}" \
  "${TARGET_X}" "${TARGET_Y}" "${TARGET_Z}" "${TARGET_YAW_DEG}"
if [[ "${DO_LAND}" == "1" ]]; then
  python3 "${OBSOLETE_DIR}/land_client.py" "${SERVICE_CONFIG}" "${DRONE_NAME}"
fi

echo "[single-mission] done"
