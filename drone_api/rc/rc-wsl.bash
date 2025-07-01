#!/bin/bash

DIR_PATH=`dirname $0`
#echo $DIR_PATH

cd ${DIR_PATH}
cmd.exe /c rc-custom-pdu.bat
