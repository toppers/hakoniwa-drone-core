# external_rpc

`hakoniwa-pdu-python` の `ShmPduServiceClientManager + ProtocolClientImmediate` を使う external service client です。

共通処理は [hakosim_rpc.py](hakosim_rpc.py) の `HakoniwaRpcDroneClient` に集約しています。各 script は thin wrapper です。

複数機体を同時に扱うための最小 controller:

- [fleet_rpc.py](fleet_rpc.py)
  - `FleetRpcController`
  - `1 drone = 1 client instance`
  - `ThreadPoolExecutor` で deferred command を非同期投入
  - `GetState` の定期監視と latest state 保持

最小 demo:

- [multi_goto_demo.py](multi_goto_demo.py)
  - `goto_async()` を複数機体へ投入
  - `latest_state` を監視表示

ドローンショー（formation JSON 駆動）:

- 実行入口: [run_show.bash](run_show.bash) -> [show_runner.py](show_runner.py)
- データ仕様/設計: [docs/fleets/drone-show-design.md](../../docs/fleets/drone-show-design.md)
- 実行手順（運用）: [docs/fleets/drone-show-runbook.md](../../docs/fleets/drone-show-runbook.md)

構成:

1. [hakosim_rpc.py](hakosim_rpc.py)
   - `HakoniwaRpcDroneClient`
   - `1 drone = 1 client instance`
   - `SetReady` / `TakeOff` / `GetState` / `GoTo` / `Land`
2. [fleet_rpc.py](fleet_rpc.py)
   - `FleetRpcController`
   - `drone_name -> HakoniwaRpcDroneClient`
   - deferred command を `Future` で非同期実行
   - `GetState` の監視結果を `latest_state` として保持
3. 各 `*_client.py`
   - 単一 command 用の thin wrapper
4. [multi_goto_demo.py](multi_goto_demo.py)
   - fleet controller の最小利用例

最初の確認対象:

- `DroneSetReady`
- `DroneTakeOff`
- `DroneGetState`
- `DroneGoTo`
- `DroneLand`

実行例:

```bash
python3 drone_api/external_rpc/set_ready_client.py
python3 drone_api/external_rpc/takeoff_client.py
python3 drone_api/external_rpc/get_state_client.py
python3 drone_api/external_rpc/goto_client.py 1.0 0.0 3.0
python3 drone_api/external_rpc/land_client.py
python3 drone_api/external_rpc/set_ready_client.py config/drone/fleets/services/api-1-service.json Drone
python3 drone_api/external_rpc/takeoff_client.py config/drone/fleets/services/api-1-service.json Drone 3.0
python3 drone_api/external_rpc/get_state_client.py config/drone/fleets/services/api-1-service.json Drone
python3 drone_api/external_rpc/goto_client.py --service-config config/drone/fleets/services/api-1-service.json --drone Drone 3.0 0.0 3.0 45.0
python3 drone_api/external_rpc/land_client.py config/drone/fleets/services/api-1-service.json Drone
python3 drone_api/external_rpc/multi_goto_demo.py --drones DroneA DroneB --x 1.0 --y 0.0 --z 3.0
bash drone_api/external_rpc/run_single_mission.bash
bash drone_api/external_rpc/run_single_mission.bash --drone Drone --alt 3.0 --x 2.0 --y 1.0 --z 0.1 --yaw -45.0
bash drone_api/external_rpc/run_single_mission.bash --drone-count 10 --alt 0.8 --x 3.0 --y 0.0 --z 0.2 --yaw 0
bash drone_api/external_rpc/run_single_mission.bash --drones Drone-1,Drone-2,Drone-3 --alt 0.8 --x 3.0 --y 0.0 --z 0.2 --yaw 0
bash drone_api/external_rpc/run_square_mission.bash --drone Drone --side 4.0 --z 0.5
bash drone_api/external_rpc/run_square_mission.bash --drone-count 10 --side 4.0 --z 0.5
bash drone_api/external_rpc/run_square_mission.bash --drones Drone-1,Drone-2,Drone-3 --side 4.0 --z 0.5
bash drone_api/external_rpc/run_show.bash --show-json config/drone-show-config/show-h-a-100-ref.json --drone-count 100
bash drone_api/external_rpc/run_show.bash --show-json config/drone-show-config/show-hello-world-100-ref.json --drone-count 100
```

