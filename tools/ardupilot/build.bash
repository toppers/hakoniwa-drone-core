#!/bin/bash

if [ ! -d hakoniwa-drone-core ]
then
    echo "Please run this script from the root of the repository."
    exit 1
fi
if [ ! -d ardupilot ]
then
    echo "Please run this script from the root of the repository."
    exit 1
fi


cd ardupilot
./Tools/environment_install/install-prereqs-ubuntu.sh -y
pip3 install empy==3.3.4 future MAVProxy
./waf configure --board sitl
./waf copter
