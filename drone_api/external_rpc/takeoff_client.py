#!/usr/bin/env python3
from __future__ import annotations

import sys
import time
from pathlib import Path

from hakosim_rpc import (
    DEFAULT_SERVICE_CONFIG_PATH,
    HakoniwaRpcDroneClient,
    print_response_elapsed,
)


DEFAULT_DRONE_NAME = "Drone"
DEFAULT_ALT_M = 0.5


def main() -> int:
    service_config_path = (
        Path(sys.argv[1]).resolve()
        if len(sys.argv) >= 2
        else DEFAULT_SERVICE_CONFIG_PATH
    )
    drone_name = sys.argv[2] if len(sys.argv) >= 3 else DEFAULT_DRONE_NAME
    alt_m = float(sys.argv[3]) if len(sys.argv) >= 4 else DEFAULT_ALT_M
    client = HakoniwaRpcDroneClient(
        drone_name=drone_name,
        service_config_path=service_config_path,
    )

    print(f"INFO: request takeoff drone={drone_name} alt_m={alt_m}")
    start_time = time.time()
    res = client.takeoff(alt_m)
    print_response_elapsed("takeoff call", start_time)
    print(f"INFO: response ok={res.ok} message={res.message}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
