# external_rpc

`external_rpc` は、Hakoniwa drone service を Python から操作するための RPC client 群です。

主な利用対象は次の 2 つです。

- 1 機を直接操作する
  - `HakoniwaRpcDroneClient`
- 複数機をまとめて扱う
  - `FleetRpcController`

## 3 軸の整理

`external_rpc` は、次の 3 軸で整理すると見通しがよい。

1. 機体数
   - 単機
   - 複数機
2. 実行方式
   - 同期
   - 非同期 shared runtime
3. 実行コンテキスト
   - external
   - asset

対応関係は次のとおりである。

| 機体数 | 実行方式 | 実行コンテキスト | 実体 |
|---|---|---|---|
| 単機 | 同期 | external | `hakosim_rpc.py` / `HakoniwaRpcDroneClient` |
| 単機 | 非同期 shared runtime | external | `hakosim_async_shared_rpc.py` / `AsyncSharedHakoniwaRpcDroneClient` |
| 単機 | 非同期 shared runtime | asset | `hakosim_async_shared_asset_rpc.py` / `AssetAsyncSharedHakoniwaRpcDroneClient` |
| 複数機 | 同期 | external | `fleet_rpc.py` / `FleetRpcController(use_async_shared=False)` |
| 複数機 | 非同期 shared runtime | external | `fleet_rpc_async_shared.py` / `FleetRpcController(use_async_shared=True)` |
| 複数機 | 非同期 shared runtime | asset | `apps/show_asset_runner.py` / `AssetAsyncSharedFleet` |

### どれを使えばよいか

- 普通に 1 機を触る:
  - `HakoniwaRpcDroneClient`
- 普通に複数機を触る:
  - `FleetRpcController(..., use_async_shared=True)`
- 台数が多く、client 登録コストを下げたい:
  - `FleetRpcController(..., use_async_shared=True)`
- 箱庭時刻に同期する asset として動かしたい:
  - `apps/show_asset_runner.py`

### `use_async_shared` について

- `FleetRpcController` の `use_async_shared` のデフォルトは `False`
- これは後方互換のためであり、推奨値ではない
- `use_async_shared=False` の場合、内部実装は同期 RPC を `ThreadPoolExecutor` で並列実行する
- 1 process / 1 thread に近い軽量な複数機制御を行いたい場合は、`use_async_shared=True` を使う
- 新規の複数機サンプルや MuJoCo 利用では、原則として `use_async_shared=True` を推奨する

## 前提

この Python client が前提とするもの:

- 箱庭側で drone service が起動済みであること
- fleet config 側で `serviceConfigPath` が設定されていること
- type config 側で RPC service が有効になっていること
- Python 環境で `hakoniwa_pdu` を import できること

代表的な service は次の 5 つです。

- `DroneSetReady`
- `DroneTakeOff`
- `DroneGetState`
- `DroneGoTo`
- `DroneLand`

典型的な呼び出し順は次のとおりです。

1. `SetReady`
2. `TakeOff`
3. `GetState`
4. `GoTo`
5. `Land`

## 主な構成

1. [hakosim_rpc.py](hakosim_rpc.py)
   - `HakoniwaRpcDroneClient`
   - 1 機を直接操作する同期 client
2. [fleet_rpc.py](fleet_rpc.py)
   - `FleetRpcController`
   - 複数機をまとめて扱う controller
   - `ThreadPoolExecutor` で複数機へ同時投入できる
   - `GetState` の定期監視と latest state 保持を行える
3. [hakosim_async_shared_rpc.py](hakosim_async_shared_rpc.py)
   - shared runtime を使う試験実装
   - `AsyncSharedHakoniwaRpcDroneClient`
4. [hakosim_async_shared_asset_rpc.py](hakosim_async_shared_asset_rpc.py)
   - asset 版 shared runtime client
   - `AssetAsyncSharedHakoniwaRpcDroneClient`
5. `obsolete/*.py`
   - 単一 command を送る thin wrapper
6. [samples/multi_goto_demo.py](samples/multi_goto_demo.py)
   - fleet controller の最小利用例
7. `apps/*.py`, `apps/*.bash`
   - show / mission 系の実行アプリ

## 最小 API

### `HakoniwaRpcDroneClient`

主なメソッド:

- `set_ready()`
- `takeoff(alt_m)`
- `get_state()`
- `get_status()`
- `goto(x, y, z, yaw_deg=0.0, speed_m_s=1.0, tolerance_m=0.5, timeout_sec=30.0)`
- `land()`

### `FleetRpcController`

主なメソッド:

- `set_ready(drone_name)`
- `takeoff(drone_name, alt_m)`
- `goto(drone_name, x, y, z, yaw_deg=0.0, speed_m_s=1.0, tolerance_m=0.5, timeout_sec=30.0)`
- `land(drone_name)`
- `land_async(drone_name, timeout_sec=0.0)`
- `get_state(drone_name)`
- `get_status(drone_name)`
- `*_async(...)`
- `start_monitoring()`
- `get_latest_state(drone_name)`
- `wait_for_all(futures, timeout_sec=...)`

## まず読むべき文書

- MuJoCo 2 機を最短で通す:
  - [MuJoCo external_rpc Quickstart](../../docs/fleets/mujoco-external-rpc-quickstart.md)
- 1 機 / 2 機の最小手順:
  - [external-rpc tutorial](../../docs/fleets/external-rpc-tutorial.md)
- API 一覧:
  - [external-rpc API reference](../../docs/fleets/external-rpc-api-reference.md)
