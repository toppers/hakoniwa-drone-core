#!/bin/bash

if [ $# -ne 2 ]
then
    echo "Usage: $0 <hakoniwa-drone-core-path> <config-path>"
    exit 1
fi

DRONECORE_DIR=${1}
CONFIG_PATH=${2}

cd ${DRONECORE_DIR}/drone_api

export PYTHONPATH=${PYTHONPATH}:`pwd`
export PYTHONPATH=${PYTHONPATH}:`pwd`/assets
export PYTHONPATH=${PYTHONPATH}:`pwd`/assets/lib

cd assets
python3 hako_env_event.py ${CONFIG_PATH} 20 config
