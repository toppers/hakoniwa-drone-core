#!/bin/bash

if [ $# -ne 3 ]
then
	echo "Usage: $0 <PDU_CONFIG_PATH> <SERVICE_CONFIG_PATH> <HAKO_BINARY_PATH>"
	exit 1
fi
export PDU_CONFIG_PATH=$1
export SERVICE_CONFIG_PATH=$2
export HAKO_BINARY_PATH=$3

 python -m hakoniwa_pdu.apps.mcp.server --manual
