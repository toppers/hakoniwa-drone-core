#!/bin/bash

if [ $# -ne 1 ]
then
    echo "Usage: $0 <config-path>"
    exit 1
fi

# check if the config path is a valid file
if [ ! -f "$1" ]; then
    echo "Error: Config path '$1' is not a valid file."
    exit 1
fi
# check the absolute path of the config directory
CONFIG_PATH=$(realpath "$1")

if [ ! -d "drone_api" ]; then
    echo "Error: drone_api directory not found."
    exit 1
fi

cd drone_api

export PYTHONPATH=${PYTHONPATH}:`pwd`
export PYTHONPATH=${PYTHONPATH}:`pwd`/assets
export PYTHONPATH=${PYTHONPATH}:`pwd`/assets/lib

cd assets
python3 hako_env_event.py ${CONFIG_PATH} 20 config
