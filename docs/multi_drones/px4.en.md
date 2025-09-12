# What is this?

This document provides instructions for building a multi-vehicle simulation environment using PX4.

# Prerequisites

It is assumed that a single PX4 simulation environment has already been set up.

Please refer to [this document](/docs/getting_started/container.md) for instructions on setting up PX4 using the container pattern.

## PX4 (Multi-vehicle) Setup

### Preliminary Preparation (Directory Structure)

When coordinating multiple vehicles, prepare as many PX4 repositories as there are vehicles.

The following shows an example directory structure for two vehicles.

```tree
px4-controllers/
├─ c1/
│  └─ PX4-Autopilot/     # PX4 repository (for vehicle 0)
│     └─ build/…         # Build artifacts for each
└─ c2/
　  └─ PX4-Autopilot/     # PX4 repository (for vehicle 1)
　     └─ build/…
```

*   `c1/PX4-Autopilot` and `c2/PX4-Autopilot` should be **separate clones** (or have separate build/working directories).
*   Perform a **build** in each. It is safer to use the same branch/tag for all.

Also, prepare the following **vehicle definition files** under `hakoniwa-drone-core/config`.
(`-2` indicates a definition file for two vehicles)

```tree
hakoniwa-drone-core/config
├── drone
│   ├── px4-1   # Definition directory for 1 vehicle
│   │   └── drone_config_0.json
│   └── px4-2   # Definition directory for 2 vehicles
│       ├── drone_config_0.json  # For the 1st vehicle
│       └── drone_config_1.json  # For the 2nd vehicle
└── pdudef
    ├── webavatar-2.json # Definition for 2 vehicles (1st: Drone, 2nd: Drone1)
    └── webavatar.json   # Definition for 1 vehicle
```

### Port Design (Default in this repository's scripts)

*   For vehicle `INSTANCE=i`:
    *   Vehicle 0 → `14540`
    *   Vehicle 1 → `14541`
*   Two destinations for transmission
    *   `udp:127.0.0.1:<PORT>` (for Python inside Docker)
    *   `udp:<HOST_IP>:<PORT>` (for QGroundControl)

> Specify the **IP of the host (Windows side)** for `HOST_IP`. Be careful when using WSL2.
> Allow UDP for the corresponding port in the OS firewall.

---

## Execution Procedure

### 1) PX4 (WSL2)

```bash
# Vehicle 0
bash -x hakoniwa-drone-core/tools/px4/run.bash \
  px4-controllers/c1/PX4-Autopilot 0

# Vehicle 1
bash -x hakoniwa-drone-core/tools/px4/run.bash \
  px4-controllers/c2/PX4-Autopilot 1
```

*   Proceed to the next step after **GPS becomes effective** (wait until HOME is set, etc.).

### 2) Hakoniwa (Docker)

```bash
bash hakoniwa-drone-core/docker/tools/run-hako.bash px4 \
  hakoniwa-drone-core/config/pdudef/webavatar-2.json 2
```

### 3) Python Script (Inside Docker)

```bash
cd hakoniwa-drone-core/drone_api/pymavlink

python3 -m hakosim_mavlink --name Drone  \
  --connection udp:127.0.0.1:14540 --type px4

python3 -m hakosim_mavlink --name Drone1 \
  --connection udp:127.0.0.1:14541 --type px4
```

### 4) Operation Check

*   Connect to `UDP 14540` / `UDP 14541` from QGroundControl.
*   Confirm that two vehicles take off and perform a triangular movement (formation).

---

## Instance Correspondence Table (Example)

| Vehicle | Sim (Inside Docker, TCP) | QGC (WSL2 IP, UDP) | Drone Name (Python) | Configuration File |
| -- | -- | -- | -- | -- |
| 0  | tcp:127.0.0.1:4560    | WSL2_IP:14540     | `Drone`         | `drone_config_0.json` |
| 1  | tcp:127.0.0.1:4561    | WSL2_IP:14541     | `Drone1`        | `drone_config_1.json` |
```