#!/bin/bash


HOST_MOUNT_PATH=$1

docker run -it --rm \
  --name ardupilot-sitl \
  -p 5760:5760 \
  -p 14550:14550 \
  -p 9002:9002/udp \
  -p 9003:9003/udp \
  ardupilot-sitl


#　./Tools/autotest/sim_vehicle.py -v ArduCopter -f airsim-copter -A "--sim-port-in=9003 --sim-port-out=9002" --out=udp:192.168.2.107:14550

