#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source ${SCRIPT_DIR}/env.bash

HAKONIWA_TOP_DIR=`pwd`
IMAGE_NAME=`cat ${SCRIPT_DIR}/image_name.txt`
IMAGE_TAG=`cat ${SCRIPT_DIR}/latest_version.txt`

DOCKER_IMAGE=${IMAGE_NAME}:${IMAGE_TAG}

DOCKER_ID=`docker ps | grep "${DOCKER_IMAGE}" | awk '{print $1}'`

docker exec -it ${DOCKER_ID} /bin/bash
