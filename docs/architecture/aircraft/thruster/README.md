# Thrust Component Specification

## Overview

The `ThrustDynamicsNonLinear` component calculates the total thrust and torque generated by all rotors based on their individual speeds and the drone's configuration. It accounts for atmospheric pressure and the rotational acceleration of the rotors.

## Input

*   **Rotor Speeds**: An array of `DroneRotorSpeedType` values, representing the current rotational speed of each rotor.
*   **Atmospheric Pressure**: The current atmospheric pressure, which influences the thrust and torque calculations.

## Output

*   **Total Thrust**: The total upward force generated by all rotors in Newtons (N).
*   **Total Torque**: The total torque applied to the drone's body in Newton-meters (Nm), affecting its roll, pitch, and yaw.

## External Parameters

### Thrust and Torque Constants
-   **`param_Ct`**: Thrust coefficient, a constant used in calculating the total thrust.
-   **`param_Cq`**: Torque coefficient, a constant used in calculating the total torque.
-   **`param_J`**: Moment of inertia, a constant used in calculating the total torque.

### Rotor Configuration
-   **`rotor_config`**: An array of `RotorConfigType` structures, defining the position and direction (clockwise/counter-clockwise) of each rotor.

## Operational Details

-   **Thrust Calculation**: The total thrust is calculated by summing the individual thrust contributions of each rotor, taking into account the `param_Ct` and atmospheric pressure.
-   **Torque Calculation**: The total torque (roll, pitch, and yaw) is calculated based on the individual rotor speeds, their positions, directions, rotational accelerations, `param_Ct`, `param_Cq`, `param_J`, and atmospheric pressure.
-   **Rotor Speed Tracking**: The component keeps track of the previous rotor speeds to calculate rotational acceleration, which is used in torque calculations.
-   **Reset Functionality**: The `reset()` method initializes the total thrust, torque, and previous rotor speeds to zero.
