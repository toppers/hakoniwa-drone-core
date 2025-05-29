English ｜ [日本語](README-ja.md)

# What is this?

This document explains the environmental simulation features of the Hakoniwa Drone Simulator, such as simulating wind effects. The goal is to apply realistic environmental disturbances like wind to the drone’s flight behavior within the simulation environment.

# Hakoniwa’s Approach to Environmental Simulation

Hakoniwa aims to provide reusable functionality without depending on specific technologies. Therefore, environmental data is managed in program-friendly formats like `json`, allowing for flexible use across different programming languages.

When considering environmental factors in drone simulations, it is efficient to separate static and dynamic information. For example, position data is static and can easily be stored in a database. On the other hand, weather information (e.g., wind, temperature, humidity, rain) is dynamic and varies by time and location.

Thus, Hakoniwa manages environmental information as follows:

- **Spatial Information**  
  Spatial information assigns a unique ID (area ID) to any given region. This area ID allows easy reference to information for different spaces.

- **Spatial Property Information**  
  Property information such as wind, temperature, and humidity is tied to specific areas. These properties are linked to spatial information using area IDs.

Based on this design, Hakoniwa provides flexible and reusable environmental simulations.

# Architecture

![image](./images/architecture.png)

This architecture diagram shows the overall flow of environmental simulation in the Hakoniwa Drone Simulator.

1. **Processing Environmental Information**  
   Hakoniwa assets monitor Hakoniwa PDU data and obtain the corresponding area ID based on the drone's position. Using this area ID, the system reads the property data (e.g., wind, temperature, humidity) and triggers environmental disturbance events for the drone.

2. **Applying Disturbances and Running the Simulation**  
   The Hakoniwa Drone Simulator uses the disturbances (e.g., wind effects) received from the environment to simulate the drone’s sensor data and physical behavior, providing a realistic simulation of drone operations.

3. **Retrieving and Transmitting Drone Position Information**  
   The simulation results, including the drone’s position and orientation data, are written to the Hakoniwa PDU data. This data is then visualized in the game engine (Unity or Unreal Engine), where the environmental disturbances are automatically reflected.

# Data Structure Definition for Spatial Information

- **Coordinate System**: ROS coordinate system is used.
- **Spatial Definition**: Defined in `space_areas.json`, where regions are specified using AABB (axis-aligned bounding box).
- **Property Definition**: Defined in `area_properties.json`, associating attributes like wind and temperature with specific areas using `area_id`.

1. **`space_areas.json`**:
   - Defines each region’s spatial boundaries. Each area is assigned a unique `area_id`, and the bounds are specified using AABB (minimum and maximum points).

2. **`area_properties.json`**:
   - Defines properties (e.g., wind, temperature) for each area. Properties are linked to spatial information using `area_id`, making it easy to assign different properties to different regions.

## 1. Spatial Definition (`space_areas.json`)

```json
{
  "space_areas": [
    {
      "area_id": "area_1",
      "bounds": {
        "min": { "x": 0, "y": 0, "z": 0 },   // Minimum point
        "max": { "x": 100, "y": 100, "z": 50 } // Maximum point
      }
    },
    {
      "area_id": "area_2",
      "bounds": {
        "min": { "x": 101, "y": 0, "z": 0 },
        "max": { "x": 200, "y": 100, "z": 50 }
      }
    }
  ]
}
```

## 2. Property Definition (`area_properties.json`)

```json
{
  "area_properties": [
    {
      "area_id": "area_1",
      "properties": {
        "wind": { 
          "velocity": { "x": 5.0, "y": 2.0, "z": -1.0 }  // Wind speed (m/s)
        },
        "temperature": 20.0  // Temperature (Celsius)
      }
    },
    {
      "area_id": "area_2",
      "properties": {
        "wind": { 
          "velocity": { "x": -3.0, "y": 1.0, "z": 0.0 }
        },
        "temperature": 25.0
      }
    }
  ]
}
```

# Class Design for Handling Spatial Information

![image](images/class-diagram.png)

