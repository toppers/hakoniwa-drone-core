# Barometric Sensor Component Specification

## Input

*   **DronePositionType**: Current position of the drone.
*   **AircraftInputType**: Contains environmental disturbances, specifically `d_atm.sea_level_atm` (sea level atmospheric pressure) and `d_temp.value` (sea level temperature in Celsius).

## Output

*   **DroneBarometricPressureType**: Contains:
    *   `abs_pressure`: Absolute pressure in Pascals.
    *   `diff_pressure`: Differential pressure (currently always 0).
    *   `pressure_alt`: Pressure altitude in meters.

## External Parameters

### Observation Interval (Δt)
- **Description**: Δt represents the time interval between each measurement taken by the barometric sensor. This parameter determines the frequency at which the sensor data is sampled and updated.
- **Impact**: The choice of Δt affects the resolution and responsiveness of the barometric readings. Shorter intervals lead to more frequent updates but can increase noise, while longer intervals can smooth out data but may reduce sensitivity to quick changes.

### Moving Average Window (N)
- **Description**: N is the number of samples used to calculate the moving average of the altitude data. This parameter defines the window size over which the data is averaged.
- **Impact**: Setting N involves a trade-off between data smoothness and latency. A larger N provides smoother data by averaging over more samples, which can reduce the effect of transient noise. However, it also introduces a delay in the sensor's response to changes.

### Noise Characteristics
- **Average (Mean) of Noise**: The average value of the noise added to the barometric data is set to zero. This means that over time, the noise will not have a net positive or negative effect on the pressure readings.
- **Variance of Noise**: The variance parameter specifies the spread of noise around the average. Even with an average of zero, the noise can vary, representing the randomness or fluctuation level in the sensor readings.

The integration of zero-mean noise ensures that any bias is minimized, allowing the simulation to accurately reflect only the random variations typical of real-world conditions.

## Operational Details

- **Altitude to Pressure Conversion**: The sensor converts the drone's altitude into barometric pressure using a standard atmospheric model. The `alt2baro` function implements this conversion, taking into account sea-level atmospheric pressure and temperature, which can be influenced by environmental disturbances.
- **Moving Average**: A moving average filter is applied to the calculated altitude to smooth out readings and reduce noise.
- **Noise Integration**: Random noise with a zero mean and specified variance is added to the final pressure and altitude values to simulate real-world sensor inaccuracies.
