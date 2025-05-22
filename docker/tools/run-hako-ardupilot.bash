#!/bin/bash

if [ $# -ne 2 ]
then
    echo "Usage: $0 <hakoniwa-drone-core-path> <config-path>"
    exit 1
fi

DRONECORE_DIR=${1}
CONFIG_PATH=${2}

cd ${DRONECORE_DIR}
WSL_IP=`ip -4 addr show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}'`
linux-main_hako_aircraft_service_ardupilot ${WSL_IP} 9002 9003 ./config/drone/ardupilot ${CONFIG_PATH}

