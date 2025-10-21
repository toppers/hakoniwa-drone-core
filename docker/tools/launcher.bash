#!/bin/bash

if [ $# -ne 1 ]; then
    echo "Usage: $0 <launcher_config_path>"
    exit 1
fi
if [ ! -f "$1" ]; then
    echo "Error: Config file '$1' not found!"
    exit 1
fi
launcher_config_path="$1"
export WSL_IP=`ip -4 addr show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}'`
export DIRNAME=$(basename $(pwd))
python3 -m hakoniwa_pdu.apps.launcher.hako_launcher --mode immediate $launcher_config_path
 