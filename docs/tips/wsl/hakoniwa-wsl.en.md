English | [日本語](hakoniwa-wsl.md)

# TIPS
## About integrating with Hakoniwa-enabled PX4/Ardupilot on Windows

When integrating with PX4/Ardupilot on Windows, high-frequency communication occurs between WSL and native applications (communication every 3ms).

![image](/docs/images/win-px4-arch.png)

Therefore, the simulation speed may become very slow (about 3-4 times slower in experience).

As a way to improve the simulation speed, you can improve it by changing the simulation configuration as follows.

![image](/docs/images/wsl-px4-arch.png)


Simulation execution procedure:

1.  [Open the WebAvatar scene in the Unity Editor.](#open-the-webavatar-scene-in-the-unity-editor)
2.  [Initial setup in WSL.](#initial-setup-in-wsl)
3.  [Start PX4 in WSL.](#start-px4-in-wsl)
4.  [Start the PX4 integration sample app in WSL.](#start-the-px4-integration-sample-app-in-wsl)
5.  [Start the Hakoniwa Web server in WSL.](#start-the-hakoniwa-web-server-in-wsl)
6.  [Start the Hakoniwa simulation in WSL.](#start-the-hakoniwa-simulation-in-wsl)
7.  Click the Play button of the WebAvatar scene in the Unity Editor.
8.  Start QGC, connect to PX4, and perform remote operation.

### Open the WebAvatar scene in the Unity Editor.

Click `HakoniwaWeb` in the hierarchy view and set the IP address of `Server Uri` in the inspector view to the IP address of WSL.

![image](https://github.com/user-attachments/assets/b7c14be1-0342-40e5-be07-77a0574adea2)


### Initial setup in WSL

#### Add the path of the Hakoniwa command.

You need to add the path of the Hakoniwa command to the environment variable `PATH`.

Configuration example:
```bash
export PATH=$PATH:/usr/local/bin/hakoniwa
```

If necessary, please add it to `~/.bashrc` or `~/.zshrc`.

```bash
echo 'export PATH=$PATH:/usr/local/bin/hakoniwa' >> ~/.bashrc
source ~/.bashrc
```

#### Move to the file system of WSL and create an empty project directory

Here, the project name is `project`, but any alphabetic characters are acceptable.

```bash
cd ~
mkdir project
cd project
```

In addition, please clone all the repositories described later directly under `project`.

#### Clone hakoniwa-drone-core

Please clone hakoniwa-drone-core in advance.

```bash
git clone --recursive https://github.com/toppers/hakoniwa-drone-core.git
```

Also, please download lnx.zip from the latest release and extract it directly under hakoniwa-drone-core.

#### Clone hakoniwa-unity-drone

Please clone hakoniwa-unity-drone in advance.

```bash
git clone --recursive https://github.com/hakoniwalab/hakoniwa-unity-drone.git
```

### Start PX4 in WSL.

```bash
cd hakoniwa-px4sim/px4/PX4-Autopilot
```

```bash
bash ../sim/simstart.bash
```

If successful, it will look like this.

```
tmori@WinHako:~/project/hakoniwa-px4sim/px4/PX4-Autopilot$ bash ../sim/simstart.bash
Linux WinHako 5.15.167.4-microsoft-standard-WSL2 #1 SMP Tue Nov 5 00:21:55 UTC 2024 x86_64 x86_64 x86_64 GNU/Linux
INFO: SINGLE INSTANCE MODE
[0/1] launching px4 none_iris (SYS_AUTOSTART=10016)

______  __   __    ___
| ___ \ \ \ / /   /   |
| |_/ /  \ V /   / /| |
|  __/   /   \  / /_| |
| |     / /^\ \ \___  |
\_|     \/   \/     |_/

px4 starting.

INFO  [px4] startup script: /bin/sh etc/init.d-posix/rcS 0
env SYS_AUTOSTART: 10016
INFO  [param] selected parameter default file parameters.bson
INFO  [param] importing from 'parameters.bson'
INFO  [parameters] BSON document size 411 bytes, decoded 411 bytes (INT32:13, FLOAT:7)
INFO  [param] selected parameter backup file parameters_backup.bson
INFO  [dataman] data manager file './dataman' size is 7868392 bytes
INFO  [init] PX4_SIM_HOSTNAME: 127.0.0.1
INFO  [simulator_mavlink] using TCP on remote host 127.0.0.1 port 4560
WARN  [simulator_mavlink] Please ensure port 4560 is not blocked by a firewall.
INFO  [simulator_mavlink] Resolved host '127.0.0.1' to address: 127.0.0.1
INFO  [simulator_mavlink] Waiting for simulator to accept connection on TCP port 4560
```

### Start the PX4 integration sample app in WSL.

```bash
lnx/linux-main_hako_aircraft_service_px4 127.0.0.1 4560 ./config/drone/px4 <path/to/hakoniwa-unity-drone>/simulation/avatar-drone.json
```

If successful, it will look like this.

```
tmori@WinHako:~/project/hakoniwa-drone-core$ ./lnx/linux-main_hako_aircraft_service_px4 127.0.01 4560 config/drone/px4 ../hakoniwa-unity-drone/simulation/webavatar.json
BatteryModelCsvFilePath: ./tmp_battery_model.csv
BatteryModelCsvFilePath does not exist.
INFO: aircraft_index=0
MavLinkService initialized
asset_name: drone
conductor start
conductor start done
simulator register
asset_name = drone
config_path = ../hakoniwa-unity-drone/simulation/webavatar.json
INFO: hako_conductor thread start
Robot: Drone, PduWriter: Drone_motor
channel_id: 0 pdu_size: 112
INFO: Drone create_lchannel: logical_id=0 real_id=0 size=112
Robot: Drone, PduWriter: Drone_pos
channel_id: 1 pdu_size: 72
INFO: Drone create_lchannel: logical_id=1 real_id=1 size=72
Robot: Drone, PduWriter: Drone_disturb
channel_id: 3 pdu_size: 56
INFO: Drone create_lchannel: logical_id=3 real_id=2 size=56
Robot: Drone, PduWriter: Drone_battery
channel_id: 4 pdu_size: 56
INFO: Drone create_lchannel: logical_id=4 real_id=3 size=56
Robot: Drone, PduWriter: Drone_velocity
channel_id: 5 pdu_size: 72
INFO: Drone create_lchannel: logical_id=5 real_id=4 size=72
Robot: Drone, PduWriter: Drone_drone_cmd_takeoff
channel_id: 6 pdu_size: 88
INFO: Drone create_lchannel: logical_id=6 real_id=5 size=88
Robot: Drone, PduWriter: Drone_drone_cmd_move
channel_id: 7 pdu_size: 104
INFO: Drone create_lchannel: logical_id=7 real_id=6 size=104
Robot: Drone, PduWriter: Drone_drone_cmd_land
channel_id: 8 pdu_size: 88
INFO: Drone create_lchannel: logical_id=8 real_id=7 size=88
Robot: Drone, PduWriter: Drone_hako_cmd_game
channel_id: 9 pdu_size: 160
INFO: Drone create_lchannel: logical_id=9 real_id=8 size=160
Robot: Drone, PduWriter: Drone_hako_cmd_camera
channel_id: 10 pdu_size: 44
INFO: Drone create_lchannel: logical_id=10 real_id=9 size=44
Robot: Drone, PduWriter: Drone_hako_cmd_camera_move
channel_id: 11 pdu_size: 64
INFO: Drone create_lchannel: logical_id=11 real_id=10 size=64
Robot: Drone, PduWriter: Drone_hako_cmd_magnet_holder
channel_id: 14 pdu_size: 40
INFO: Drone create_lchannel: logical_id=14 real_id=11 size=40
Robot: Drone, PduWriter: Drone_impulse
channel_id: 2 pdu_size: 216
INFO: Drone create_lchannel: logical_id=2 real_id=12 size=216
Robot: Drone, PduWriter: Drone_hako_camera_data
channel_id: 12 pdu_size: 1002992
INFO: Drone create_lchannel: logical_id=12 real_id=13 size=1002992
Robot: Drone, PduWriter: Drone_hako_cmd_camera_info
channel_id: 13 pdu_size: 56
INFO: Drone create_lchannel: logical_id=13 real_id=14 size=56
Robot: Drone, PduWriter: Drone_hako_status_magnet_holder
channel_id: 15 pdu_size: 32
INFO: Drone create_lchannel: logical_id=15 real_id=15 size=32
Robot: Drone, PduWriter: Drone_lidar_points
channel_id: 16 pdu_size: 177424
INFO: Drone create_lchannel: logical_id=16 real_id=16 size=177424
Robot: Drone, PduWriter: Drone_lidar_pos
channel_id: 17 pdu_size: 72
INFO: Drone create_lchannel: logical_id=17 real_id=17 size=72
INFO: asset(drone) is registered.
HakoniwaPduAccessor::init()
HakoniwaPduAccessor::create_map()
reader: robot_name = Drone, channel_id = 2, pdu_size = 216
reader: robot_name = Drone, channel_id = 12, pdu_size = 1002992
reader: robot_name = Drone, channel_id = 13, pdu_size = 56
reader: robot_name = Drone, channel_id = 15, pdu_size = 32
reader: robot_name = Drone, channel_id = 16, pdu_size = 177424
reader: robot_name = Drone, channel_id = 17, pdu_size = 72
reader: robot_name = Drone, channel_id = 0, pdu_size = 112
reader: robot_name = Drone, channel_id = 1, pdu_size = 72
reader: robot_name = Drone, channel_id = 3, pdu_size = 56
reader: robot_name = Drone, channel_id = 4, pdu_size = 56
reader: robot_name = Drone, channel_id = 5, pdu_size = 72
reader: robot_name = Drone, channel_id = 6, pdu_size = 88
reader: robot_name = Drone, channel_id = 7, pdu_size = 104
reader: robot_name = Drone, channel_id = 8, pdu_size = 88
reader: robot_name = Drone, channel_id = 9, pdu_size = 160
reader: robot_name = Drone, channel_id = 10, pdu_size = 44
reader: robot_name = Drone, channel_id = 11, pdu_size = 64
reader: robot_name = Drone, channel_id = 14, pdu_size = 40
writer: robot_name = Drone, channel_id = 0, pdu_size = 112
writer: robot_name = Drone, channel_id = 1, pdu_size = 72
writer: robot_name = Drone, channel_id = 3, pdu_size = 56
writer: robot_name = Drone, channel_id = 4, pdu_size = 56
writer: robot_name = Drone, channel_id = 5, pdu_size = 72
writer: robot_name = Drone, channel_id = 6, pdu_size = 88
writer: robot_name = Drone, channel_id = 7, pdu_size = 104
writer: robot_name = Drone, channel_id = 8, pdu_size = 88
writer: robot_name = Drone, channel_id = 9, pdu_size = 160
writer: robot_name = Drone, channel_id = 10, pdu_size = 44
writer: robot_name = Drone, channel_id = 11, pdu_size = 64
writer: robot_name = Drone, channel_id = 14, pdu_size = 40
writer: robot_name = Drone, channel_id = 2, pdu_size = 216
writer: robot_name = Drone, channel_id = 12, pdu_size = 1002992
writer: robot_name = Drone, channel_id = 13, pdu_size = 56
writer: robot_name = Drone, channel_id = 15, pdu_size = 32
writer: robot_name = Drone, channel_id = 16, pdu_size = 177424
writer: robot_name = Drone, channel_id = 17, pdu_size = 72
simulator register done
HakoniwaDroneService::registerService() done
INFO: lockStep=1
INFO: deltaTimeUsec=3000
INFO: AircraftService startService wait for connection : 0
INFO: AircraftService startService is returned : 0
INFO: COMMAND_LONG ack sended: ret = 1
INFO: AircraftService started
WAIT START
```

### Start the Hakoniwa simulation in WSL.

```bash
hako-cmd start
```

If successful, the PX4 log will look like this.

```
:
INFO  [simulator_mavlink] Waiting for simulator to accept connection on TCP port 4560
INFO  [simulator_mavlink] Simulator connected on TCP port 4560.
ERROR [simulator_mavlink] poll timeout 0, 111
ERROR [simulator_mavlink] poll timeout 0, 111
INFO  [lockstep_scheduler] setting initial absolute time to 1747721032882577 us
WARN  [vehicle_angular_velocity] no gyro selected, using sensor_gyro_fifo:0 1310988
INFO  [commander] LED: open /dev/led0 failed (22)
WARN  [health_and_arming_checks] Preflight Fail: ekf2 missing data
INFO  [mavlink] mode: Normal, data rate: 4000000 B/s on udp port 18570 remote port 14550
INFO  [mavlink] mode: Onboard, data rate: 4000000 B/s on udp port 14580 remote port 14540
INFO  [mavlink] mode: Onboard, data rate: 4000 B/s on udp port 14280 remote port 14030
INFO  [mavlink] mode: Gimbal, data rate: 400000 B/s on udp port 13030 remote port 13280
INFO  [logger] logger started (mode=all)
INFO  [logger] Start file log (type: full)
INFO  [logger] [logger] ./log/2025-05-20/06_03_53.ulg
INFO  [logger] Opened full log file: ./log/2025-05-20/06_03_53.ulg
* MPC_XY_CRUISE: curr: 20.0000 -> new: 3.5000
INFO  [mavlink] MAVLink only on localhost (set param MAV_{i}_BROADCAST = 1 to enable network)
INFO  [mavlink] MAVLink only on localhost (set param MAV_{i}_BROADCAST = 1 to enable network)
INFO  [px4] Startup script returned successfully
pxh> INFO  [tone_alarm] home set
INFO  [mavlink] partner IP: 172.31.0.1
INFO  [commander] Ready for takeoff!
```

### Start the Hakoniwa Web server in WSL.

```bash
cd hakoniwa-unity-drone/hakoniwa-webserver
```

```bash
python -m server.main --asset_name WebServer --config_path ../simulation/webavatar.json --delta_time_usec 20000
```

If successful, it will look like this.

```
(venv) tmori@WinHako:~/project/hakoniwa-unity-drone/hakoniwa-webserver$ python -m server.main --asset_name WebServer --config_path ../simulation/webavatar.json --delta_time_usec 20000
INFO: start http server
INFO: start websocket server
run webserver
set event loop on asyncio
Starting WebSocket server...
INFO: Success for external initialization.
append_list(pub_pdus) : Drone 2 impulse
pdu create: Drone 2 216
WebSocket server started on ws://0.0.0.0:8765
append_list(pub_pdus) : Drone 12 hako_camera_data
pdu create: Drone 12 1002992
append_list(pub_pdus) : Drone 13 hako_cmd_camera_info
pdu create: Drone 13 56
append_list(pub_pdus) : Drone 15 hako_status_magnet_holder
Starting HTTP server on port 8000...
pdu create: Drone 15 32
append_list(pub_pdus) : Drone 16 lidar_points
pdu create: Drone 16 177424
append_list(pub_pdus) : Drone 17 lidar_pos
pdu create: Drone 17 72
append_list(pub_pdus) : Drone 0 motor
======== Running on http://localhost:8080 ========
(Press CTRL+C to quit)
pdu create: Drone 0 112
append_list(pub_pdus) : Drone 1 pos
pdu create: Drone 1 72
append_list(pub_pdus) : Drone 3 disturb
pdu create: Drone 3 56
append_list(pub_pdus) : Drone 4 battery
pdu create: Drone 4 56
append_list(pub_pdus) : Drone 5 velocity
pdu create: Drone 5 72
append_list(pub_pdus) : Drone 6 drone_cmd_takeoff
pdu create: Drone 6 88
append_list(pub_pdus) : Drone 7 drone_cmd_move
pdu create: Drone 7 104
append_list(pub_pdus) : Drone 8 drone_cmd_land
pdu create: Drone 8 88
append_list(pub_pdus) : Drone 9 hako_cmd_game
pdu create: Drone 9 160
append_list(pub_pdus) : Drone 10 hako_cmd_camera
pdu create: Drone 10 44
append_list(pub_pdus) : Drone 11 hako_cmd_camera_move
pdu create: Drone 11 64
append_list(pub_pdus) : Drone 14 hako_cmd_magnet_holder
pdu create: Drone 14 40
append_list(sub_pdus) : Drone 0 motor
pdu create: Drone 0 112
append_list(sub_pdus) : Drone 1 pos
pdu create: Drone 1 72
append_list(sub_pdus) : Drone 3 disturb
pdu create: Drone 3 56
append_list(sub_pdus) : Drone 4 battery
pdu create: Drone 4 56
append_list(sub_pdus) : Drone 5 velocity
pdu create: Drone 5 72
append_list(sub_pdus) : Drone 6 drone_cmd_takeoff
pdu create: Drone 6 88
append_list(sub_pdus) : Drone 7 drone_cmd_move
pdu create: Drone 7 104
append_list(sub_pdus) : Drone 8 drone_cmd_land
pdu create: Drone 8 88
append_list(sub_pdus) : Drone 9 hako_cmd_game
pdu create: Drone 9 160
append_list(sub_pdus) : Drone 10 hako_cmd_camera
pdu create: Drone 10 44
append_list(sub_pdus) : Drone 11 hako_cmd_camera_move
pdu create: Drone 11 64
append_list(sub_pdus) : Drone 14 hako_cmd_magnet_holder
pdu create: Drone 14 40
append_list(sub_pdus) : Drone 2 impulse
pdu create: Drone 2 216
append_list(sub_pdus) : Drone 12 hako_camera_data
pdu create: Drone 12 1002992
append_list(sub_pdus) : Drone 13 hako_cmd_camera_info
pdu create: Drone 13 56
append_list(sub_pdus) : Drone 15 hako_status_magnet_holder
pdu create: Drone 15 32
append_list(sub_pdus) : Drone 16 lidar_points
pdu create: Drone 16 177424
append_list(sub_pdus) : Drone 17 lidar_pos
pdu create: Drone 17 72
LOADED: PDU DATA
WARNING: on_simulation_step_async() took longer than delta_time_usec: 21.79 ms
```