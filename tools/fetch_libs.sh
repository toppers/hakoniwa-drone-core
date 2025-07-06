#!/bin/bash
# Fetch prebuilt libraries for hakoniwa-drone-core
set -e

REPO="toppers/hakoniwa-drone-core"
RELEASE=${1:-latest}

if [ "$(uname -s)" = "Darwin" ]; then
    ASSET="mac.zip"
    DIR_NAME="mac"
else
    ASSET="lnx.zip"
    DIR_NAME="lnx"
fi

WORK_DIR=$(mktemp -d)
ZIP_PATH="$WORK_DIR/$ASSET"

URL="https://github.com/${REPO}/releases/${RELEASE}/download/${ASSET}"
echo "Downloading $URL"

curl -L -o "$ZIP_PATH" "$URL"
unzip -o "$ZIP_PATH" -d "$WORK_DIR/unpack"

mkdir -p "$(dirname "$0")/../lib"
cp "$WORK_DIR/unpack/$DIR_NAME"/* "$(dirname "$0")/../lib/" 2>/dev/null || true

rm -rf "$WORK_DIR"
echo "Libraries installed to ./lib"
