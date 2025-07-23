# Architecture

This architectural diagram represents the simulation configuration of a drone, including the PX4 platform and related sensors and actuators. Each component processes a specific type of data and passes this data to other parts within the system. This interaction simulates the real-world operation of the drone.

![Architecture Diagram](/docs/images/architecture-aircraft.png)


Here is a table summarizing the input/output data and overview of each component in the aforementioned architecture.

|component|type|overview|input|output|
|---|---|---|---|---|
|PX4|Platform|Core flight control platform for the drone| [HIL_SENSOR](/docs/flight_controller/mavlink/HIL_SENSOR/README.md) <br> [HIL_GPS](/docs/flight_controller/mavlink/HIL_GPS/README.md) | [HIL_ACTUATOR_CONTROLS](/docs/flight_controller/mavlink/HIL_ACTUATOR_CONTROLS/README.md)|
|[DroneDynamics](/docs/architecture/physics/README.md#body-frame-dynamics)|Physics|Simulates physical dynamics of the drone (implemented by `DroneDynamicsBodyFrame` or `MDroneDynamicsBodyFrame`)|[Thrust/Torque](/docs/fundamental/README.md#thrust)| [Position](/docs/fundamental/README.md#position)<br>[Velocity](/docs/fundamental/README.md#velocity)<br>[Angle](/docs/fundamental/README.md#angle)<br>[Angular Velocity(Body)](/docs/fundamental/README.md#angular-velocity-in-body-coordinate-system)<br>[Velocity(Body)](/docs/fundamental/README.md#velocity-in-body-coordinate-system)|
|[ThrustDynamics](/docs/architecture/aircraft/thruster/README.md)|Physics|Simulates physical dynamics of multiple rotors (implemented by `ThrustDynamicsNonLinear`)|[RotorSpeed](/docs/fundamental/README.md#rotor-speed)|[Thrust/Torque](/docs/fundamental/README.md#thrust)|
|[RotorDynamics](/docs/architecture/aircraft/rotor/README.md)|Actuator|Controls the speed of rotors based on input (implemented by `RotorDynamics`)| [HIL_ACTUATOR_CONTROLS](/docs/flight_controller/mavlink/HIL_ACTUATOR_CONTROLS/README.md) | [RotorSpeed](/docs/fundamental/README.md#rotor-speed) |
|[Acceleration](/docs/architecture/aircraft/sensor/acceleration/README.md)|Sensor|Measures acceleration in 3D space| [Velocity(Body)](/docs/fundamental/README.md#velocity-in-body-coordinate-system)| [HIL_SENSOR](/docs/flight_controller/mavlink/HIL_SENSOR/README.md)/acc |
|[Gyro](/docs/architecture/aircraft/sensor/gyro/README.md)|Sensor|Measures rotational motion (implemented by `SensorGyro`)| [Angular Velocity(Body)](/docs/fundamental/README.md#angular-velocity-in-body-coordinate-system)| [HIL_SENSOR](/docs/flight_controller/mavlink/HIL_SENSOR/README.md)/gyro |
|[Geomagnetic](/docs/architecture/aircraft/sensor/geomagnet/README.md)|Sensor|Measures Earth's magnetic field for orientation (implemented by `SensorMag`)| [Angle](/docs/fundamental/README.md#angle) | [HIL_SENSOR](/docs/flight_controller/mavlink/HIL_SENSOR/README.md)/mag |
|[Battery](/docs/architecture/aircraft/battery/README.md)|Power|Simulates battery discharge and provides voltage and status (implemented by `BatteryDynamics`)|Current from Rotors<br>Temperature|Voltage<br>Discharge Current<br>Discharge Capacity<br>Battery Status|
|[GPS](/docs/architecture/aircraft/sensor/gps/README.md)|Sensor|Provides location coordinates and velocity (implemented by `SensorGps`)| [Position](/docs/fundamental/README.md#position)<br>[Velocity](/docs/fundamental/README.md#velocity) | [HIL_GPS](/docs/flight_controller/mavlink/HIL_GPS/README.md) |

Here is a table of the sending intervals for the simulator's MAVLink messages, as observed in AirSim:

| Sensor Data  | Sending Interval (ms) |
|--------------|-----------------------|
| SYSTEM_TIME  | 3                     |
| HIL_SENSOR   | 3                     |
| HIL_GPS      | 21                    |

