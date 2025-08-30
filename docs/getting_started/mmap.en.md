English | [日本語](mmap.md)

# Use Case with Hakoniwa

When using with Hakoniwa, in addition to the features available without Hakoniwa, the following becomes possible:

1.  **Unity Integration**: Use [hakoniwa-unity-drone](https://github.com/hakoniwalab/hakoniwa-unity-drone)
2.  **Digital Twin Integration**: Use [Zenoh/ROS2 Hakoniwa Bridge](https://github.com/toppers/hakoniwa-bridge)
3.  **Mission Planner Integration**: Use [MAVLink Hakoniwa Bridge](mavlink/bridge/README.md)
4.  **Hakoniwa Drone AR Shared Simulation**: Use [Hakoniwa Web Server](https://github.com/toppers/hakoniwa-webserver) and [Hakoniwa AR Bridge](https://github.com/toppers/hakoniwa-ar-bridge)

The provided binaries for the version with Hakoniwa are as follows:

1.  Sample app for PX4 integration (`<os_name>-main_hako_aircraft_service_px4`)
2.  Sample app for Ardupilot integration (`<os_name>-main_hako_aircraft_service_ardupilot`)
3.  Sample app for Hakoniwa Drone (`<os_name>-main_hako_drone_servce`)

All are cross-platform compatible. Please download the binaries from the release page.

`os_name` is as follows:

-   mac
-   win
-   linux

### Installation of Hakoniwa Core Functions

When using the version with Hakoniwa, please install [hakoniwa-core-cpp-client](https://github.com/toppers/hakoniwa-core-cpp-client) in advance.

For Windows, please execute the following command in WSL2.

```bash
dd if=/dev/zero of=/mnt/z/mmap/mmap-0x100.bin bs=1M count=5
```

Reason: The size of the mmap file on ramdisk is insufficient. (5MB or more is required)

### Preparation of Unity Editor

When using the version with Hakoniwa, it is necessary to open the `simulation` project of [hakoniwa-unity-drone](https://github.com/hakoniwalab/hakoniwa-unity-drone) in the Unity Editor in advance.

After starting the Unity Editor, please open the Avatar scene.

![image](/docs/images/unity-editor.png)

In this scene, the position and orientation information of the Hakoniwa drone and the PWM duty values of the rotors are received to visualize the drone's movement.

By integrating with the sample app for the version with Hakoniwa, you can check the movement of the Hakoniwa drone on the Unity Editor.

Also, to start the simulation, please press the START button shown in the figure below.

![image](/docs/images/unity-sim.png)

### How to Use the PX4 Integration Sample App

You can integrate the physical model of the Hakoniwa Drone Simulator with PX4 using the PX4 integration sample app.

Execution method:

```bash
<os_name>-main_hako_aircraft_service_px4 <IP_address> 4560 ./config/drone/px4 <path/to/hakoniwa-unity-drone>/simulation/avatar-drone.json
```

*   Supplement:
    *   For Windows, for the IP address, please specify the IP address of WSL when `ipconfig` is executed in Power Shell.
    *   Ethernet adapter vEthernet (WSL (Hyper-V firewall)):


At this time, by starting PX4, it is possible to integrate with PX4.

Reference: https://github.com/toppers/hakoniwa-px4sim?tab=readme-ov-file#terminal-a

In addition, by integrating with QGC, remote operation is possible.


Simulation execution procedure:

1.  Open the Avatar scene in the Unity Editor.
2.  Start the PX4 integration sample app.
3.  Start PX4.
4.  Press the START button in the Unity Editor.
5.  Start QGC, connect to PX4, and perform remote operation.


### How to Use the Ardupilot Integration Sample App

You can integrate the physical model of the Hakoniwa Drone Simulator with Ardupilot using the Ardupilot integration sample app.

Execution method:

```bash
<os_name>-main_hako_aircraft_service_ardupilot <host_PC_IP_address> 9002 9003 ./config/drone/ardupilot <path/to/hakoniwa-unity-drone>/simulation/avatar-drone.json
```

At this time, by starting Ardupilot, it is possible to integrate with Ardupilot.

```bash
./Tools/autotest/sim_vehicle.py -v ArduCopter -f airsim-copter -A "--sim-port-in 9003 --sim-port-out 9002"  --sim-address=<host_PC_IP_address>  --out=udp:<Mission_Planner_IP_address>:14550
```

Reference: https://github.com/ArduPilot/ardupilot

At this time, by integrating with Mission Planner, remote operation is possible.

Simulation execution procedure:

1.  Open the Avatar scene in the Unity Editor.
2.  Start the Ardupilot integration sample app.
3.  Start Ardupilot.
4.  Press the START button in the Unity Editor.
5.  Start Mission Planner, connect to Ardupilot, and perform remote operation.


### How to Use the Hakoniwa Drone Sample App

You can operate via CUI by linking the physical and control models of the Hakoniwa Drone Simulator using the Hakoniwa Drone sample app.

There are the following two types of Hakoniwa Drone sample apps.

1.  Sample app for radio control operation
2.  Sample app for flight plan operation

#### Sample app for radio control operation

You can operate the Hakoniwa drone with your game controller.

Execution method:

```bash
<os_name>-main_hako_drone_servce  ./config/drone/rc <path/to/hakoniwa-unity-drone>/simulation/avatar-drone.json
```

At this time, you can operate the Hakoniwa drone by using the Python script for radio control operation.

For how to operate the radio control, please refer to [here](/drone_api/README-ja.md).



Simulation execution procedure:

1.  Open the Avatar scene in the Unity Editor.
2.  Start the Hakoniwa Drone sample app.
3.  Press the START button in the Unity Editor.
4.  Start the Python script for radio control operation.
5.  Operate the Hakoniwa drone with the game controller.


#### Sample app for flight plan operation

It is possible to execute a flight plan using the [Python API](/drone_api/libs/README.md) of the Hakoniwa Drone.


Execution method:

```bash
<os_name>-main_hako_drone_servce  ./config/drone/api <path/to/hakoniwa-unity-drone>/simulation/avatar-drone.json
```

At this time, you can operate the Hakoniwa drone by using the Python script for flight plan operation.

For how to execute the Python script, please refer to [here](/drone_api/README-ja.md).

Simulation execution procedure:

1.  Open the Avatar scene in the Unity Editor.
2.  Start the Hakoniwa Drone sample app.
3.  Press the START button in the Unity Editor.
4.  Start the Python script for flight plan operation.
