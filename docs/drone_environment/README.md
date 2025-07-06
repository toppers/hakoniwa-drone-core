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
- **Spatial Definition**: Defined in `area.json`, where regions are specified using AABB (axis-aligned bounding box).
- **Property Definition**: Defined in `area_property.json`, associating attributes like wind and temperature with specific areas using `area_id`.
- **Boundary Definition**: Defined in `boundary.json`, which specifies physical boundaries such as the ground and ceiling.

1. **`area.json`**:
   - Defines the spatial boundaries of each area. Each area is assigned a unique `area_id`, and its bounds are specified using an AABB (Axis-Aligned Bounding Box) with minimum and maximum points.

2. **`area_property.json`**:
   - Defines physical properties for each area, such as wind, temperature, and sea-level atmospheric pressure. These properties are linked to the spatial information in `area.json` via `area_id`, making it easy to assign different environmental conditions to different regions.

3. **`boundary.json`**:
    - Defines the physical boundaries within the simulation space, such as the ground and ceiling. This prevents the drone from flying outside the designated area.

## 1. Spatial Definition (`area.json`)


```json
{
  "space_areas": [
    {
      "area_id": "area_1",
      "bounds": {
        "min": { "x": -2.0, "y": -2.0, "z": 0 },
        "max": { "x": 2.0,  "y": 2.0,  "z": 20 }
      }
    },
    {
      "area_id": "area_2",
      "bounds": {
        "min": { "x": 2.0, "y": -2.0, "z": 0 },
        "max": { "x": 6.0, "y":  2.0, "z": 20 }
      }
    }
  ]
}
```

- `space_areas`: (list) A list of spatial area definitions.
  - `area_id`: (string) A unique identifier for the area.
  - `bounds`: (object) The AABB defining the spatial extent of the area.
    - `min`: (object) The minimum coordinate point of the AABB (in meters).
      - `x`, `y`, `z`: (float)
    - `max`: (object) The maximum coordinate point of the AABB (in meters).
      - `x`, `y`, `z`: (float)

## 2. Property Definition (`area_property.json`)


```json
{
    "area_properties": [
      {
        "area_id": "area_1",
        "properties": {
          "wind_velocity": [0.0, 0.0, 0.0],
          "temperature": 10.5,
          "sea_level_atm": 0.9
        }
      },
      {
        "area_id": "area_2",
        "properties": {
          "wind_velocity": [0.0, -1.0, 0.0],
          "temperature": -15.0,
          "sea_level_atm": 1.1
        }
      }
    ]
  }
```

- `area_properties`: (list) A list of area property definitions.
  - `area_id`: (string) Corresponds to the `area_id` in `area.json`.
  - `properties`: (object) The physical properties of the area.
    - `wind_velocity`: (array of float) The wind velocity vector [x, y, z] (in m/s).
    - `temperature`: (float) The ambient temperature (in degrees Celsius).
    - `sea_level_atm`: (float) The sea-level atmospheric pressure (in atm).

## 3. Boundary Definition (`boundary.json`)

```json
[
    {
        "name": "ground",
        "position": [0.0, 0.0, 0.0],
        "size": [10.0, 10.0],
        "rotation": [0.0, 0.0, 0.0]
    },
    {
        "name": "ceiling",
        "position": [0.0, 0.0, 2.0],
        "size": [1.0, 1.0],
        "rotation": [0.0, 0.0, 0.0]
    }
]
```

- `name`: (string) The name of the boundary.
- `position`: (array of float) The center position of the boundary rectangle [x, y, z] (in meters).
- `size`: (array of float) The size of the boundary rectangle [width, height] (in meters).
- `rotation`: (array of float) The Euler angles of the boundary rectangle [Z, Y, X] (in degrees).

# Class Design for Handling Spatial Information

![image](images/class-diagram.png)

This class design aims to provide a flexible structure for managing spatial information in Hakoniwa. The design is based on Hakoniwa’s specifications, but is intended to allow future replacement and customization of spatial information or environmental settings.

1. **`HakoEnvEvent`**  
   - Main class for managing environmental events, such as wind and temperature.
   - It applies environmental information to drones and other simulation elements.

2. **`IHakoAreaPropAccessor` and `IHakoAreaAccessor` (Abstract Classes)**  
   - Interfaces for handling data from `area_property.json` and `area.json`.
   - They provide a unified way to access spatial and property information.
   - These abstract classes allow for future extensibility and the replacement of different spatial or property data sources.

3. **`HakoAreaPropAccessorImpl` and `HakoAreaAccessorImpl`**  
   - Concrete implementation classes for retrieving spatial and property information based on Hakoniwa specifications.
   - They fetch data from `area.json` and `area_property.json` and apply it to the simulation.

4. **`HakoAABBObjectSpace`**  
   - A class that defines spatial regions using axis-aligned bounding boxes (AABB). This allows efficient definition and management of spatial areas.

5. **`HakoBoundary`**
   - A class used to calculate the distance between the drone and boundaries (e.g., the ground) defined in `boundary.json`. This is utilized for simulating propeller effects, such as ground effect.

This design links spatial and property information via `area_id`, making it easy to apply different properties (e.g., wind speed and temperature) to different areas. By using abstract classes, this design also supports future expansion and compatibility with other specifications.

# Sample Implementation

The sample implementation is available here: [Hakoniwa Drone's Environment Assets](https://github.com/toppers/hakoniwa-px4sim/tree/main/drone_api/assets)

- **`hako_env_event.py`**: Contains the implementation of the HakoEnvEvent, which simulates environmental events.
- **`lib`**: Contains the Python implementations based on the class designs, including access logic for spatial and property information.
- **`config`**: Contains sample environment data, including `area.json`, `area_property.json`, and `boundary.json`.
- **`tests`**: Contains test scripts to verify the functionality and behavior of the implementation.

Based on this sample implementation, you can set up the environment and try the simulation as needed.


# Use Case Examples

This environmental simulation feature can be used to test drone behavior in various scenarios:

- **Wind Resistance Testing in Specific Areas**
  - Define a narrow space in `area.json` and set a strong crosswind for that area in `area_property.json`.
  - This allows you to evaluate the drone's attitude control and the robustness of its control algorithms when passing through that area.

- **Ground Effect Simulation**
  - Define a ground plane in `boundary.json` to observe the drone's behavior during landing.
  - You can simulate the influence of propeller wash on the airframe near the ground (e.g., increased lift) to validate landing control logic.

- **Complex Weather Environment Reproduction**
  - By finely dividing the space in `area.json` and slightly varying the wind speed and atmospheric pressure in each area, you can simulate complex airflows, such as those created by buildings or terrain, to test the drone's stability.

# How to Customize the Environment

Users can freely create their own simulation environments by editing the JSON files in the `config` directory.

1. **Prepare Configuration Files**
   - Create your own environment configuration directory, referencing the `drone_api/assets/config` directory.

2. **Define Spatial Partitions (`area.json`)**
   - Decide how you want to divide the simulation space and define the scope of each area using AABBs.
   - For example, you can define a specific flight path as a separate area.

3. **Set Physical Properties (`area_property.json`)**
   - For each `area_id` defined in `area.json`, set parameters such as wind velocity, temperature, and atmospheric pressure.
   - To disable wind, set `wind_velocity` to `[0.0, 0.0, 0.0]`.

4. **Run the Simulation**
   - When executing `hako_env_event.py`, specify the path to your created configuration directory as an argument.
   - This will start the simulation with your customized environment.


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

