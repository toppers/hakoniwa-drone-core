# What is this?

This document provides instructions for building a multi-vehicle simulation environment using Ardupilot.

# Prerequisites

It is assumed that a single Ardupilot simulation environment has already been set up.

Please refer to [this document](/docs/getting_started/container.md) for instructions on setting up Ardupilot using the container pattern.

## Ardupilot (Multi-vehicle) Setup

### Preliminary Preparation (Directory Structure)

When coordinating multiple vehicles, prepare as many Ardupilot repositories as there are vehicles.

The following shows an example directory structure for two vehicles.

```tree
ardupilot-controllers/
├─ c1/
│  └─ ardupilot/        # ArduPilot repository (for vehicle 0)
│     └─ build/…        # Build artifacts for each
└─ c2/
　  └─ ardupilot/        # Ardupilot repository (for vehicle 1)
　     └─ build/…
```

*   `c1/ardupilot` and `c2/ardupilot` should be **separate clones** (or have separate build/working directories).
*   Perform a **build** in each. It is safer to use the same branch/tag for all.

Also, prepare the following **vehicle definition files** under `hakoniwa-drone-core/config`.
(`-2` indicates a definition file for two vehicles)

```tree
hakoniwa-drone-core/config
├── drone
│   ├── ardupilot-1 # Definition directory for 1 vehicle
│   │   └── drone_config_0.json
│   └── ardupilot-2 # Definition directory for 2 vehicles
│       ├── drone_config_0.json  # For the 1st vehicle
│       └── drone_config_1.json  # For the 2nd vehicle
└── pdudef
    ├── webavatar-2.json # Definition for 2 vehicles (1st: Drone, 2nd: Drone1)
    └── webavatar.json   # Definition for 1 vehicle
```

### Port Design (Default in this repository's scripts)

*   For vehicle `INSTANCE=i`: `MAVLINK_OUT_PORT = 14550 + 10 * i`
    *   Vehicle 0 → `14550`, Vehicle 1 → `14560`
*   Two destinations for transmission
    *   `udp:127.0.0.1:<PORT>` (for Python inside Docker)
    *   `udp:<HOST_IP>:<PORT>` (for Mission Planner)

> Specify the **IP of the host (Windows side)** for `HOST_IP`. Be careful when using WSL2.
> Allow UDP for the corresponding port in the OS firewall.

---

## Execution Procedure

### 1) Ardupilot (WSL2)

```bash
# Vehicle 0
bash -x hakoniwa-drone-core/tools/ardupilot/run.bash \
  ardupilot-controllers/c1/ardupilot/ <HOST_IP> 0

# Vehicle 1
bash -x hakoniwa-drone-core/tools/ardupilot/run.bash \
  ardupilot-controllers/c2/ardupilot/ <HOST_IP> 1
```

*   `HOST_IP` is the host IP (where Mission Planner is running).
*   Proceed to the next step after **GPS becomes effective** (wait until HOME is set, etc.).

### 2) Hakoniwa (Docker)

```bash
bash hakoniwa-drone-core/docker/tools/run-hako.bash ardupilot \
  hakoniwa-drone-core/config/pdudef/webavatar-2.json 2
```

### 3) Python Script (Inside Docker)

```bash
cd hakoniwa-drone-core/drone_api/pymavlink

python3 -m hakosim_mavlink --name Drone  \
  --connection udp:127.0.0.1:14550 --type ardupilot

python3 -m hakosim_mavlink --name Drone1 \
  --connection udp:127.0.0.1:14560 --type ardupilot
```

### 4) Operation Check

*   Connect to `UDP 14550` / `UDP 14560` from Mission Planner.
*   Confirm that two vehicles take off and perform a triangular movement (formation).

---

## Instance Correspondence Table (Example)

| Vehicle | MAVLink UDP (Inside Docker) | MAVLink UDP (MissionPlanner) | Drone Name (Python) | Configuration File |
| -- | --------------------- | ---------------------------- | --------------- | --------------------- |
| 0 | 127.0.0.1:14550       | HOST_IP:14550               | `Drone`         | `drone_config_0.json` |
| 1 | 127.0.0.1:14560       | HOST_IP:14560               | `Drone1`        | `drone_config_1.json` |

---
