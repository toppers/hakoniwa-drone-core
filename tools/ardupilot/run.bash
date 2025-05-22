#!/bin/bash

if [ $# -ne 2 ]
then
    echo "Usage: $0 <ardupilot-path> <HOST_IP>"
    exit 1
fi

ARDUPILOT_DIR=${1}
cd ${ARDUPILOT_DIR}

WSL_IP=`ip -4 addr show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}'`
HOST_IP=${2}

./Tools/autotest/sim_vehicle.py -v ArduCopter -f airsim-copter -A "--sim-port-in 9003 --sim-port-out 9002"  --sim-address=${WSL_IP}  --out=udp:${HOST_IP}:14550

