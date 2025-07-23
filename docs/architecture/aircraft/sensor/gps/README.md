# GPS Sensor Component Specification

## Input

*   **DronePositionType**: Current position of the drone in NED (North-East-Down) coordinates.
*   **DroneVelocityType**: Current velocity of the drone in NED (North-East-Down) coordinates.

## Output

*   **DroneGpsDataType**: Contains:
    *   `lat`: Latitude in degrees.
    *   `lon`: Longitude in degrees.
    *   `alt`: Altitude in meters.
    *   `vel`: Ground speed in m/s.
    *   `vn`: North velocity in m/s.
    *   `ve`: East velocity in m/s.
    *   `vd`: Down velocity in m/s.
    *   `cog`: Course over ground in degrees.
    *   `eph`: GPS horizontal accuracy estimate (fixed at 10).
    *   `epv`: GPS vertical accuracy estimate (fixed at 10).
    *   `num_satelites_visible`: Number of visible satellites (fixed at 10).

## External Parameters

### Observation Interval (Δt)
- **Description**: Δt represents the time interval between each measurement taken by the GPS sensor. This parameter determines the frequency at which the sensor data is sampled and updated.
- **Impact**: The choice of Δt affects the resolution and responsiveness of the GPS readings. Shorter intervals lead to more frequent updates but can increase noise, while longer intervals can smooth out data but may reduce sensitivity to quick changes.

### Moving Average Window (N)
- **Description**: N is the number of samples used to calculate the moving average of the GPS data. This parameter defines the window size over which the data is averaged.
- **Impact**: Setting N involves a trade-off between data smoothness and latency. A larger N provides smoother data by averaging over more samples, which can reduce the effect of transient noise. However, it also introduces a delay in the sensor's response to changes.

### Noise Characteristics
- **Average (Mean) of Noise**: The average value of the noise added to the GPS data is set to zero. This means that over time, the noise will not have a net positive or negative effect on the GPS readings.
- **Variance of Noise**: The variance parameter specifies the spread of noise around the average. Even with an average of zero, the noise can vary, representing the randomness or fluctuation level in the sensor readings.

The integration of zero-mean noise ensures that any bias is minimized, allowing the simulation to accurately reflect only the random variations typical of real-world conditions.

## Operational Details

- **Coordinate Conversion (NED to Geodetic)**: The sensor converts NED (North-East-Down) coordinates to geodetic coordinates (latitude, longitude, altitude) using Vincenty's Formulae. This method provides high-accuracy transformation based on the WGS-84 ellipsoid model, accounting for the Earth's ellipsoidal shape.
- **Velocity Calculation**: Calculates ground speed, and North, East, and Down velocities.
- **Course Over Ground (COG) Calculation**: Determines the course over ground based on North and East velocities.
- **Moving Average**: A moving average filter is applied to latitude, longitude, altitude, and velocity components to smooth out readings and reduce noise.
- **Noise Integration**: Random noise with a zero mean and specified variance is added to the final GPS values to simulate real-world sensor inaccuracies.