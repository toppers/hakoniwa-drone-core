English | [日本語](container.md)

# Getting Started: Container Pattern (With Hakoniwa)

When using the Hakoniwa Drone Simulator with the **Container Pattern (with Hakoniwa)**, you can use Docker containers to **run the physical and control models separately**.
In this configuration, it is possible to **integrate with Unity, Unreal Engine, ROS2, the Web, etc., via a Bridge**.


📘 [See the overview and configuration image of the entire container pattern](/docs/architecture/overview.md) 

---

## ✅ Features

*   Each component (PX4/Ardupilot, hakoniwa-drone-core, hakoniwa-core, etc.) is containerized independently.
*   Simplified installation with docker.
*   Connect with ROS2, the Web, Python scripts, etc., via a Bridge.
*   Can also run on WSL2 and in the cloud.
*   Integration with gamepads and XR is also possible.

---

## 🧰 Tutorials and Examples (Qiita)

> Since execution in the container pattern involves various setups depending on the purpose and OS configuration, detailed procedures are explained in the following Qiita articles.

| Title                          | Content                                                   | Link                                                                   |
| ------------------------------ | --------------------------------------------------------- | ---------------------------------------------------------------------- |
| PX4 + Unity + Docker Configuration | Configuration to run PX4 and Unity separately in Docker   | [📘 Read Article](https://qiita.com/kanetugu2018/items/d4a21b590950774c6cf8) |
| High-speed setup of ArduPilot with WSL+Docker | Configuration to perform flight control in conjunction with ArduPilot   | [📘 Read Article](https://qiita.com/kanetugu2018/items/59e3b657c402691bff54) |
| Python + Unity + GamePad Configuration    | Example of combining Python control and a gamepad         | [📘 Read Article](https://qiita.com/kanetugu2018/items/24d66fc9ac189feca952) |
| Python API + Unity Configuration       | Example of Unity integration using Python API             | [📘 Read Article](https://qiita.com/kanetugu2018/items/d9763ceb4e527b50c7e2) |
---

## TIPS

- [About integrating with Hakoniwa-enabled PX4/Ardupilot on Windows](/docs/tips/wsl/hakoniwa-wsl.md)
- [How to deal with "Warning, time moved backwards. Restarting timer." when starting Ardupilot on WSL](/docs/tips/wsl/warning-timer.md)
- [How to set up Ardupilot SITL](/docs/tips/wsl/ardupilot-setup.md)
- [How to set up WSL/docker environment](/docs/tips/wsl/docker-setup.md)
- [How to integrate Hakoniwa & PX4 in WSL/docker environment](/docs/tips/wsl/docker-px4.md)
- [How to integrate Hakoniwa & Ardupilot in WSL/docker environment](/docs/tips/wsl/docker-ardupilot.md)
- [How to integrate Hakoniwa & Python API in WSL/docker environment](/docs/tips/wsl/docker-python-api.md)
- [How to operate with a gamepad in WSL/docker environment](/docs/tips/wsl/docker-gamepad.md)
- [How to set up port forwarding in WSL2](/docs/tips/wsl/wsl-portfoward.md)
