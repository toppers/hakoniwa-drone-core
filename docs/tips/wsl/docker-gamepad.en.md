English | [日本語](docker-gamepad.md)

# TIPS

## How to operate Hakoniwa with a gamepad in a WSL/docker environment

### Prerequisites

- You need to have docker installed in your WSL2/Ubuntu environment.
- For how to install docker, please refer to [here](docker-setup.md).
- You need to have Unity installed.
- You need to have a PS4/PS5 controller connected via USB.
- You need to open the `simulation` project of [hakoniwa-unity-drone](https://github.com/hakoniwalab/hakoniwa-unity-drone) and have the `Scenes/WebAvatar` scene open.


### Execution Procedure

1.  Start Unity.
2.  [Start the Hakoniwa Drone Simulator.](#starting-the-hakoniwa-drone-simulator)
3.  Play the WebAvatar scene in Unity.
4.  [Operate with the gamepad.](#gamepad-operation)



#### Starting the Hakoniwa Drone Simulator

Please execute the following.

```bash
bash hakoniwa-drone-core/docker/run.bash
```

```bash
bash hakoniwa-drone-core/docker/tools/run-hako.bash rc
```


#### Gamepad Operation

If you have a PS4/PS5 controller connected via USB, you can operate the drone with the following controls.

- X button: ARM/DISARM
- Circle button: Attach/Detach baggage
- Square button: Take a picture with the camera

- Up button: Camera up
- Down button: Camera down


- Left stick (up/down): Ascend/Descend
- Left stick (left/right): Turn left/right
- Right stick (up/down): Move forward/backward
- Right stick (left/right): Move left/right

Supplement:

The PS4/PS5 controller is handled by Unity, and the events are sent to the docker side via WebSocket.