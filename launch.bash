#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <launch file>" >&2
  exit 1
fi

if [ "$(uname)" = "Linux" ]; then
  export PYTHONPATH=/usr/lib/python3/dist-packages:${PYTHONPATH:-}
fi

LAUNCH_FILE=$1
if [[ ! -f "$LAUNCH_FILE" ]]; then
  echo "Launch file not found: $LAUNCH_FILE" >&2
  exit 1
fi

# スクリプト基準の相対パスを安定化
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 事前に HAKO_BINARY_PATH が未設定 or 空ならデフォルトをセット
: "${HAKO_BINARY_PATH:=/usr/share/hakoniwa/offset}"
export HAKO_BINARY_PATH
echo $HAKO_BINARY_PATH

python -m hakoniwa_pdu.apps.rpcserver.server_rpc \
  --pdu-config "$SCRIPT_DIR/config/pdudef/webavatar.json" \
  --service-config "$SCRIPT_DIR/config/launcher/drone_service.json" \
  --offset-path "$HAKO_BINARY_PATH" \
  --server-type drone \
  "$LAUNCH_FILE"