This class design aims to provide a flexible structure for managing spatial information in Hakoniwa. The design is based on Hakoniwa’s specifications, but is intended to allow future replacement and customization of spatial information or environmental settings.

1. **`HakoEnvEvent`**  
   - Main class for managing environmental events, such as wind and temperature.
   - It applies environmental information to drones and other simulation elements.

2. **`IHakoAreaPropAccessor` and `IHakoAreaAccessor` (Abstract Classes)**  
   - Interfaces for handling data from `area_properties.json` and `space_areas.json`.
   - They provide a unified way to access spatial and property information.
   - These abstract classes allow for future extensibility and the replacement of different spatial or property data sources.

3. **`HakoAreaPropAccessorImpl` and `HakoAreaAccessorImpl`**  
   - Concrete implementation classes for retrieving spatial and property information based on Hakoniwa specifications.
   - They fetch data from `space_areas.json` and `area_properties.json` and apply it to the simulation.

4. **`HakoAABBObjectSpace`**  
   - A class that defines spatial regions using axis-aligned bounding boxes (AABB). This allows efficient definition and management of spatial areas.

This design links spatial and property information via `area_id`, making it easy to apply different properties (e.g., wind speed and temperature) to different areas. By using abstract classes, this design also supports future expansion and compatibility with other specifications.

# Sample Implementation

The sample implementation is available here: [Hakoniwa Drone's Environment Assets](https://github.com/toppers/hakoniwa-px4sim/tree/main/drone_api/assets)

- **`hako_env_event.py`**: Contains the implementation of the HakoEnvEvent, which simulates environmental events.
- **`lib`**: Contains the Python implementations based on the class designs, including access logic for spatial and property information.
- **`config`**: Contains sample environment data, including `space_areas.json` and `area_properties.json`.
- **`tests`**: Contains test scripts to verify the functionality and behavior of the implementation.

Based on this sample implementation, you can set up the environment and try the simulation as needed.


---

# 📘 Sample Execution Guide: Wind Asset + Remote Control (Hakoniwa Drone)

## ✅ Prerequisites

* Python 3.12 is installed
* Unity editor is installed and the `hakoniwa-unity-drone/simulation` project is open
* `bash` is available (macOS or Ubuntu recommended)
* Supported OS: **macOS, Ubuntu 22.04, 24.04**
* This sample demonstrates **remote control operation of the drone**
* You will need **3 terminals (or terminal tabs)** to run the full system

---

## 📋 Overview

This sample demonstrates how to run the Hakoniwa drone simulator with the following setup:

1. **Terminal A**: Start the drone simulator
2. **Terminal B**: Launch the wind asset (`HakoEnvEvent`)
3. **Terminal C**: Operate the drone using a game controller (RC input)

---

## 🖥️ Terminal A: 

Start the Drone Simulator

This command starts the physical simulation backend.

---

## 🌬️ Terminal B: 

Launch the Wind Asset (HakoEnvEvent)

```bash
cd hakoniwa-drone-core/drone_api
export PYTHONPATH=${PYTHONPATH}:`pwd`
export PYTHONPATH=${PYTHONPATH}:`pwd`/assets
export PYTHONPATH=${PYTHONPATH}:`pwd`/assets/lib

cd assets
python3 hako_env_event.py <PDU-config-file-path> 20 config
```

### 💡 Notes:

* `<PDU-config-file-path>` should be the path to your configuration file (e.g., `../config/custom.json`)
* `20` represents the event loop period in milliseconds (you may adjust it)


## 🖼️ Unity Application: Visualization

Launch the Unity editor and open the `hakoniwa-unity-drone/simulation` project.
After the scene loads, press the `START` button in the UI to begin simulation.

## 🎮 Terminal C: 

Start the Remote Control (RC) Input

```bash
cd hakoniwa-drone-core/drone_api
python rc/rc-custom.py <PDU-config-file-path> rc/rc_config/ps4-control.json
```

* Connect a PS4 or PS5 controller via USB or Bluetooth
* `ps4-control.json` defines the input mapping for the controller

---

