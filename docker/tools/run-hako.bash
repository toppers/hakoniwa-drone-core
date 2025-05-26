#!/bin/bash

if [ $# -ne 1 ]
then
    echo "Usage: $0 {px4|ardupilot|rc|api}"
    exit 1
fi

HAKO_DRONE_PID=
HAKO_WEB_PID=
HAKO_REAL_PID=
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

if [ $RUN_MODE = "px4" ]
then
     setsid bash hakoniwa-drone-core/docker/tools/run-hako-px4.bash ${BASE_DIR}/hakoniwa-drone-core ${BASE_DIR}/hakoniwa-drone-core/config/pdudef/webavatar.json &
     HAKO_DRONE_PID=$!
     sleep 2
elif [ $RUN_MODE = "ardupilot" ]
then
     setsid bash hakoniwa-drone-core/docker/tools/run-hako-ardupilot.bash ${BASE_DIR}/hakoniwa-drone-core ${BASE_DIR}/hakoniwa-drone-core/config/pdudef/webavatar.json &
     HAKO_DRONE_PID=$!
     sleep 2
elif [ $RUN_MODE = "rc" -o $RUN_MODE = "api" ]
then
     setsid bash hakoniwa-drone-core/docker/tools/run-hako-drone.bash ${BASE_DIR}/hakoniwa-drone-core ${BASE_DIR}/hakoniwa-drone-core/config/pdudef/webavatar.json $RUN_MODE &
     HAKO_DRONE_PID=$!
     sleep 2

     setsid bash hakoniwa-drone-core/docker/tools/run-hako-real.bash ${BASE_DIR}/hakoniwa-drone-core ${BASE_DIR}/hakoniwa-drone-core/config/pdudef/webavatar.json &
     HAKO_REAL_PID=$!
     sleep 2
else
    echo "ERROR: not supported mode: ${RUN_MODE}"
    exit 1
fi

hako-cmd start

sleep 3

setsid bash hakoniwa-drone-core/docker/tools/run-webserver.bash ${BASE_DIR}/hakoniwa-webserver ${BASE_DIR}/hakoniwa-drone-core/config/pdudef/webavatar.json &
HAKO_WEB_PID=$!
echo "WEBSERVER PID: ${HAKO_WEB_PID}"

sleep 1

while [ 1 ]; do
    sleep 1
done
