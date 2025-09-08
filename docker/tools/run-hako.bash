#!/bin/bash

if [ $# -ne 1 ] && [ $# -ne 2 ] && [ $# -ne 3 ]
then
    echo "Usage: $0 {px4|ardupilot|rc|api} [config-path] [drone-num]"
    exit 1
fi

HAKO_DRONE_PID=
HAKO_WEB_PID=
HAKO_REAL_PID=
HAKO_WIND_PID=
kill_children() {
    local pid=$1
    echo "Now killing $pid"
    for child in $(ps --ppid $pid -o pid=); do
        kill_children $child
    done
    kill -9 $pid 2>/dev/null
}

kill_processes() {
    if [ -n "$HAKO_DRONE_PID" ]; then
        kill_children $HAKO_DRONE_PID
    fi
    if [ -n "$HAKO_WEB_PID" ]; then
        kill_children $HAKO_WEB_PID
    fi
    if [ -n "$HAKO_REAL_PID" ]; then
        kill_children $HAKO_REAL_PID
    fi
    if [ -n "$HAKO_WIND_PID" ]; then
        kill_children $HAKO_WIND_PID
    fi
    echo "All processes killed"
    exit 0
}


function signal_handler() {
    echo "Signal received"
    kill_processes
}
trap signal_handler SIGINT

BASE_DIR=`pwd`

if [ ! -d hakoniwa-drone-core ]
then
    echo "ERROR: can not find hakoniwa-drone-core"
    exit 1
fi
if [ ! -d hakoniwa-webserver ]
then
    echo "ERROR: can not find hakoniwa-webserver"
    exit 1
fi

RUN_MODE=${1}
CONFIG_PATH=${2:-hakoniwa-drone-core/config/pdudef/webavatar.json}
CONFIG_PATH=${BASE_DIR}/${CONFIG_PATH}
DRONE_NUM=${3:-1}

if [ $RUN_MODE = "px4" ]
then
     setsid bash hakoniwa-drone-core/docker/tools/run-hako-px4.bash ${BASE_DIR}/hakoniwa-drone-core ${CONFIG_PATH} ${DRONE_NUM} &
     HAKO_DRONE_PID=$!
     sleep 2
elif [ $RUN_MODE = "ardupilot" ]
then
     setsid bash hakoniwa-drone-core/docker/tools/run-hako-ardupilot.bash ${BASE_DIR}/hakoniwa-drone-core ${CONFIG_PATH} ${DRONE_NUM} &
     HAKO_DRONE_PID=$!
     sleep 2
elif [ $RUN_MODE = "rc" -o $RUN_MODE = "api" ]
then
     setsid bash hakoniwa-drone-core/docker/tools/run-hako-drone.bash ${BASE_DIR}/hakoniwa-drone-core ${CONFIG_PATH} ${RUN_MODE}-${DRONE_NUM} &
     HAKO_DRONE_PID=$!
     sleep 2

     #setsid bash hakoniwa-drone-core/docker/tools/run-hako-real.bash ${BASE_DIR}/hakoniwa-drone-core ${BASE_DIR}/hakoniwa-drone-core/config/pdudef/webavatar.json &
     #HAKO_REAL_PID=$!
else
    echo "ERROR: not supported mode: ${RUN_MODE}"
    exit 1
fi

curr_dir=$(pwd)
cd ${BASE_DIR}/hakoniwa-drone-core
setsid bash drone_api/assets/run-wind.bash  ${CONFIG_PATH} &
HAKO_WIND_PID=$!
cd ${curr_dir}
sleep 2


hako-cmd start

sleep 3

setsid bash hakoniwa-drone-core/docker/tools/run-webserver.bash ${BASE_DIR}/hakoniwa-webserver ${CONFIG_PATH} &
HAKO_WEB_PID=$!
echo "WEBSERVER PID: ${HAKO_WEB_PID}"

sleep 1

while [ 1 ]; do
    sleep 1
done
