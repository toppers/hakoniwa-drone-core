English | [日本語](single.md)

# Getting Started: Single Pattern (Without Hakoniwa)

When using the Hakoniwa Drone Simulator with the **"Without Hakoniwa" configuration (Single Pattern)**, you can **run the physical and control models standalone**.

In this configuration, it is possible to **integrate directly by calling the C library** from Unity, Unreal Engine, Python scripts, etc.

---

## ✅ Configuration Overview

*   **Without Hakoniwa (hakoniwa-core not required)**
*   Cross-platform support (macOS / Windows / Linux)
*   No integration with GUI or other assets

Use case examples:

*   Standalone integration test with PX4/Ardupilot
*   Operation check of drone control via CUI
*   Direct embedding from Python or Unreal

---

## 📦 Provided Binaries List

Please get the latest version from the Releases page:
👉 [🔗 Latest Binaries (Releases)](https://github.com/toppers/hakoniwa-drone-core/releases)

| Binary Name                              | Overview                                      |
| ---------------------------------- | --------------------------------------------- |
| `<os_name>-aircraft_service_px4`       | Communication/Integration with PX4            |
| `<os_name>-aircraft_service_ardupilot` | Communication/Integration with Ardupilot      |
| `<os_name>-drone_service_rc`           | CUI-operable radio control style control      |
| `hako_service_c`                   | Directly usable as a C library                |

> `<os_name>` is one of `mac`, `win`, `linux`.

Each binary is included in the directory extracted from the ZIP.

---

## 1. PX4 Integration: aircraft_service_px4

```bash
<os_name>-aircraft_service_px4 <IP_address> 4560 ./config/drone/px4
```

*   It is also possible to operate remotely by starting PX4 separately and integrating with QGC.
*   Reference
    *   [How to build PX4](/docs/tips/wsl/px4-setup.md)
    *   [How to start PX4](/docs/tips/wsl/docker-px4.md)

---

## 2. Ardupilot Integration: aircraft_service_ardupilot

```bash
<os_name>-aircraft_service_ardupilot <host_PC_IP_address> 9002 9003 ./config/drone/ardupilot
```

*   Performs control integration with Ardupilot via bidirectional UDP communication.
*   Can be operated in conjunction with Mission Planner.

Ardupilot startup example:

```bash
./Tools/autotest/sim_vehicle.py -v ArduCopter -f airsim-copter \
  -A "--sim-port-in 9003 --sim-port-out 9002" \
  --sim-address=<host_PC_IP> \
  --out=udp:<MissionPlanner_IP>:14550
```

*   Reference
    *   [How to build Ardupilot](/docs/tips/wsl/ardupilot-setup.md)
    *   [How to start Ardupilot](/docs/tips/wsl/docker-ardupilot.md)


---


## 3. CUI Operation: drone_service_rc

It is possible to operate via CUI by linking the physical and control models of the Hakoniwa Drone Simulator.

```bash
drone_service_rc 1 config/drone/rc
```

```
 ----- USAGE ----- 
 ----- STICK ----- 
|  LEFT  | RIGHT  |
|   w    |   i    |
| a   d  | j   l  |
|   s    |   k    |
 ---- BUTTON ---- 
 x : radio control button
 p : get position
 r : get attitude
 t : get simtime usec
 f : flip
 b : get battery status
```


Execution example: Log immediately after startup
```bash
BatteryModelCsvFilePath: ./tmp_battery_model.csv
BatteryModelCsvFilePath does not exist.
Angle rate control is disabled
Angle rate control is disabled
flip_target_time_sec: 0.4
flip_constant_time_sec: 0.1
target_angular_rate_rad_sec: 25.1327
target_angular_rate_delta: 0.167552
target_angular_inc_time_sec: 0.15
target_angular_dec_time_sec: 0.25
INFO: mixer is enabled
timestep_usec: 1000
DroneService::startService: 1000
> Start service
```

In this state, to arm, press `x` and then the Enter key.

> Note: The drone will not operate unless you arm it by pressing `x`. Please perform the operations described below after arming.

Then, press `w` and Enter to ascend.

Execution example: Arm and ascend
```bash
> Start service
x
w
position x=0.0 y=-0.0 z=0.1
position x=0.0 y=-0.0 z=0.2
position x=0.0 y=-0.0 z=0.3
position x=0.0 y=-0.0 z=0.4
position x=0.0 y=-0.0 z=0.5
position x=0.0 y=-0.0 z=0.6
position x=0.0 y=-0.0 z=0.7
position x=0.0 y=-0.0 z=0.8
position x=0.0 y=-0.0 z=0.9
position x=0.0 y=-0.0 z=1.0
position x=0.0 y=-0.0 z=1.1
```

Execution example: Move forward

```bash
i
position x=0.1 y=0.0 z=1.2
position x=0.2 y=0.0 z=1.3
position x=0.3 y=0.0 z=1.3
position x=0.4 y=0.0 z=1.3
position x=0.5 y=0.0 z=1.3
position x=0.6 y=0.0 z=1.3
```


---


## 4. C Library Integration: hako_service_c

If you want to embed it as a library:

*   `include/service/service.h`
*   `include/service/drone/drone_service_rc_api.h`

You can use them by including them.

Integration examples:

*   Unreal Engine (C++)
*   Unity (C# + P/Invoke)
*   Python (ctypes / pybind11)


## How to build the source of drone_service_rc

`drone_service_rc` is implemented in C++ and can be built with the following steps.

### Build steps on Ubuntu / macOS

```bash
cd src
mkdir cmake-build
cd cmake-build
cmake ..
make
```

### Build steps on Windows

```powershell
cd src
cmake -G "Visual Studio 17 2022" -A x64 -DHAKO_DRONE_OPTION_FILEPATH="cmake-options\win-cmake-options.cmake" .
cmake --build . --config Release
```


---


## 🚀 Reference Information

*   PX4 Integration Repository: [PX4/PX4-Autopilot](https://github.com/PX4/PX4-Autopilot)
*   Ardupilot Integration: [ArduPilot/ardupilot](https://github.com/ArduPilot/ardupilot)

```
