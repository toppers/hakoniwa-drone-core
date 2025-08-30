# TIPS

## How to integrate Hakoniwa & Ardupilot in a WSL/docker environment

### Prerequisites

- You need to have docker installed in your WSL2/Ubuntu environment.
- For how to install docker, please refer to [here](docker-setup.md).
- You need to have Mission Planner installed.
- You need to have Unity installed.
- You need to open the `simulation` project of [hakoniwa-unity-drone](https://github.com/hakoniwalab/hakoniwa-unity-drone) and have the `Scenes/WebAvatar` scene open.
- You need to have Ardupilot built.
- For how to build Ardupilot, please refer to [here](ardupilot-setup.md).
- You need to check the IP address of the host PC. Please start power shell and execute the following command.

```powershell
ipconfig
```

### Execution Procedure

1.  Start Mission Planner.
2.  Start Unity.
3.  [Start Ardupilot.](#starting-ardupilot)
4.  [Start the Hakoniwa Drone Simulator.](#starting-the-hakoniwa-drone-simulator)
5.  Play the Unity scene.

#### Starting Ardupilot

Please execute the following.

```bash
English | [日本語](docker-ardupilot.md)

# TIPS

## How to integrate Hakoniwa & Ardupilot in a WSL/docker environment

### Prerequisites

- You need to have docker installed in your WSL2/Ubuntu environment.
- For how to install docker, please refer to [here](docker-setup.md).
- You need to have Mission Planner installed.
- You need to have Unity installed.
- You need to open the `simulation` project of [hakoniwa-unity-drone](https://github.com/hakoniwalab/hakoniwa-unity-drone) and have the `Scenes/WebAvatar` scene open.
- You need to have Ardupilot built.
- For how to build Ardupilot, please refer to [here](ardupilot-setup.md).
- You need to check the IP address of the host PC. Please start power shell and execute the following command.

```powershell
ipconfig
```

### Execution Procedure

1.  Start Mission Planner.
2.  Start Unity.
3.  [Start Ardupilot.](#starting-ardupilot)
4.  [Start the Hakoniwa Drone Simulator.](#starting-the-hakoniwa-drone-simulator)
5.  Play the Unity scene.

#### Starting Ardupilot

Please execute the following.

```bash
bash tools/ardupilot/run.bash <ardupilot-path> <HOST_IP>
```

For `<ardupilot-path>`, please specify the path to Ardupilot.  
For `<HOST_IP>`, please specify the IP address of the host PC.

Example:
```bash
tmori@WinHako:~/project/hakoniwa-drone-core$ bash tools/ardupilot/run.bash ../ardupilot  192.168.2.156
SIM_VEHICLE: Start
SIM_VEHICLE: Killing tasks
SIM_VEHICLE: Starting up at SITL location
SIM_VEHICLE: WAF build
SIM_VEHICLE: Configure waf
SIM_VEHICLE: "/home/tmori/project/ardupilot/modules/waf/waf-light" "configure" "--board" "sitl"
```

#### Starting the Hakoniwa Drone Simulator

Please execute the following.

```bash
bash hakoniwa-drone-core/docker/run.bash
```

```bash
bash hakoniwa-drone-core/docker/tools/run-hako.bash ardupilot
```

If successful, Mission Planner will respond.


```

For `<ardupilot-path>`, please specify the path to Ardupilot.  
For `<HOST_IP>`, please specify the IP address of the host PC.

Example:
```bash
tmori@WinHako:~/project/hakoniwa-drone-core$ bash tools/ardupilot/run.bash ../ardupilot  192.168.2.156
SIM_VEHICLE: Start
SIM_VEHICLE: Killing tasks
SIM_VEHICLE: Starting up at SITL location
SIM_VEHICLE: WAF build
SIM_VEHICLE: Configure waf
SIM_VEHICLE: "/home/tmori/project/ardupilot/modules/waf/waf-light" "configure" "--board" "sitl"
```

#### Starting the Hakoniwa Drone Simulator

Please execute the following.

```bash
bash hakoniwa-drone-core/docker/run.bash
```

```bash
bash hakoniwa-drone-core/docker/tools/run-hako.bash ardupilot
```

If successful, Mission Planner will respond.

