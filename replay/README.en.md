# Hakoniwa Drone – Log Replay Feature

## Overview
This feature replays the flight status of a drone based on `drone_dynamics.csv` logs recorded by the Hakoniwa drone simulator.
It works in conjunction with Hakoniwa's Conductor (in manual timing control mode) to write log data as PDUs to shared memory at specified time intervals.

Since it uses the same PDU interface as the simulation environment (Unity/Unreal), it is possible to **transparently switch between live simulation and replay playback**.
Internally, it utilizes the `pandas` library for efficient time-series data processing.

---

## Feature List
- **Log Playback**
  - Targets `drone_dynamics.csv` for playback.
  - Generates PDUs (Twist type) along the time series and writes them to shared memory.
- **Multiple Drone Support**
  - Can simultaneously play back multiple log directories, such as `drone_log0`, `drone_log1`.
  - Manages the mapping of each log to a drone name and PDU name.
- **Playback Control**
  - Specification of playback range (by time or seconds).
  - Change of playback speed (e.g., slow playback at 0.5x speed).
- **Data Handling**
  - Automatically cleans data when loading logs, such as invalid data (NaN/inf) and timestamp distortions.
  - Converts coordinates from the standard NED coordinate system in the simulator to the ROS coordinate system, which is common in ROS, for output.

---

## Module Configuration

```
replay/
├── __init__.py
├── clock.py                 # Manages the global replay time
├── hako_asset_replayer.py   # Executes log playback, writes to PDU, and registers as a Hakoniwa asset
├── logdata_model.py         # Parses CSV logs, provides data cleansing and time-series access
└── replay_model.py          # Reads the replay.json file and manages playback settings
```

### Role of Each Module
- **hako_asset_replayer.py**
  This is the entry point for the feature. It is registered as a Hakoniwa asset and executes a manual timing control loop under the direction of the Conductor.
  It manages `DroneReplayer` internally and writes the log data of each drone as a PDU to shared memory.

- **replay_model.py**
  It is responsible for reading and parsing the `replay.json` configuration file.
  It interprets the logs to be replayed, drone names, PDU settings, playback range, speed, etc., and converts them into a format that `HakoAssetReplayer` can use.

- **logdata_model.py**
  Reads `drone_dynamics.csv` as a `pandas` DataFrame.
  After performing cleansing processes such as validation of required fields, removal of invalid values, and ensuring monotonic increase of timestamps, it converts the coordinate system from NED to ROS.

- **clock.py**
  A simple class for managing the time during replay (in microseconds).
  It manages the start and end times, and the progression to the next time step.

---

## Replay Configuration File (`replay.json`)

The behavior of the replay is defined in the `replay.json` file.

### Configuration Items
- `log_map` (required): Maps the log directories you want to play back to the corresponding drone names and PDU names.
  - `(key)`: Path to a log directory like `drone_log0`.
  - `drone_name`: Hakoniwa asset name.
  - `pdu_name`: PDU channel name (e.g., "pos").
- `pdu_def_file` (required): Path to the JSON file that defines the PDU structure.
- `start_time`: The base start time for the replay (in `HH:MM:SS.ffffff` format). Used in combination with `range_sec`.
- `range_sec`: Specifies the playback range in relative seconds from `start_time`. This takes precedence over `range_timestamp`.
  - `begin`: Start second.
  - `end`: End second.
- `range_timestamp`: Specifies the playback range in absolute time.
  - `begin`: Start time (in `HH:MM:SS.ffffff` format).
  - `end`: End time (in `HH:MM:SS.ffffff` format).
- `speed`: Playback speed. `1.0` is normal speed, `0.5` is half speed (slow playback).

### `replay.json` Example

```json
{
  "log_map": {
    "../drone_log1": {
      "drone_name": "Drone",
      "pdu_name": "pos"
    }
  },
  "pdu_def_file": "config/pdudef/webavatar-2.json",
  "start_time": "00:00:00.000",
  "range_sec": {
    "description": "Relative seconds from start_time. Takes precedence over range_timestamp.",
    "begin": 65,
    "end": 100
  },
  "range_timestamp": {
    "begin": "00:01:05.000",
    "end": "00:01:40.000"
  },
  "speed": 1.0
}
```

---

## How to Execute

Start the replay feature with the following command.
`hakopy`'s `conductor_start()` is called, and the replay is executed in manual timing mode.

```bash
# Execute from the project root directory
python3 -m replay.hako_asset_replayer --replay config/replay/replay.json
```

### Command Line Arguments
- `--replay` (required): Path to the `replay.json` file.
- `--delta-time-msec`: Time interval for writing PDUs (in milliseconds). Default is `3`.
- `--asset-name`: Asset name to register with Hakoniwa. Default is `AssetReplayer`.
- `--quiet`: Suppresses detailed log output.
