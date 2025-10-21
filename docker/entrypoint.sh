#!/usr/bin/env bash
set -euo pipefail

BIN_DIR="/usr/local/bin/hakoniwa"
LIB_DIR="/usr/local/lib/hakoniwa"
STAMP="/var/lib/hakoniwa/.pro_installed"
mkdir -p "$(dirname "$STAMP")"

# --- ユーザ指定対応（指定がなければデフォルト値を採用） ---
HAKO_PRO_PACKAGE="${HAKO_PRO_PACKAGE:-/opt/pro/lnx.zip}"
HAKO_PRO_DIR="${HAKO_PRO_DIR:-/opt/pro/lnx}"

install_from_dir () {
  local src="$1"
  echo "[hako-entry] Installing PRO from directory: $src"
  cp -f "$src"/linux-* "$BIN_DIR"/ 2>/dev/null || true
  chmod +x "$BIN_DIR"/linux-* 2>/dev/null || true
  cp -f "$src"/libhako_service_c.so "$LIB_DIR"/ 2>/dev/null || true
  ldconfig || true
  echo "pro" > "$STAMP"
}

install_from_zip () {
  local zip="$1"
  echo "[hako-entry] Installing PRO from zip: $zip"
  tmpd="$(mktemp -d)"
  unzip -q "$zip" -d "$tmpd"
  if [ -d "$tmpd/lnx" ]; then
    install_from_dir "$tmpd/lnx"
  else
    install_from_dir "$tmpd"
  fi
  rm -rf "$tmpd"
}

did_install="no"

# --- PRO 資材があれば上書き、なければスキップ ---
if [ -f "$HAKO_PRO_PACKAGE" ]; then
  install_from_zip "$HAKO_PRO_PACKAGE"
  did_install="yes"
elif [ -d "$HAKO_PRO_DIR" ]; then
  install_from_dir "$HAKO_PRO_DIR"
  did_install="yes"
fi

if [ "$did_install" = "yes" ]; then
  echo "[hako-entry] PRO binaries installed (override done)."
else
  echo "[hako-entry] No PRO package or directory found. Using default (OSS) binaries."
fi

# 引数があればそれを実行、なければbash
exec "$@"
