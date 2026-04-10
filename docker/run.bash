#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 必要環境（HOST_WORKDIR / DOCKER_DIR など）は env.bash で設定している想定
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/env.bash"

HAKONIWA_TOP_DIR="$(pwd)"
IMAGE_NAME="$(cat "${SCRIPT_DIR}/image_name.txt")"
IMAGE_TAG="$(cat "${SCRIPT_DIR}/latest_version.txt")"
DOCKER_IMAGE="toppersjp/${IMAGE_NAME}:${IMAGE_TAG}"
CONTAINER_NAME="${IMAGE_NAME}"
RUN_DETACHED=0

PRO_PATH=""
LAUNCHER_SCRIPT=""
LAUNCHER_ARGS=()
DOCKER_TTY_MODE="${DOCKER_TTY_MODE:-auto}"

usage() {
  cat <<'EOF'
Usage:
  bash docker/run.bash [-p PRO_PATH] [--launcher SCRIPT] [-- launcher_args...]

Examples:
  bash docker/run.bash
  bash docker/run.bash -p /path/to/lnx.zip
  bash docker/run.bash --launcher tools/launch-mujoco-web-bridge-ubuntu.bash
  bash docker/run.bash --launcher tools/launch-fleets-scale-perf.bash -- 100 "" 4

Env:
  DOCKER_TTY_MODE=auto|always|never
EOF
}

