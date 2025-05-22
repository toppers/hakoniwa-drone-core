#!/bin/bash

if [ $# -ne 2 ]
then
    echo "Usage: $0 <hakoniwa-drone-core-path> <config-path>"
    exit 1
fi

DRONECORE_DIR=${1}
CONFIG_PATH=${2}

cd ${DRONECORE_DIR}

linux-main_hako_aircraft_service_px4 127.0.0.1 4560 ./config/drone/px4 ${CONFIG_PATH}
