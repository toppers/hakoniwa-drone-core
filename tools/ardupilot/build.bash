#!/bin/bash

ARDUPILOT_DIR=${1:-ardupilot}

if [ ! -d hakoniwa-drone-core ]
then
    echo "Please run this script from the root of the repository."
    exit 1
fi
if [ ! -d "${ARDUPILOT_DIR}" ]
then
    echo "ArduPilot directory '${ARDUPILOT_DIR}' not found."
    echo "Usage: $0 [path_to_ardupilot_directory]"
    exit 1
fi


cd "${ARDUPILOT_DIR}"
./Tools/environment_install/install-prereqs-ubuntu.sh -y
pip3 install empy==3.3.4 future MAVProxy
./waf configure --board sitl
./waf copter