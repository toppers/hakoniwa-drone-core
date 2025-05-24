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

PX4_DIR=PX4-Autopilot
cd ${PX4_DIR}

WSL_IP=`ip -4 addr show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}'`
export PX4_HOME_LAT=47.641468
export PX4_HOME_LON=-122.140165
export PX4_HOME_ALT=0.0
export PX4_SIM_HOSTNAME=127.0.0.1
#export PX4_SIM_HOSTNAME=${WSL_IP}
make px4_sitl none_iris