map_launcher_path_for_container() {
  local launcher_path="$1"
  if [[ "${launcher_path}" = /* ]]; then
    case "${launcher_path}" in
      "${HOST_WORKDIR}"/*)
        printf "%s\n" "${DOCKER_DIR}${launcher_path#${HOST_WORKDIR}}"
        ;;
      *)
        echo "[run] Error: absolute launcher path must be under HOST_WORKDIR: ${launcher_path}" >&2
        exit 1
        ;;
    esac
  else
    printf "%s\n" "${launcher_path}"
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -p)
      PRO_PATH="${2:-}"
      if [[ -z "${PRO_PATH}" ]]; then
        echo "[run] Error: -p requires a path" >&2
        exit 1
      fi
      PRO_PATH="$(cd "$(dirname "${PRO_PATH}")" && pwd)/$(basename "${PRO_PATH}")"
      shift 2
      ;;
    --launcher)
      LAUNCHER_SCRIPT="${2:-}"
      if [[ -z "${LAUNCHER_SCRIPT}" ]]; then
        echo "[run] Error: --launcher requires a script path" >&2
        exit 1
      fi
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    --)
      shift
      LAUNCHER_ARGS=("$@")
      break
      ;;
    *)
      echo "[run] Error: unsupported option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

# --- 2) 共通フラグ（ここに PRO の -v/-e も後段で積む） -----------------------
TTY_FLAGS=(--rm)
case "${DOCKER_TTY_MODE}" in
  auto)
    if [[ -t 0 && -t 1 ]]; then
      TTY_FLAGS=(-it --rm)
    else
      RUN_DETACHED=1
    fi
    ;;
  always)
    TTY_FLAGS=(-it --rm)
    ;;
  never)
    RUN_DETACHED=1
    ;;
  *)
    echo "[run] Error: invalid DOCKER_TTY_MODE: ${DOCKER_TTY_MODE}" >&2
    exit 1
    ;;
esac

RUN_FLAGS=(
  "${TTY_FLAGS[@]}"
  -w "${DOCKER_DIR}"
  --name "${CONTAINER_NAME}"
  -e TZ=Asia/Tokyo
  -v "${HOST_WORKDIR}:${DOCKER_DIR}"
)

# --- 3) -p が指定されていれば存在チェック → マウント + 環境変数 ------------
if [[ -n "${PRO_PATH}" ]]; then
  if [[ -f "${PRO_PATH}" ]]; then
    echo "[run] Using PRO ZIP: ${PRO_PATH}"
    RUN_FLAGS+=(-v "${PRO_PATH}:/opt/pro/lnx.zip:ro" -e HAKO_PRO_PACKAGE="/opt/pro/lnx.zip")
  elif [[ -d "${PRO_PATH}" ]]; then
    echo "[run] Using PRO DIR: ${PRO_PATH}"
    RUN_FLAGS+=(-v "${PRO_PATH}:/opt/pro/lnx:ro" -e HAKO_PRO_DIR="/opt/pro/lnx")
  else
    echo "[run] Error: -p path is not valid: ${PRO_PATH}" >&2
    exit 1
  fi
else
  echo "[run] No PRO package/dir specified."
fi

# --- 4) OS/ARCH に応じたネットワーク・プラットフォーム設定 -----------------
ARCH="$(arch)"
OS_TYPE="$("${SCRIPT_DIR}/utils/detect_os_type.bash")"
PORT="${PORT:-8765}"

echo "[run] ARCH=${ARCH}"
echo "[run] OS_TYPE=${OS_TYPE}"
echo "[run] IMAGE=${DOCKER_IMAGE}"
echo "[run] WORKDIR host=${HOST_WORKDIR} -> container=${DOCKER_DIR}"

PLATFORM_FLAG=()
NET_FLAG=()

if [[ "${OS_TYPE}" == "Mac" ]]; then
  # macOS は --net=host が使えない → ポートフォワード
  NET_FLAG=(-p "${PORT}:${PORT}")
  # Apple Silicon は x86_64 強制
  if [[ "${ARCH}" == "arm64" ]]; then
    PLATFORM_FLAG=(--platform linux/amd64)
  fi
else
  # Linux は host ネットワーク
  NET_FLAG=(--net host)
fi

# --- 4.5) GLFW のための X11 受け渡し -----------------------------------------
# ホスト側に X サーバがある場合（Linux/WSLg など）は DISPLAY をそのまま渡し、
# X11 ソケットをマウントする。無い場合はヘッドレス（xvfb）で動かす。
if [[ -n "${DISPLAY:-}" ]]; then
  echo "[run] Enable X11 forwarding for GLFW (DISPLAY=${DISPLAY})"
  RUN_FLAGS+=(
    -e DISPLAY="${DISPLAY}"
    -v /tmp/.X11-unix:/tmp/.X11-unix
  )
  # 物理 GPU を使える環境なら /dev/dri を渡す（無ければスキップで可）
  if [[ -d /dev/dri ]]; then
    RUN_FLAGS+=(--device /dev/dri)
  fi
else
  echo "[run] DISPLAY not set → run in headless (software GL)"
  RUN_FLAGS+=(
    -e LIBGL_ALWAYS_SOFTWARE=1
  )
  # もしイメージに xvfb が入っていてエントリポイントが GUI 前提なら
  # コンテナ内で xvfb-run するためのフラグも渡す（任意）
  RUN_FLAGS+=(-e HAKO_USE_XVFB=1)
fi

CONTAINER_COMMAND=()
if [[ -n "${LAUNCHER_SCRIPT}" ]]; then
  CONTAINER_LAUNCHER_SCRIPT="$(map_launcher_path_for_container "${LAUNCHER_SCRIPT}")"
  CONTAINER_COMMAND=(bash "${CONTAINER_LAUNCHER_SCRIPT}" "${LAUNCHER_ARGS[@]}")
  echo "[run] LAUNCHER=${CONTAINER_LAUNCHER_SCRIPT}"
  if [[ ${#LAUNCHER_ARGS[@]} -gt 0 ]]; then
    echo "[run] LAUNCHER_ARGS=${LAUNCHER_ARGS[*]}"
  fi
fi

cleanup_container() {
  docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true
}

on_signal() {
  local sig="$1"
  echo "[run] ${sig} received -> stopping container ${CONTAINER_NAME}"
  cleanup_container
  exit 130
}

trap 'on_signal SIGINT' INT
trap 'on_signal SIGTERM' TERM
trap 'cleanup_container' EXIT

# --- 5) 実行 -------------------------------------------------------------------
if [[ "${RUN_DETACHED}" == "1" ]]; then
  echo "[run] MODE=detached"
  docker run -d "${PLATFORM_FLAG[@]}" "${RUN_FLAGS[@]}" "${NET_FLAG[@]}" "${DOCKER_IMAGE}" "${CONTAINER_COMMAND[@]}" >/dev/null
  docker wait "${CONTAINER_NAME}" >/dev/null
else
  docker run "${PLATFORM_FLAG[@]}" "${RUN_FLAGS[@]}" "${NET_FLAG[@]}" "${DOCKER_IMAGE}" "${CONTAINER_COMMAND[@]}"
fi
