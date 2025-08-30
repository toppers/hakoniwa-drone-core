English | [日本語](docker-python-api.md)

# TIPS

## How to integrate Hakoniwa & Python API in a WSL/docker environment

### Prerequisites

- You need to have docker installed in your WSL2/Ubuntu environment.
- For how to install docker, please refer to [here](docker-setup.md).
- You need to have Unity installed.
- You need to open the `simulation` project of [hakoniwa-unity-drone](https://github.com/hakoniwalab/hakoniwa-unity-drone) and have the `Scenes/WebAvatar` scene open.


### Execution Procedure

1.  Start Unity.
2.  [Start the Hakoniwa Drone Simulator.](#starting-the-hakoniwa-drone-simulator)
3.  Play the WebAvatar scene in Unity.
4.  [Run the Python API sample.](#python-api)




#### Starting the Hakoniwa Drone Simulator

Please execute the following.

```bash
bash hakoniwa-drone-core/docker/run.bash
```

```bash
bash hakoniwa-drone-core/docker/tools/run-hako.bash api
```


#### Python API
Please execute the following.

```bash
bash hakoniwa-drone-core/docker/attach.bash
```

```bash
cd hakoniwa-drone-core/drone_api
```

```bash
python3 rc/api_control_sample.py ../config/pdudef/webavatar.json
```

## Supplement:

For the Python API specification, please refer to the following.

- https://github.com/toppers/hakoniwa-drone-core/tree/main/drone_api/libs

For this sample code, please refer to the following.

- https://github.com/toppers/hakoniwa-drone-core/blob/main/drone_api/rc/api_control_sample.py