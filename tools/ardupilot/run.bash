#!/bin/bash

if [ $# -ne 2 ] && [ $# -ne 3 ]; then
    echo "Usage: $0 <ardupilot-path> <HOST_IP> [instance-id]"
    exit 1
fi

ARDUPILOT_DIR=${1}
HOST_IP=${2}
INSTANCE=${3:-0}

cd ${ARDUPILOT_DIR}

WSL_IP=`ip -4 addr show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}'`

# Calculate ports based on instance ID
MAVLINK_OUT_PORT=$((14550 + 10 * INSTANCE))
SIM_PORT_IN=9003
SIM_PORT_OUT=9002

echo "Starting instance ${INSTANCE}"
echo "  MAVLink out: udp:${HOST_IP}:${MAVLINK_OUT_PORT}"

./Tools/autotest/sim_vehicle.py -v ArduCopter -f airsim-copter  \
-A "--sim-port-in ${SIM_PORT_IN} --sim-port-out ${SIM_PORT_OUT}" \
--instance ${INSTANCE} \
--slave 0 \
--sim-address=${WSL_IP} \
--out=udp:127.0.0.1:${MAVLINK_OUT_PORT} \
--out=udp:${HOST_IP}:${MAVLINK_OUT_PORT}
