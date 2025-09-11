# Python API (for Ardupilot / PX4)

## Overview
This is a Python API for controlling the Hakoniwa drone simulator.
It supports both Ardupilot and PX4 via MAVLink, allowing you to control them with identical API calls.


## Features
- Basic control via API
  - ARM / DISARM
  - Takeoff / Land
  - Move to a specified position
- Retrieve sensor information
  - LiDAR data
  - Camera images
  - Drone pose
- Simultaneous control of multiple vehicles
  - Mix Ardupilot / PX4 using `add_vehicle()`
- Baggage operations (grab / release)

## How it works
- It uses `pymavlink` as the MAVLink communication library.
- Acquisition of sensor data (LiDAR/Camera), which is achieved in coordination with a game engine (Unity/Unreal), is implemented via the Hakoniwa PDU.
- Flight stack-specific differences are absorbed by `ArduPilotController` / `PX4Controller`.
- The high-level API is provided in an integrated manner by `MavlinkMultirotorClient`.

## Class Design Overview
### AbstractFlightController
- A common abstract class for flight controllers.
- Defines `set_api_mode`, `arm`, `takeoff`, `land`, and `go_to_local_ned`.

### ArduPilotController / PX4Controller
- Concrete implementations of `AbstractFlightController`.
- Ardupilot: Implements GUIDED/STABILIZE mode settings, waiting for GPS FIX, etc.
- PX4: Implements OFFBOARD mode and setpoint streaming in a thread.

### MavlinkDrone
- A class representing a single drone.
- Handles connection establishment, pose acquisition, disconnection, etc.

### MavlinkMultirotorClient
- A client that manages multiple vehicles in an integrated way.
- Users call the API through this class.
- Main methods:
  - `add_vehicle(name, conn, type)`
  - `enableApiControl`, `armDisarm`, `takeoff`, `land`, `moveToPosition`
  - `simGetVehiclePose`, `simGetImage`, `getLidarData`, `grab_baggage`

## Class Diagram

```mermaid
classDiagram
    class MavlinkMultirotorClient {
        - Dict~str, MavlinkDrone~ vehicles
        - FrameConverter converter
        + add_vehicle(name, conn, type)
        + confirmConnection()
        + enableApiControl(enable, vehicle_name)
        + armDisarm(arm, vehicle_name)
        + takeoff(height, vehicle_name, timeout)
        + land(vehicle_name)
        + moveToPosition(x,y,z,speed,yaw,timeout,vehicle_name)
        + simGetVehiclePose(vehicle_name)
        + simGetImage(camera_id, type, vehicle_name)
        + getLidarData(vehicle_name)
        + grab_baggage(grab, timeout, vehicle_name)
    }

    class MavlinkDrone {
        - string name
        - string connection_string
        - AbstractFlightController controller
        + connect()
        + disconnect()
        + get_vehicle_pose()
    }

    class AbstractFlightController {
        <<interface>>
        + init_connection(mavlink_conn)
        + set_api_mode()
        + arm()
        + disarm()
        + takeoff(z)
        + land()
        + go_to_local_ned(x,y,z,yaw)
        + stop_movement()
    }

    class ArduPilotController {
        + init_connection()
        + set_api_mode()
        + arm()
        + disarm()
        + takeoff()
        + land()
        + go_to_local_ned()
        + stop_movement()
    }

    class PX4Controller {
        + init_connection()
        + set_api_mode()
        + arm()
        + disarm()
        + takeoff()
        + land()
        + go_to_local_ned()
        + stop_movement()
    }

    MavlinkMultirotorClient "1" --> "*" MavlinkDrone
    MavlinkDrone "1" --> "1" AbstractFlightController
    AbstractFlightController <|-- ArduPilotController
    AbstractFlightController <|-- PX4Controller
```

## Usage Examples
For actual execution procedures, please refer to the following:
- [Multi-vehicle simulation with Ardupilot](/docs/multi_drones/ardupilot.md)
- [Multi-vehicle simulation with PX4](/docs/multi_drones/px4.md)
