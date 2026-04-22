#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

SERVICE_CONFIG="${REPO_ROOT}/config/drone/fleets/services/api-current-service.json"
SHOW_JSON="${REPO_ROOT}/config/drone-show-config/show-h-a-100-ref.json"
DRONES_CSV=""
DRONE_COUNT=""
ASSIGN_MODE="index"
TAKEOFF_ALT=""
SPEED_M_S="1.5"
TOLERANCE_M="0.5"
TIMEOUT_SEC="120.0"
TIMEOUT_SEC_EXPLICIT="0"
DO_LAND="0"
SERIAL_MODE="0"
BATCH_SIZE="0"
BATCH_INIT=""
BATCH_GOTO=""
BATCH_LAND=""
INIT_RETRY_MAX=""
INIT_RETRY_INTERVAL_SEC=""
READY_GATE_TIMEOUT_SEC=""
READY_GATE_INTERVAL_SEC=""
READY_GATE_CALL_TIMEOUT_SEC=""
NO_READY_GATE="0"
PROC_COUNT="1"
INIT_CONCURRENCY_PER_PROC="12"
USE_ASYNC_SHARED="0"

usage() {
  cat <<'EOF'
Usage:
  bash drone_api/external_rpc/apps/run_show.bash [options]

Options:
  --service-config PATH
  --show-json PATH
  --show-config PATH   # alias of --show-json
  --drones CSV
  --drone-count N
  --assign-mode index|nearest
  --takeoff-alt M
  --speed MPS
  --tolerance M
  --timeout-sec SEC
  --batch-size N      # 0:auto, <0:off, >0:chunk size
  --batch-init N      # set_ready/takeoff 用
  --batch-goto N      # goto 用
  --batch-land N      # land 用
  --init-retry-max N  # set_ready/takeoff の最大リトライ回数
  --init-retry-interval-sec SEC  # set_ready/takeoff のリトライ間隔[sec]
  --ready-gate-timeout-sec SEC   # set_ready前のget_state到達待ちタイムアウト
  --ready-gate-interval-sec SEC  # set_ready前のget_state再確認間隔
  --ready-gate-call-timeout-sec SEC # ready gate 1回あたりの待ち時間
  --no-ready-gate                # ready gate無効化
  --proc-count N                 # drone-service プロセス数(初期化バッチ自動計算用)
  --init-concurrency-per-proc N  # 1プロセスあたりの初期化同時実行数
  --use-async-shared
  --land
  --serial
  -h, --help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    --service-config) SERVICE_CONFIG="$2"; shift 2 ;;
    --show-json|--show-config) SHOW_JSON="$2"; shift 2 ;;
    --drones) DRONES_CSV="$2"; shift 2 ;;
    --drone-count) DRONE_COUNT="$2"; shift 2 ;;
    --assign-mode) ASSIGN_MODE="$2"; shift 2 ;;
    --takeoff-alt) TAKEOFF_ALT="$2"; shift 2 ;;
    --speed) SPEED_M_S="$2"; shift 2 ;;
    --tolerance) TOLERANCE_M="$2"; shift 2 ;;
    --timeout-sec) TIMEOUT_SEC="$2"; TIMEOUT_SEC_EXPLICIT="1"; shift 2 ;;
    --batch-size) BATCH_SIZE="$2"; shift 2 ;;
    --batch-init) BATCH_INIT="$2"; shift 2 ;;
    --batch-goto) BATCH_GOTO="$2"; shift 2 ;;
    --batch-land) BATCH_LAND="$2"; shift 2 ;;
    --init-retry-max) INIT_RETRY_MAX="$2"; shift 2 ;;
    --init-retry-interval-sec) INIT_RETRY_INTERVAL_SEC="$2"; shift 2 ;;
    --ready-gate-timeout-sec) READY_GATE_TIMEOUT_SEC="$2"; shift 2 ;;
    --ready-gate-interval-sec) READY_GATE_INTERVAL_SEC="$2"; shift 2 ;;
    --ready-gate-call-timeout-sec) READY_GATE_CALL_TIMEOUT_SEC="$2"; shift 2 ;;
    --no-ready-gate) NO_READY_GATE="1"; shift 1 ;;
    --proc-count) PROC_COUNT="$2"; shift 2 ;;
    --init-concurrency-per-proc) INIT_CONCURRENCY_PER_PROC="$2"; shift 2 ;;
    --use-async-shared) USE_ASYNC_SHARED="1"; shift 1 ;;
    --land) DO_LAND="1"; shift 1 ;;
    --serial) SERIAL_MODE="1"; shift 1 ;;
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
DRONE_TOTAL="${#DRONES[@]}"
if [[ "${TIMEOUT_SEC_EXPLICIT}" == "0" ]]; then
  if (( DRONE_TOTAL >= 200 )); then
    TIMEOUT_SEC="180.0"
  elif (( DRONE_TOTAL >= 128 )); then
    TIMEOUT_SEC="150.0"
  elif (( DRONE_TOTAL >= 64 )); then
    TIMEOUT_SEC="120.0"
  fi
