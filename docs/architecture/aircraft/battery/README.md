# Battery Component Specification

## Input

*   **Current from Rotors**: The current drawn by each rotor, used to calculate the total discharge.
*   **Disturbance (Temperature)**: Environmental temperature, which can affect battery discharge characteristics.

## Output

*   **Voltage**: The current battery voltage.
*   **Discharge Current**: The total current being discharged from the battery.
*   **Discharge Capacity**: The total capacity discharged from the battery in Ampere-hours (Ah).
*   **Battery Status**: Includes full voltage, current voltage, temperature, and status (green, yellow, red).

## External Parameters

### Observation Interval (Δt)
- **Description**: Δt represents the time interval between each battery state update.
- **Impact**: Affects the resolution and responsiveness of battery state changes.

### Battery Model Parameters
- **`vendor`**: String, name of the battery vendor.
- **`BatteryModelCsvFilePath`**: String, path to a CSV file containing detailed discharge data for the battery model. If empty, a linear model is used.
- **`model`**: String, specifies the battery model to use. Can be "constant" or other values for a linear/CSV-based model.
- **`NominalCapacity`**: Double, the nominal capacity of the battery in Ampere-hours (Ah).
- **`EODVoltage`**: Double, End-of-Discharge Voltage.
- **`NominalVoltage`**: Double, the nominal voltage of the battery.
- **`VoltageLevelGreen`**: Double, voltage threshold for "green" status.
- **`VoltageLevelYellow`**: Double, voltage threshold for "yellow" status.
- **`CapacityLevelYellow`**: Double, capacity threshold for "yellow" status.

## Operational Details

-   **Discharge Calculation**: The battery tracks the accumulated discharge capacity based on the current drawn by the rotors and the simulation time step.
-   **Battery Models**:
    *   **Constant Model**: If `model` is "constant", the battery voltage remains at `NominalVoltage`.
    *   **Linear Model**: If `BatteryModelCsvFilePath` is empty and `model` is not "constant", a simplified linear discharge model is used, transitioning from `NominalVoltage` to `EODVoltage` based on `NominalCapacity`, `VoltageLevelGreen`, and `CapacityLevelYellow`.
    *   **CSV-based Model**: If `BatteryModelCsvFilePath` is provided and the file exists, a more detailed discharge model is used. This model interpolates voltage based on discharged capacity and temperature data loaded from the CSV file.
-   **Voltage Output**: The `get_vbat()` method returns the current calculated battery voltage.
-   **Status Calculation**: The `get_status()` method provides a simplified battery status (green, yellow, red) based on the current voltage and predefined thresholds.
-   **Noise**: The current implementation does not explicitly show noise being added to the battery voltage or current.
