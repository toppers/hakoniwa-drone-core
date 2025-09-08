#!/bin/bash

if [ $# -ne 1 ] && [ $# -ne 2 ]; then
    echo "Usage: $0 [path_to_px4_directory] [instance-id]"
    exit 1
fi

PX4_DIR=${1:-PX4-Autopilot}
INSTANCE=${2:-0}
if [ ! -d hakoniwa-drone-core ]
then
    echo "Please run this script from the root of the repository."
    exit 1
fi
if [ ! -d "${PX4_DIR}" ]
then
    echo "Please run this script from the root of the repository."
    exit 1
fi

cd ${PX4_DIR}

WSL_IP=`ip -4 addr show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}'`
export PX4_HOME_LAT=47.641468
export PX4_HOME_LON=-122.140165
export PX4_HOME_ALT=0.0
export PX4_SIM_HOSTNAME=127.0.0.1
#export PX4_SIM_HOSTNAME=${WSL_IP}
export PX4_MAVLINK_UDP_PORT=$((14550 + INSTANCE))
export PX4_SIM_PORT=$((4560 + INSTANCE))
PX4_SIM_MODEL=none_iris ./build/px4_sitl_default/bin/px4 -i ${INSTANCE} 
