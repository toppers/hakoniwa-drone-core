#!/bin/bash

if [ $# -ne 2 ] && [ $# -ne 3 ]
then
    echo "Usage: $0 <hakoniwa-drone-core-path> <config-path> [drone-num]"
    exit 1
fi

DRONECORE_DIR=${1}
CONFIG_PATH=${2}
DRONE_NUM=${3:-1}
echo "Starting instance ${DRONE_NUM}"

cd ${DRONECORE_DIR}

linux-main_hako_aircraft_service_px4 127.0.0.1 4560 ./config/drone/px4-${DRONE_NUM} ${CONFIG_PATH}
