#!/bin/bash

if [ $# -ne 2 ]
then
    echo "Usage: $0 <hakoniwa-drone-core-path> <config-path>"
    exit 1
fi

DRONE_CORE_DIR=${1}
CONFIG_PATH=${2}

cd ${DRONE_CORE_DIR}/drone_api

python3 -m rc.real_time_syncher ${CONFIG_PATH} 20