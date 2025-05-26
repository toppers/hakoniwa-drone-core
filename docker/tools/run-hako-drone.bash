#!/bin/bash

if [ $# -ne 3 ]
then
    echo "Usage: $0 <hakoniwa-drone-core-path> <config-path> {rc|api}"
    exit 1
fi

DRONECORE_DIR=${1}
CONFIG_PATH=${2}
OPTION=${3}

cd ${DRONECORE_DIR}

if [ ${OPTION} != "rc" ] && [ ${OPTION} != "api" ]
then
    echo "Invalid option: ${OPTION}. Use 'rc' or 'api'."
    exit 1
fi
linux-main_hako_drone_service ./config/drone/${OPTION} ${CONFIG_PATH}