- MuJoCo runtime 生成:
  - [MuJoCo Runtime Generation](../../docs/fleets/mujoco-runtime-generation.md)

## 単体 command の実行例

```bash
python3 drone_api/external_rpc/obsolete/set_ready_client.py
python3 drone_api/external_rpc/obsolete/takeoff_client.py
python3 drone_api/external_rpc/obsolete/get_state_client.py
python3 drone_api/external_rpc/obsolete/goto_client.py 1.0 0.0 3.0
python3 drone_api/external_rpc/obsolete/land_client.py
```

明示的に service config と drone 名を渡す例:

```bash
python3 drone_api/external_rpc/obsolete/set_ready_client.py config/drone/fleets/services/api-1-service.json Drone
python3 drone_api/external_rpc/obsolete/takeoff_client.py config/drone/fleets/services/api-1-service.json Drone 3.0
python3 drone_api/external_rpc/obsolete/get_state_client.py config/drone/fleets/services/api-1-service.json Drone
python3 drone_api/external_rpc/obsolete/goto_client.py --service-config config/drone/fleets/services/api-1-service.json --drone Drone 3.0 0.0 3.0 45.0
python3 drone_api/external_rpc/obsolete/land_client.py config/drone/fleets/services/api-1-service.json Drone
```

## 複数機の最小例

```bash
python3 drone_api/external_rpc/samples/multi_goto_demo.py --drones DroneA DroneB --x 1.0 --y 0.0 --z 3.0
```

mission script の例:

```bash
bash drone_api/external_rpc/apps/run_single_mission.bash
bash drone_api/external_rpc/apps/run_single_mission.bash --drone Drone --alt 3.0 --x 2.0 --y 1.0 --z 0.1 --yaw -45.0
bash drone_api/external_rpc/apps/run_single_mission.bash --drone-count 10 --alt 0.8 --x 3.0 --y 0.0 --z 0.2 --yaw 0
bash drone_api/external_rpc/apps/run_single_mission.bash --drones Drone-1,Drone-2,Drone-3 --alt 0.8 --x 3.0 --y 0.0 --z 0.2 --yaw 0
```

```bash
bash drone_api/external_rpc/apps/run_square_mission.bash --drone Drone --side 4.0 --z 0.5
bash drone_api/external_rpc/apps/run_square_mission.bash --drone-count 10 --side 4.0 --z 0.5
bash drone_api/external_rpc/apps/run_square_mission.bash --drones Drone-1,Drone-2,Drone-3 --side 4.0 --z 0.5
```

## ドローンショー関連

- 実行入口:
  - [apps/run_show.bash](apps/run_show.bash) -> [apps/show_runner.py](apps/show_runner.py)
  - [apps/run_show_asset.bash](apps/run_show_asset.bash) -> [apps/show_asset_runner.py](apps/show_asset_runner.py)
- 設計:
  - [docs/fleets/drone-show-design.md](../../docs/fleets/drone-show-design.md)
- 実行手順:
  - [docs/fleets/drone-show-runbook.md](../../docs/fleets/drone-show-runbook.md)

代表例:

```bash
bash drone_api/external_rpc/apps/run_show.bash --show-json config/drone-show-config/show-h-a-100-ref.json --drone-count 100
bash drone_api/external_rpc/apps/run_show_asset.bash --show-json config/drone-show-config/show-h-a-100-ref.json --drone-count 100
bash drone_api/external_rpc/apps/run_show_scale_bench.bash 100 4
```

## MuJoCo 2 機の最小サンプル

`api-current-service.json` などで `Drone-1` / `Drone-2` が起動していれば、次で 2 機同時制御を確認できる。

```bash
python3 drone_api/external_rpc/samples/mujoco_two_drone_demo.py
```

このサンプルは、あえて汎用化せずに次だけをそのまま書いている。

1. `set_ready_async()` を 2 回呼ぶ
2. `wait_for_all()` で待つ
3. `takeoff_async()` を 2 回呼ぶ
4. `wait_for_all()` で待つ
5. `goto_async()` を 2 回呼ぶ
6. `wait_for_all()` で待つ
7. `land_async()` を 2 回呼ぶ
8. `wait_for_all()` で待つ

API の最小利用例として読むためのサンプルである。

## 衝突結果の読み方

`GetState` の RPC 応答には衝突情報は含まれない。
衝突回数を見たい場合は `status` PDU を読む。

```python
from fleet_rpc import FleetRpcController

with FleetRpcController(["Drone-1", "Drone-2"]) as fleet:
    status1 = fleet.get_status("Drone-1")
    status2 = fleet.get_status("Drone-2")
    print(status1.collided_counts, status2.collided_counts)
```

`get_status()` は `hako_msgs/DroneStatus` を返す。
典型的には `collided_counts` を見る。

`land_async()` / `land()` には `timeout_sec` を付けられる。
`timeout_sec > 0` の場合、`DroneLand` RPC の timeout として扱われ、時間内に応答しなければ `TimeoutError` になる。

## 補足

- `GetState` の返却本体は quaternion を含むが、client 側では angle(deg) にも直して扱う
- `GoTo` / `GetState` の座標は、この client では ROS 由来の表現を前提にしている
- 複数機同時制御の入口は `HakoniwaRpcDroneClient` より `FleetRpcController` を想定している
- `use_async_shared=True` では shared runtime を使うため、client registration の固定コストを減らせる

profiling 用環境変数:

- `HAKO_RPC_PROFILE_PREPARE=1`
- `HAKO_PROFILE_SERVICE_CLIENT=1`
