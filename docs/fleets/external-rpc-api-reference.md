# external_rpc API Reference

この文書は `drone_api/external_rpc` の主要 API を簡潔にまとめる。

`external_rpc` 全体の見方としては、

- 機体数
- 実行方式（同期 / 非同期 shared runtime）
- 実行コンテキスト（external / asset）

の 3 軸で整理すると分かりやすい。詳細な対応表は
[external_rpc README](../../drone_api/external_rpc/README.md)
を参照。

## 1. `HakoniwaRpcDroneClient`

定義:

- [hakosim_rpc.py](../../drone_api/external_rpc/hakosim_rpc.py)

用途:

- 1 機を直接操作する同期 RPC client

主な constructor 引数:

- `drone_name`
- `service_config_path`
- `asset_name`
- `pdu_config_path`

主なメソッド:

- `set_ready()`
- `takeoff(alt_m)`
- `get_state()`
- `goto(x, y, z, yaw_deg=0.0, speed_m_s=1.0, tolerance_m=0.5, timeout_sec=30.0)`
- `land()`

## 2. `FleetRpcController`

定義:

- [fleet_rpc.py](../../drone_api/external_rpc/fleet_rpc.py)

用途:

- 複数機をまとめて扱う controller

主な constructor 引数:

- `drone_names`
- `service_config_path`
- `max_workers`
- `monitor_interval_sec`
- `use_async_shared`

注意:

- `use_async_shared` のデフォルトは `False`
- これは後方互換のためであり、複数機の新規利用では `True` を推奨する
- `False` の場合、内部実装は同期 RPC をスレッド並列するファサードになる
- `True` の場合、shared runtime ベースの複数機実装になる

主なメソッド:

- `set_ready(drone_name)`
- `takeoff(drone_name, alt_m)`
- `goto(drone_name, x, y, z, yaw_deg=0.0, speed_m_s=1.0, tolerance_m=0.5, timeout_sec=30.0)`
- `land(drone_name)`
- `get_state(drone_name)`
- `set_ready_async(drone_name)`
- `takeoff_async(drone_name, alt_m)`
- `goto_async(drone_name, x, y, z, ...)`
- `land_async(drone_name)`
- `get_state_async(drone_name)`
- `wait_for_all(futures, timeout_sec=None, return_exceptions=False)`
- `start_monitoring()`
- `stop_monitoring()`
- `get_latest_state(drone_name)`

## 3. `DroneStateSnapshot`

定義:

- [fleet_rpc.py](../../drone_api/external_rpc/fleet_rpc.py)

主な項目:

- `drone_name`
- `ok`
- `is_ready`
- `mode`
- `message`
- `x`, `y`, `z`
- `roll_deg`, `pitch_deg`, `yaw_deg`

## 4. service 名

この client 群が前提とする service 名は次である。

- `DroneService/DroneSetReady/<DroneName>`
- `DroneService/DroneTakeOff/<DroneName>`
- `DroneService/DroneGetState/<DroneName>`
- `DroneService/DroneGoTo/<DroneName>`
- `DroneService/DroneLand/<DroneName>`

## 5. 関連資料

- [external_rpc README](../../drone_api/external_rpc/README.md)
- [external_rpc tutorial](external-rpc-tutorial.md)
- [MuJoCo Runtime Generation](mujoco-runtime-generation.md)