fi

echo "[show-runner] service_config=${SERVICE_CONFIG}"
echo "[show-runner] show_json=${SHOW_JSON}"
echo "[show-runner] drones=${DRONES[*]}"
echo "[show-runner] assign_mode=${ASSIGN_MODE} timeout_sec=${TIMEOUT_SEC}"
echo "[show-runner] batch_size=${BATCH_SIZE}"
[[ -n "${BATCH_INIT}" ]] && echo "[show-runner] batch_init=${BATCH_INIT}"
[[ -n "${BATCH_GOTO}" ]] && echo "[show-runner] batch_goto=${BATCH_GOTO}"
[[ -n "${BATCH_LAND}" ]] && echo "[show-runner] batch_land=${BATCH_LAND}"
[[ -n "${INIT_RETRY_MAX}" ]] && echo "[show-runner] init_retry_max=${INIT_RETRY_MAX}"
[[ -n "${INIT_RETRY_INTERVAL_SEC}" ]] && echo "[show-runner] init_retry_interval_sec=${INIT_RETRY_INTERVAL_SEC}"
[[ -n "${READY_GATE_TIMEOUT_SEC}" ]] && echo "[show-runner] ready_gate_timeout_sec=${READY_GATE_TIMEOUT_SEC}"
[[ -n "${READY_GATE_INTERVAL_SEC}" ]] && echo "[show-runner] ready_gate_interval_sec=${READY_GATE_INTERVAL_SEC}"
[[ -n "${READY_GATE_CALL_TIMEOUT_SEC}" ]] && echo "[show-runner] ready_gate_call_timeout_sec=${READY_GATE_CALL_TIMEOUT_SEC}"
[[ "${NO_READY_GATE}" == "1" ]] && echo "[show-runner] ready_gate=off"
echo "[show-runner] proc_count=${PROC_COUNT}"
echo "[show-runner] init_concurrency_per_proc=${INIT_CONCURRENCY_PER_PROC}"
[[ "${USE_ASYNC_SHARED}" == "1" ]] && echo "[show-runner] use_async_shared=1"

CMD=(
  python3 "${SCRIPT_DIR}/show_runner.py"
  --service-config "${SERVICE_CONFIG}"
  --show-json "${SHOW_JSON}"
  --drones "${DRONES[@]}"
  --assign-mode "${ASSIGN_MODE}"
  --speed "${SPEED_M_S}"
  --tolerance "${TOLERANCE_M}"
  --timeout-sec "${TIMEOUT_SEC}"
  --batch-size "${BATCH_SIZE}"
  --proc-count "${PROC_COUNT}"
  --init-concurrency-per-proc "${INIT_CONCURRENCY_PER_PROC}"
)

if [[ -n "${TAKEOFF_ALT}" ]]; then
  CMD+=(--takeoff-alt "${TAKEOFF_ALT}")
fi
if [[ -n "${BATCH_INIT}" ]]; then
  CMD+=(--batch-init "${BATCH_INIT}")
fi
if [[ -n "${BATCH_GOTO}" ]]; then
  CMD+=(--batch-goto "${BATCH_GOTO}")
fi
if [[ -n "${BATCH_LAND}" ]]; then
  CMD+=(--batch-land "${BATCH_LAND}")
fi
if [[ -n "${INIT_RETRY_MAX}" ]]; then
  CMD+=(--init-retry-max "${INIT_RETRY_MAX}")
fi
if [[ -n "${INIT_RETRY_INTERVAL_SEC}" ]]; then
  CMD+=(--init-retry-interval-sec "${INIT_RETRY_INTERVAL_SEC}")
fi
if [[ -n "${READY_GATE_TIMEOUT_SEC}" ]]; then
  CMD+=(--ready-gate-timeout-sec "${READY_GATE_TIMEOUT_SEC}")
fi
if [[ -n "${READY_GATE_INTERVAL_SEC}" ]]; then
  CMD+=(--ready-gate-interval-sec "${READY_GATE_INTERVAL_SEC}")
fi
if [[ -n "${READY_GATE_CALL_TIMEOUT_SEC}" ]]; then
  CMD+=(--ready-gate-call-timeout-sec "${READY_GATE_CALL_TIMEOUT_SEC}")
fi
if [[ "${NO_READY_GATE}" == "1" ]]; then
  CMD+=(--no-ready-gate)
fi
if [[ "${DO_LAND}" == "1" ]]; then
  CMD+=(--land)
fi
if [[ "${SERIAL_MODE}" == "1" ]]; then
  CMD+=(--serial)
fi
if [[ "${USE_ASYNC_SHARED}" == "1" ]]; then
  CMD+=(--use-async-shared)
fi

"${CMD[@]}"
echo "[show-runner] done"
