#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

DRONE_COUNT="${1:-}"
PROC_COUNT="${2:-4}"

if [[ -z "${DRONE_COUNT}" ]]; then
  cat <<'EOF' >&2
Usage:
  bash drone_api/external_rpc/apps/run_show_scale_bench.bash DRONE_COUNT [PROC_COUNT] [extra run_show.bash args...]

Examples:
  bash drone_api/external_rpc/apps/run_show_scale_bench.bash 100 4
  bash drone_api/external_rpc/apps/run_show_scale_bench.bash 200 4 --speed 14.0
  bash drone_api/external_rpc/apps/run_show_scale_bench.bash 512 8 --timeout-sec 240
EOF
  exit 1
fi

shift
if [[ $# -gt 0 && "$1" =~ ^[0-9]+$ ]]; then
  PROC_COUNT="$1"
  shift
fi

case "${DRONE_COUNT}" in
  100)
    SHOW_JSON="${REPO_ROOT}/config/drone-show-config/show-hakoniwa-100-ref.json"
    ;;
  200)
    SHOW_JSON="${REPO_ROOT}/config/drone-show-config/show-hakoniwa-drone-icon-drone-show-3step-200-ref.json"
    ;;
  400)
    SHOW_JSON="${REPO_ROOT}/config/drone-show-config/show-hakoniwa-drone-icon-drone-show-3step-400-ref.json"
    ;;
  512)
    SHOW_JSON="${REPO_ROOT}/config/drone-show-config/show-hakoniwa-drone-icon-drone-show-3step-512-ref.json"
    ;;
  *)
    echo "Unsupported DRONE_COUNT: ${DRONE_COUNT} (supported: 100, 200, 400, 512)" >&2
    exit 1
    ;;
esac

INIT_CONCURRENCY_PER_PROC="${INIT_CONCURRENCY_PER_PROC:-10}"
SPEED_M_S="${SPEED_M_S:-14.0}"
BATCH_INIT="${BATCH_INIT:-${DRONE_COUNT}}"
BATCH_GOTO="${BATCH_GOTO:-${DRONE_COUNT}}"
TIMEOUT_SEC="${TIMEOUT_SEC:-}"
LOG_DIR="${LOG_DIR:-${REPO_ROOT}/tmp/show-scale-bench}"
LOG_STEM="${LOG_STEM:-show_scale}"

if [[ -z "${TIMEOUT_SEC}" ]]; then
  if (( DRONE_COUNT >= 512 )); then
    TIMEOUT_SEC="240"
  elif (( DRONE_COUNT >= 400 )); then
    TIMEOUT_SEC="180"
  elif (( DRONE_COUNT >= 200 )); then
    TIMEOUT_SEC="150"
  else
    TIMEOUT_SEC="120"
  fi
fi

echo "[show-scale-bench] show_json=${SHOW_JSON}"
echo "[show-scale-bench] drone_count=${DRONE_COUNT}"
echo "[show-scale-bench] proc_count=${PROC_COUNT}"
echo "[show-scale-bench] init_concurrency_per_proc=${INIT_CONCURRENCY_PER_PROC}"
echo "[show-scale-bench] batch_init=${BATCH_INIT}"
echo "[show-scale-bench] batch_goto=${BATCH_GOTO}"
echo "[show-scale-bench] speed=${SPEED_M_S}"
echo "[show-scale-bench] timeout_sec=${TIMEOUT_SEC}"

mkdir -p "${LOG_DIR}"
LOG_PATH="${LOG_DIR}/${LOG_STEM}_n${DRONE_COUNT}_p${PROC_COUNT}.log"
echo "[show-scale-bench] log_path=${LOG_PATH}"

exec bash "${SCRIPT_DIR}/run_show.bash" \
  --show-config "${SHOW_JSON}" \
  --drone-count "${DRONE_COUNT}" \
  --assign-mode nearest \
  --proc-count "${PROC_COUNT}" \
  --init-concurrency-per-proc "${INIT_CONCURRENCY_PER_PROC}" \
  --batch-init "${BATCH_INIT}" \
  --batch-goto "${BATCH_GOTO}" \
  --speed "${SPEED_M_S}" \
  --timeout-sec "${TIMEOUT_SEC}" \
  --use-async-shared \
  "$@" | tee "${LOG_PATH}"
