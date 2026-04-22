# external_rpc Tutorial

この文書は、Hakoniwa drone service を Python から操作する最短手順をまとめる。

対象:

- 1 機を動かしたい
- 2 機を自分の Python から動かしたい
- `HakoniwaRpcDroneClient` と `FleetRpcController` の入口だけ知りたい

## 1. 前提

事前に次が揃っていること。

- 箱庭側の drone service が起動している
- 対応する `service config` が存在する
- Python 環境で `hakoniwa_pdu` を import できる

MuJoCo を使う場合は、さらに次が揃っていること。

- fleet config
- MuJoCo XML
- service config
- pdudef

生成方法は次を参照:

- [MuJoCo Runtime Generation](mujoco-runtime-generation.md)

## 2. 1 機を動かす

### 2.1 既存 client script を使う

最小確認:

```bash
python3 drone_api/external_rpc/obsolete/set_ready_client.py
python3 drone_api/external_rpc/obsolete/takeoff_client.py
python3 drone_api/external_rpc/obsolete/get_state_client.py
python3 drone_api/external_rpc/obsolete/goto_client.py 1.0 0.0 3.0
python3 drone_api/external_rpc/obsolete/land_client.py
```

明示的に service config と drone 名を指定する場合:

```bash
python3 drone_api/external_rpc/obsolete/set_ready_client.py config/drone/fleets/services/api-1-service.json Drone
python3 drone_api/external_rpc/obsolete/takeoff_client.py config/drone/fleets/services/api-1-service.json Drone 3.0
python3 drone_api/external_rpc/obsolete/get_state_client.py config/drone/fleets/services/api-1-service.json Drone
python3 drone_api/external_rpc/obsolete/goto_client.py --service-config config/drone/fleets/services/api-1-service.json --drone Drone 3.0 0.0 3.0 45.0
python3 drone_api/external_rpc/obsolete/land_client.py config/drone/fleets/services/api-1-service.json Drone
```

### 2.2 Python から直接使う

```python
from drone_api.external_rpc.hakosim_rpc import HakoniwaRpcDroneClient

client = HakoniwaRpcDroneClient(
    drone_name="Drone",
    service_config_path="config/drone/fleets/services/api-1-service.json",
)

client.set_ready()
client.takeoff(3.0)
state = client.get_state()
client.goto(1.0, 0.0, 3.0, yaw_deg=0.0, speed_m_s=1.0)
client.land()
```

## 3. 2 機を動かす

複数機を扱う場合は `FleetRpcController` を使う。
新規の複数機利用では、`use_async_shared=True` を推奨する。
デフォルトの `False` は後方互換のための同期実装であり、内部では同期 RPC をスレッド並列しているだけである。

```python
from drone_api.external_rpc.fleet_rpc import FleetRpcController

with FleetRpcController(
    drone_names=["Drone-1", "Drone-2"],
    service_config_path="config/drone/fleets/services/api-mujoco-instance-2-service.json",
    use_async_shared=True,
) as fleet:
    fleet.set_ready("Drone-1")
    fleet.set_ready("Drone-2")
    fleet.takeoff("Drone-1", 1.5)
    fleet.takeoff("Drone-2", 1.5)
    fleet.goto("Drone-1", 1.0, 0.0, 1.5)
    fleet.goto("Drone-2", -1.0, 0.0, 1.5)
    state1 = fleet.get_state("Drone-1")
    state2 = fleet.get_state("Drone-2")
    fleet.land("Drone-1")
    fleet.land("Drone-2")
```

同時投入する場合:

```python
from drone_api.external_rpc.fleet_rpc import FleetRpcController

with FleetRpcController(
    drone_names=["Drone-1", "Drone-2"],
    service_config_path="config/drone/fleets/services/api-mujoco-instance-2-service.json",
    use_async_shared=True,
) as fleet:
    futures = [
        fleet.goto_async("Drone-1", 1.0, 0.0, 1.5),
        fleet.goto_async("Drone-2", -1.0, 0.0, 1.5),
    ]
    fleet.wait_for_all(futures, timeout_sec=35.0)
```

## 4. latest state を監視する

`FleetRpcController` は内部監視スレッドで latest state を保持できる。

```python
from drone_api.external_rpc.fleet_rpc import FleetRpcController

with FleetRpcController(
    drone_names=["Drone-1", "Drone-2"],
    service_config_path="config/drone/fleets/services/api-mujoco-instance-2-service.json",
) as fleet:
    fleet.start_monitoring()
    state = fleet.get_latest_state("Drone-1")
    fleet.stop_monitoring()
```

実行例:

```bash
python3 drone_api/external_rpc/samples/multi_goto_demo.py \
  --service-config config/drone/fleets/services/api-mujoco-instance-2-service.json \
  --drones Drone-1 Drone-2 \
  --x 1.0 --y 0.0 --z 1.5
```

## 5. よくある前提

- `TakeOff` の前に `SetReady` が必要
- `GoTo` の前に `SetReady` と `TakeOff` が必要
- `Land` の前に `SetReady` と `TakeOff` が必要
- `service config` 内の service 名は `DroneService/<Operation>/<DroneName>` で一致している必要がある

## 6. MuJoCo 2 機サンプルとの関係

MuJoCo の 2 機 runtime を作る場合は、まず次を生成する。

- fleet config
  - `config/drone/fleets/api-mujoco-instance-2.json`
- service config
  - `config/drone/fleets/services/api-mujoco-instance-2-service.json`
- pdudef
  - `config/pdudef/drone-pdudef-mujoco-instance-2.json`
- MuJoCo XML
  - `config/drone/mujoco-current/drone.xml`

その上で、この tutorial の `service_config_path` を `api-mujoco-instance-2-service.json` に合わせればよい。

## 7. MuJoCo 2 機の最小サンプル

次の script は `Drone-1` と `Drone-2` を同時に

1. `SetReady`
2. `TakeOff`
3. 左右対称位置へ `GoTo`
4. `GetState`
5. `Land`

する最小サンプルである。

```bash
python3 drone_api/external_rpc/samples/mujoco_two_drone_demo.py
```

このサンプルは API の使い方を見せることを優先して、あえて次をベタ書きしている。

- `fleet.set_ready_async("Drone-1")`
- `fleet.set_ready_async("Drone-2")`
- `fleet.wait_for_all(...)`
- `fleet.takeoff_async(...)`
- `fleet.goto_async(...)`
- `fleet.get_state(...)`
- `fleet.land_async(...)`

つまり、`Future` を返す API をどう使うかを最短距離で追える。
