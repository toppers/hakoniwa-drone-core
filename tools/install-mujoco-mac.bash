#!/bin/bash

if [ $# -ne 1 ]
then
    echo "Usage: $0 {install_dir}"
    exit 1
fi

INSTALL_DIR=${1}
MUJOCO_VERSION=$(cat MUJOCO_VERSION.txt)

mkdir -p ${INSTALL_DIR}/vendor/mujoco
mkdir -p ${INSTALL_DIR}/vendor/mujoco/include
mkdir -p ${INSTALL_DIR}/vendor/mujoco/lib
mkdir -p ${INSTALL_DIR}/vendor/mujoco/include/mujoco

if [ ! -f mujoco-${MUJOCO_VERSION}-macos-universal2.dmg ]
then
    echo "Downloading MuJoCo ${MUJOCO_VERSION}..."
    curl -L -O https://github.com/google-deepmind/mujoco/releases/download/${MUJOCO_VERSION}/mujoco-${MUJOCO_VERSION}-macos-universal2.dmg
fi

hdiutil attach mujoco-${MUJOCO_VERSION}-macos-universal2.dmg -mountpoint /Volumes/MuJoCo
cp -rp /Volumes/MuJoCo/MuJoCo.app/Contents/Frameworks/MuJoCo.framework ${INSTALL_DIR}/vendor/mujoco/
hdiutil detach /Volumes/MuJoCo

cp -R ${INSTALL_DIR}/vendor/mujoco/MuJoCo.framework/Headers/* ${INSTALL_DIR}/vendor/mujoco/include/mujoco/
cp ${INSTALL_DIR}/vendor/mujoco/MuJoCo.framework/Versions/Current/libmujoco.${MUJOCO_VERSION}.dylib ${INSTALL_DIR}/vendor/mujoco/lib/

echo "SUCCESS"
