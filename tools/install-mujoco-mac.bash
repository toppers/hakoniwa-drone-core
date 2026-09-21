#!/bin/bash

set -euo pipefail

if [ $# -ne 1 ]
then
    echo "Usage: $0 {install_dir}"
    exit 1
fi

INSTALL_DIR="${1}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
MUJOCO_VERSION="$(cat "${PROJECT_DIR}/MUJOCO_VERSION.txt")"
ARCHIVE_NAME="mujoco-${MUJOCO_VERSION}-macos-universal2.dmg"
ARCHIVE_DIR="${INSTALL_DIR}/vendor/downloads"
ARCHIVE_PATH="${ARCHIVE_DIR}/${ARCHIVE_NAME}"
MOUNT_POINT="$(mktemp -d "${TMPDIR:-/tmp}/mujoco-mount.XXXXXX")"
MOUNTED=0

cleanup() {
    if [ "${MOUNTED}" -eq 1 ]
    then
        hdiutil detach "${MOUNT_POINT}" >/dev/null || true
    fi
    rmdir "${MOUNT_POINT}" 2>/dev/null || true
}
trap cleanup EXIT

mkdir -p "${ARCHIVE_DIR}"
mkdir -p "${INSTALL_DIR}/vendor/mujoco/include"
mkdir -p "${INSTALL_DIR}/vendor/mujoco/lib"

if [ ! -f "${ARCHIVE_PATH}" ]
then
    echo "Downloading MuJoCo ${MUJOCO_VERSION}..."
    curl --fail --location --output "${ARCHIVE_PATH}" \
        "https://github.com/google-deepmind/mujoco/releases/download/${MUJOCO_VERSION}/${ARCHIVE_NAME}"
fi

hdiutil attach "${ARCHIVE_PATH}" -mountpoint "${MOUNT_POINT}" -nobrowse
MOUNTED=1

# vendor/mujoco is generated SDK state.  Replace versioned inputs atomically
# enough for repeated prepare runs; never leave an older dylib discoverable.
rm -rf "${INSTALL_DIR}/vendor/mujoco/MuJoCo.framework"
rm -rf "${INSTALL_DIR}/vendor/mujoco/include/mujoco"
find "${INSTALL_DIR}/vendor/mujoco/lib" -maxdepth 1 -type f \
    -name 'libmujoco.*.dylib' -delete
mkdir -p "${INSTALL_DIR}/vendor/mujoco/include/mujoco"

cp -rp "${MOUNT_POINT}/MuJoCo.app/Contents/Frameworks/MuJoCo.framework" \
    "${INSTALL_DIR}/vendor/mujoco/"
hdiutil detach "${MOUNT_POINT}"
MOUNTED=0
rmdir "${MOUNT_POINT}"

cp -R "${INSTALL_DIR}/vendor/mujoco/MuJoCo.framework/Headers/." \
    "${INSTALL_DIR}/vendor/mujoco/include/mujoco/"
cp "${INSTALL_DIR}/vendor/mujoco/MuJoCo.framework/Versions/Current/libmujoco.${MUJOCO_VERSION}.dylib" \
    "${INSTALL_DIR}/vendor/mujoco/lib/"

echo "SUCCESS"
