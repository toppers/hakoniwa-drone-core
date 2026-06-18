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
if [ -z "${HAKO_DRONE_PROJECT_PATH:-}" ]; then
    launcher_config_abs="$(cd "$(dirname "$launcher_config_path")" && pwd)/$(basename "$launcher_config_path")"
    case "$launcher_config_abs" in
        */config/launcher/*)
            export HAKO_DRONE_PROJECT_PATH="${launcher_config_abs%%/config/launcher/*}"
            ;;
        *)
            export HAKO_DRONE_PROJECT_PATH="$(pwd)"
            ;;
    esac
fi
export DIRNAME=$(basename "${HAKO_DRONE_PROJECT_PATH}")
python3 -m hakoniwa_pdu.apps.launcher.hako_launcher --mode immediate $launcher_config_path
 
