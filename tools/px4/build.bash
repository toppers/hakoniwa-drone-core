#!/bin/bash

if [ ! -d hakoniwa-drone-core ]
then
    echo "Please run this script from the root of the repository."
    exit 1
fi
if [ ! -d PX4-Autopilot ]
then
    echo "Please run this script from the root of the repository."
    exit 1
fi

PX4_TOO_DIR=hakoniwa-drone-core/tools/px4
#cp ${PX4_TOO_DIR}/config/10016_none_iris PX4-Autopilot/ROMFS/px4fmu_common/init.d-posix/airframes/10016_none_iris

cd PX4-Autopilot
bash Tools/setup/ubuntu.sh --no-nuttx --no-sim-tools
make px4_sitl_default
