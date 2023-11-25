# Architecture

This architectural diagram represents the simulation configuration of a drone, including the PX4 platform and related sensors and actuators. Each component processes a specific type of data and passes this data to other parts within the system. This interaction simulates the real-world operation of the drone.

![スクリーンショット 2023-11-25 12 26 19](https://github.com/toppers/hakoniwa-px4sim/assets/164193/4402d0f2-e21a-4764-a651-11f07132fbc7)


Here is a table summarizing the input/output data and overview of each component in the aforementioned architecture.

|component|type|overview|input|output|
|---|---|---|---|---|
|PX4|Platform|Core flight control platform for the drone| [HIL_SENSOR](https://github.com/toppers/hakoniwa-px4sim/blob/main/docs/phys_specs/data/mavlink/HIL_SENSOR/README.md) <br> [HIL_GPS](https://github.com/toppers/hakoniwa-px4sim/blob/main/docs/phys_specs/data/mavlink/HIL_GPS/README.md) | [HIL_ACTUATOR_CONTROLS](https://github.com/toppers/hakoniwa-px4sim/blob/main/docs/phys_specs/data/mavlink/HIL_ACTUATOR_CONTROLS/README.md)|
|DronePhysics|Physics|Simulates physical dynamics of the drone| [RotorSpeedVariation](https://github.com/toppers/hakoniwa-px4sim/blob/main/docs/phys_specs/data/physics/README.md#rotorspeedvariation) | [Position](https://github.com/toppers/hakoniwa-px4sim/blob/main/docs/phys_specs/data/physics/README.md#position)<br>[Velocity](https://github.com/toppers/hakoniwa-px4sim/blob/main/docs/phys_specs/data/physics/README.md#velocity)<br>[Angle](https://github.com/toppers/hakoniwa-px4sim/blob/main/docs/phys_specs/data/physics/README.md#angle)<br>[AngularVelocity](https://github.com/toppers/hakoniwa-px4sim/blob/main/docs/phys_specs/data/physics/README.md#angularvelocity)<br>|
|RotorDynamics|Actuator|Controls the speed of rotors based on input| [HIL_ACTUATOR_CONTROLS](https://github.com/toppers/hakoniwa-px4sim/blob/main/docs/phys_specs/data/mavlink/HIL_ACTUATOR_CONTROLS/README.md) | [RotorSpeedVariation](https://github.com/toppers/hakoniwa-px4sim/blob/main/docs/phys_specs/data/physics/README.md#rotorspeedvariation) |
|Acceleration|Sensor|Measures acceleration in 3D space| [Velocity](https://github.com/toppers/hakoniwa-px4sim/blob/main/docs/phys_specs/data/physics/README.md#velocity) | [HIL_SENSOR](https://github.com/toppers/hakoniwa-px4sim/blob/main/docs/phys_specs/data/mavlink/HIL_SENSOR/README.md)/acc |
|Gyro|Sensor|Measures rotational motion| [AngularVelocity](https://github.com/toppers/hakoniwa-px4sim/blob/main/docs/phys_specs/data/physics/README.md#angularvelocity) | [HIL_SENSOR](https://github.com/toppers/hakoniwa-px4sim/blob/main/docs/phys_specs/data/mavlink/HIL_SENSOR/README.md)/gyro |
|Geomagnetic|Sensor|Measures Earth's magnetic field for orientation| [Angle](https://github.com/toppers/hakoniwa-px4sim/blob/main/docs/phys_specs/data/physics/README.md#angle) | [HIL_SENSOR](https://github.com/toppers/hakoniwa-px4sim/blob/main/docs/phys_specs/data/mavlink/HIL_SENSOR/README.md)/mag |
|Barometric|Sensor|Measures atmospheric pressure for altitude| [Position](https://github.com/toppers/hakoniwa-px4sim/blob/main/docs/phys_specs/data/physics/README.md#position) | [HIL_SENSOR](https://github.com/toppers/hakoniwa-px4sim/blob/main/docs/phys_specs/data/mavlink/HIL_SENSOR/README.md)/pressure |
|GPS|Sensor|Provides location coordinates and velocity| [Velocity](https://github.com/toppers/hakoniwa-px4sim/blob/main/docs/phys_specs/data/physics/README.md#velocity) | [HIL_GPS](https://github.com/toppers/hakoniwa-px4sim/blob/main/docs/phys_specs/data/mavlink/HIL_GPS/README.md) |

Here is a table of the sending intervals for the simulator's MAVLink messages, as observed in AirSim:

| Sensor Data  | Sending Interval (ms) |
|--------------|-----------------------|
| SYSTEM_TIME  | 3                     |
| HIL_SENSOR   | 3                     |
| HIL_GPS      | 21                    |
