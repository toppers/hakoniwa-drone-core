#!/bin/bash
set -e
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
REPO_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)

# Fetch libraries if not present
if [ ! -d "$REPO_ROOT/lib" ]; then
    "$SCRIPT_DIR/fetch_libs.sh" || echo "Failed to download libs"
fi

BUILD_DIR="$REPO_ROOT/test/build"
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"
cmake ..
cmake --build .
ctest --output-on-failure
