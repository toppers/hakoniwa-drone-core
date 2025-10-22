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

# --- 1) -p オプション（PRO 資材のパス） --------------------------------------
PRO_PATH=""
if [[ "${1:-}" == "-p" ]]; then
  PRO_PATH="${2:-}"
  # 追加：相対パスを絶対パスに変換
  PRO_PATH="$(cd "$(dirname "${PRO_PATH}")" && pwd)/$(basename "${PRO_PATH}")"
  shift 2
fi

# --- 2) 共通フラグ（ここに PRO の -v/-e も後段で積む） -----------------------
RUN_FLAGS=(
  -it --rm
  -w "${DOCKER_DIR}"
  --name "${IMAGE_NAME}"
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

# --- 5) 実行 -------------------------------------------------------------------
docker run "${PLATFORM_FLAG[@]}" "${RUN_FLAGS[@]}" "${NET_FLAG[@]}" "${DOCKER_IMAGE}"