引数:

1. `service_config_path` は省略可
2. `drone_name` は省略可
3. `takeoff_client.py` は `alt_m` を省略可
4. `goto_client.py` は通常 `x y z [yaw]` のみ指定すればよい
5. `goto_client.py` の追加オプション:
   - `--service-config`
   - `--drone`
   - `--speed`
   - `--tolerance`
   - `--timeout-sec`
6. `run_single_mission.bash` の追加オプション:
   - `--service-config`
   - `--drone`
   - `--drone-count`（`Drone-1..N` を自動生成）
   - `--drones`（`,` 区切り。指定時は複数機体同時実行）
   - `--alt`
   - `--x`
   - `--y`
   - `--z`
   - `--yaw`
   - `--speed`
   - `--tolerance`
   - `--timeout-sec`
   - `--land`
   - `--serial`（複数機体時に直列実行へ切り替え）
7. `run_square_mission.bash` の追加オプション:
   - `--service-config`
   - `--drone`
   - `--drone-count`（`Drone-1..N` を自動生成）
   - `--drones`（`,` 区切り。指定時は複数機体同時実行）
   - `--alt`
   - `--center-x`
   - `--center-y`
   - `--side`
   - `--z`
   - `--layer-size`（何機体ごとに高度レイヤを切るか。既定: `8`）
   - `--layer-step`（レイヤごとの高度加算[m]。既定: `1.0`）
   - `--phase-step`（機体インデックスごとの waypoint 位相ずらし。既定: `0`）
   - `--speed`
   - `--tolerance`
   - `--timeout-sec`
   - `--yaw`
   - `--land`（最後に着陸）
   - `--serial`（複数機体時に直列実行へ切り替え）
8. `run_show.bash` の追加オプション:
   - `--service-config`
   - `--show-json`
   - `--show-config`（`--show-json` の alias）
   - `--drone-count`（`Drone-1..N` を自動生成）
   - `--drones`（`,` 区切り）
   - `--assign-mode`（`index|nearest`）
   - `--takeoff-alt`
   - `--speed`
   - `--tolerance`
   - `--timeout-sec`
   - `--batch-size`
   - `--batch-init`
   - `--batch-goto`
   - `--batch-land`
   - `--init-retry-max`
   - `--init-retry-interval-sec`
   - `--ready-gate-timeout-sec`
   - `--ready-gate-interval-sec`
   - `--ready-gate-call-timeout-sec`
   - `--no-ready-gate`
   - `--proc-count`
   - `--init-concurrency-per-proc`
   - `--land`
   - `--serial`

前提:

- 箱庭側で `api-1` の service が起動済みであること
- fleet file 側で `serviceConfigPath` が設定され、type 側で `controller.serviceMode = "rpc"` が設定されていること
- Python 環境で `hakoniwa_pdu` が import できること
- `TakeOff` の前に `SetReady` を実行すること
- `GoTo` の前に `SetReady` と `TakeOff` を実行すること
- `Land` の前に `SetReady` と `TakeOff` を実行すること

補足:

- 返却される `GetState` 本体は quaternion だが、client 側では angle(deg) も表示する
- ROS 座標系で request を与える前提
  - `GoTo` の `x y z yaw`
  - `GetState` の `position` / `angle_deg`
- deferred command は blocking call だが、`FleetRpcController` では `ThreadPoolExecutor` を使って複数機体へ同時投入できる
- 100台同時制御の入口は `HakoniwaRpcDroneClient` ではなく `FleetRpcController` を想定している
