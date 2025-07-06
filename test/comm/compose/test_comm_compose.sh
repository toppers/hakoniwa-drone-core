#!/bin/bash
# SPEC: docs/test/comm/compose/test_comm_compose.md#TEST001
set -e
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
REPO_ROOT=$(cd "$SCRIPT_DIR/../../.." && pwd)
PROTO=${1:-tcp}
export PROTO
cd "$REPO_ROOT"

if ! command -v docker > /dev/null; then
    echo "docker not available, skipping compose test" > "$SCRIPT_DIR/compose.log"
    exit 0
fi

LOGFILE="$SCRIPT_DIR/${PROTO}_compose.log"
docker compose up --build --exit-code-from client > "$LOGFILE" 2>&1 || {
    docker compose down >> "$LOGFILE" 2>&1 || true
    cat "$LOGFILE"
    exit 1
}

docker compose down >> "$LOGFILE" 2>&1 || true

grep -q "PASSED" "$LOGFILE"
