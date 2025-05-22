#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source ${SCRIPT_DIR}/env.bash

IMAGE_NAME=`cat ${SCRIPT_DIR}/image_name.txt`
IMAGE_TAG=`cat ${SCRIPT_DIR}/latest_version.txt`
DOCKER_IMAGE=${IMAGE_NAME}:${IMAGE_TAG}

docker pull toppersjp/${DOCKER_IMAGE}
