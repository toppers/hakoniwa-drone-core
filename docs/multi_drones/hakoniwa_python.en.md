# What is this?

This document provides instructions for controlling multiple vehicles simultaneously using the Hakoniwa Drone Operation Python API.
Basically, you can control two or more vehicles by simply **changing the drone name** in the existing sample scripts.

# Prerequisites

It is assumed that the Python API control for a single vehicle is already working.

For instructions on how to control a single vehicle, please refer to the following article:
[Unity + Python for Drone Control: Hakoniwa Drone Simulator that can be used as is for practical training and classes](https://qiita.com/kanetugu2018/items/d9763ceb4e527b50c7e2)

## Python API (Multi-vehicle) Setup

### Sample Scripts

There are several control samples in the `drone_api/rc` directory.

```tree
drone_api/rc
├── api_control_sample.py   # For Drone
├── api_control_sample2.py  # For Drone1
```

*   `api_control_sample.py` is a sample for controlling **Drone** (the first vehicle).
*   `api_control_sample2.py` is a sample for controlling **Drone1** (the second vehicle).

By **running each in a separate process at the same time**, you can control multiple vehicles simultaneously.

---

## Execution Procedure

### 1) Hakoniwa (Docker)

```bash
bash hakoniwa-drone-core/docker/tools/run-hako.bash api \
  hakoniwa-drone-core/config/pdudef/webavatar-2.json 2
```

### 2) Python Script (Inside Docker)

```bash
cd hakoniwa-drone-core/drone_api

# Vehicle 0 (Drone)
python3 rc/api_control_sample.py config/pdudef/webavatar-2.json

# Vehicle 1 (Drone1)
python3 rc/api_control_sample2.py config/pdudef/webavatar-2.json
```

* Please execute each in a separate terminal (process).

---

### Operation Check

On Unity, confirm that two drones take off at the same time and execute the scenarios described in each sample code (movement, cargo operation, sensor acquisition, etc.).

(The scene name is `WebAvatar2`)

---

## Instance Correspondence Table (Example)

| Vehicle | Drone Name (Python) | Sample Script | Configuration File |
| -- | --------------- | ------------------------ | --------------------- |
| 0  | `Drone`         | `api_control_sample.py`  | `drone_config_0.json` |
| 1  | `Drone1`        | `api_control_sample2.py` | `drone_config_1.json` |
