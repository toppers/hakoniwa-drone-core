English | [日本語](docker-px4.md)

# TIPS

## How to integrate Hakoniwa & PX4 in a WSL/docker environment

### Prerequisites

- You need to have docker installed in your WSL2/Ubuntu environment.
- For how to install docker, please refer to [here](docker-setup.md).
- You need to have QGC installed.
- You need to have Unity installed.
- You need to open the `simulation` project of [hakoniwa-unity-drone](https://github.com/hakoniwalab/hakoniwa-unity-drone) and have the `Scenes/WebAvatar` scene open.
- You need to have PX4 built.
- For how to build PX4, please refer to [here](px4-setup.md).


### Execution Procedure

1.  Start QGC.
2.  Start Unity.
3.  [Start PX4.](#starting-px4)
4.  [Start the Hakoniwa Drone Simulator.](#starting-the-hakoniwa-drone-simulator)
5.  Play the Unity scene.

#### Starting PX4

Please execute the following.

```bash
bash hakoniwa-drone-core/tools/px4/run.bash
```

Example:
```bash
tmori@WinHako:~/qiita$ bash hakoniwa-drone-core/tools/px4/run.bash
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
INFO  [parameters] BSON document size 350 bytes, decoded 350 bytes (INT32:15, FLOAT:3)
INFO  [param] selected parameter backup file parameters_backup.bson
INFO  [dataman] data manager file './dataman' size is 1208528 bytes
INFO  [init] PX4_SIM_HOSTNAME: 127.0.0.1
INFO  [simulator_mavlink] using TCP on remote host 127.0.0.1 port 4560
WARN  [simulator_mavlink] Please ensure port 4560 is not blocked by a firewall.
INFO  [simulator_mavlink] Resolved host '127.0.0.1' to address: 127.0.0.1
INFO  [simulator_mavlink] Waiting for simulator to accept connection on TCP port 4560
```

#### Starting the Hakoniwa Drone Simulator

Please execute the following.

```bash
bash hakoniwa-drone-core/docker/run.bash
```

```bash
bash hakoniwa-drone-core/docker/tools/run-hako.bash px4
```

If successful, QGC will respond.