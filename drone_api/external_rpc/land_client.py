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


def main() -> int:
    service_config_path = (
        Path(sys.argv[1]).resolve()
        if len(sys.argv) >= 2
        else DEFAULT_SERVICE_CONFIG_PATH
    )
    drone_name = sys.argv[2] if len(sys.argv) >= 3 else DEFAULT_DRONE_NAME
    client = HakoniwaRpcDroneClient(
        drone_name=drone_name,
        service_config_path=service_config_path,
    )

    print(f"INFO: request land drone={drone_name}")
    start_time = time.time()
    res = client.land()
    print_response_elapsed("land call", start_time)
    print(f"INFO: response ok={res.ok} message={res.message}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
