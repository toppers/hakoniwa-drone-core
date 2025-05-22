#!/bin/bash

if [ $# -ne 2 ]
then
    echo "Usage: $0 <hakoniwa-webserver-path> <config-path>"
    exit 1
fi

WEBSERVER_DIR=${1}
CONFIG_PATH=${2}

cd ${WEBSERVER_DIR}

python3 -m server.main --asset_name WebServer --config_path ${CONFIG_PATH} --delta_time_usec 20000
