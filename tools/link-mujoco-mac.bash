#!/usr/bin/env bash
set -euo pipefail

# link-mujoco-mac.bash
# Usage:
#   link-mujoco-mac.bash <target-dir> (--lib-dir <DIR> | --framework-dir <DIR>)
#
# Examples:
#   link-mujoco-mac.bash ./out --lib-dir "/Users/you/project/vendor/mujoco/lib"
#   link-mujoco-mac.bash ./out --framework-dir "/Users/you/project/vendor/mujoco"
#
# This script scans executables inside <target-dir> and fixes MuJoCo dynamic linking:
# - If --lib-dir is provided (recommended): switch dependency to @rpath/libmujoco.<ver>.dylib
#   and add rpath to the provided directory.
# - If --framework-dir is provided: keep framework reference and add rpath to that dir.
#
# Notes:
# - Requires: otool, install_name_tool
# - Safe to run multiple times (adds rpath idempotently; -change ignored when not present).

if [[ $# -lt 3 ]]; then
  echo "Usage: $0 <target-dir> (--lib-dir <DIR> | --framework-dir <DIR>)" >&2
  exit 1
fi

TARGET_DIR="$1"; shift
MODE="$1"; shift
VALUE="${1:-}"; shift || true

if [[ ! -d "$TARGET_DIR" ]]; then
  echo "Target dir not found: $TARGET_DIR" >&2
  exit 1
fi

if ! command -v otool >/dev/null || ! command -v install_name_tool >/dev/null; then
  echo "otool/install_name_tool is required on macOS." >&2
  exit 1
fi

LIB_MODE=""
case "$MODE" in
  --lib-dir)
    [[ -d "$VALUE" ]] || { echo "--lib-dir not found: $VALUE" >&2; exit 1; }
    # detect actual dylib version in lib dir (e.g., libmujoco.3.3.6.dylib)
    dylib_path="$(ls "$VALUE"/libmujoco.*.dylib 2>/dev/null | head -n1 || true)"
    if [[ -z "${dylib_path}" ]]; then
      echo "MuJoCo dylib not found in $VALUE (expected libmujoco.*.dylib)" >&2
      exit 1
    fi
    dylib_base="$(basename "$dylib_path")" # libmujoco.X.Y.Z.dylib
    LIB_MODE="dylib"
    ;;
  --framework-dir)
    [[ -d "$VALUE" ]] || { echo "--framework-dir not found: $VALUE" >&2; exit 1; }
    # Accept MuJoCo.framework or mujoco.framework (case-insensitive FS usually ok)
    if [[ ! -d "$VALUE/MuJoCo.framework" && ! -d "$VALUE/mujoco.framework" ]]; then
      echo "Framework not found under $VALUE (MuJoCo.framework or mujoco.framework)" >&2
      exit 1
    fi
    LIB_MODE="framework"
    ;;
  *)
    echo "Unknown mode: $MODE (use --lib-dir or --framework-dir)" >&2
    exit 1
    ;;
esac

# Find candidate binaries: regular files with executable bit set (depth 1..)
bins=()
while IFS= read -r bin; do
    bins+=("$bin")
done < <(find "$TARGET_DIR" -type f -perm +111)

if [[ ${#bins[@]} -eq 0 ]]; then
  echo "No executables found in $TARGET_DIR" >&2
  exit 1
fi

echo "Scanning ${#bins[@]} executables under $TARGET_DIR ..."

fix_one_bin() {
  local bin="$1"
  # Get all linked library paths that mention mujoco
  local mujoco_deps=$(otool -L "$bin" | grep -i 'mujoco' | awk '{print $1}')

  if [[ -z "$mujoco_deps" ]]; then
    return 0
  fi

  if [[ "$LIB_MODE" == "dylib" ]]; then
    # Change framework-style references (if any) to @rpath/<dylib_base>
    for old in $mujoco_deps; do
      # Skip if it's already the target dylib
      if [[ "$old" == "@rpath/${dylib_base}" ]]; then
        continue
      fi
      install_name_tool -change "$old" "@rpath/${dylib_base}" "$bin"
    done
    # Ensure rpath to lib dir exists
    if ! otool -l "$bin" | grep -A2 LC_RPATH | grep -q "$VALUE"; then
      install_name_tool -add_rpath "$VALUE" "$bin"
    fi
    echo "[OK mac:dylib] $(basename "$bin") -> rpath += $VALUE ; dep=@rpath/${dylib_base}"

  else
    # Framework mode: just ensure rpath to framework parent is present
    if ! otool -l "$bin" | grep -A2 LC_RPATH | grep -q "$VALUE"; then
      install_name_tool -add_rpath "$VALUE" "$bin"
    fi
    echo "[OK mac:framework] $(basename "$bin") -> rpath += $VALUE"
  fi
}

for b in "${bins[@]}"; do
  fix_one_bin "$b"
done

echo "Done. Verify with: otool -l <bin> | grep -A2 LC_RPATH ; otool -L <bin> | grep -i mujoco"
