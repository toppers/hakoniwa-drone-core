#!/bin/bash

if [ $# -ne 2 ] && [ $# -ne 3 ]
then
    echo "Usage: $0 <hakoniwa-drone-core-path> <config-path> [drone-num]"
    exit 1
fi

DRONECORE_DIR=${1}
CONFIG_PATH=${2}
DRONE_NUM=${3:-1}

SIM_PORT_IN=9003
SIM_PORT_OUT=9002

echo "Starting instance ${DRONE_NUM}"
echo "  Sim ports (in/out): ${SIM_PORT_IN}/${SIM_PORT_OUT}"
    
cd ${DRONECORE_DIR}
WSL_IP=`ip -4 addr show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}'`
linux-main_hako_aircraft_service_ardupilot ${WSL_IP} ${SIM_PORT_OUT} ${SIM_PORT_IN} ./config/drone/ardupilot-${DRONE_NUM} ${CONFIG_PATH}

