# fleets 実行時コンフィグ構成（どれを使うか）

このページは、fleets 実行時に各コンポーネントが参照する設定ファイルを整理したものです。

## 全体像

`tools/launch-fleets-scale-perf.bash <N>` 実行時の流れ:

1. `tools/gen_fleet_scale_config.py` が `*-current.json` を生成
2. launcher が drone service / visual_state_publisher / bridge / viewer web を起動
3. browser は `viewer-config-fleets.json` を読み、WS 経由で state を受信

## 生成される current 系（N依存）

- `config/drone/fleets/api-current.json`
  - drone service が読む fleet instance
- `config/pdudef/drone-pdudef-current.json`
  - drone service の sim入力 pdudef
- `config/drone/fleets/services/api-current-service.json`
  - external_rpc（Python制御）の service 定義
  - `api-current.json` の `serviceConfigPath` でも参照

## launcher が直接参照するファイル

- `config/launcher/fleets-scale-perf.launch.json`
  - 起動定義の本体
- `config/drone/fleets/api-current.json`
  - drone service 引数
- `config/pdudef/drone-pdudef-current.json`
  - drone service 引数
- `config/assets/visual_state_publisher/visual_state_publisher.json`
  - visual_state_publisher 引数
- `work/hakoniwa-pdu-bridge-core/config/web_bridge_fleets/*`
  - bridge の `--config-root` 配下設定
- `work/hakoniwa-threejs-drone`（または `HAKO_THREEJS_VIEWER_PATH`）
  - viewer web の配信ルート

## visual_state_publisher が参照する主設定

- `config/assets/visual_state_publisher/visual_state_publisher.json`
  - endpoint 設定、publish interval、`max_drones_per_packet`
- `config/assets/visual_state_publisher/endpoints/input_shm.json`
  - `pdu_def_path` として `drone-pdudef-current.json` を参照
- `config/pdudef/drone-visual-state.json`
  - 出力側 pdudef
- `config/pdudef/drone-visual-state-pdutypes.json`
  - 出力 pdutypes（`drone_visual_state_array_0.pdu_size` は N依存で更新）

## bridge が参照する主設定（config-root=web_bridge_fleets）

- `bridge/bridge.json`
  - 転送ポリシー、ticker、入出力定義
- `comm/visual-state-shm-callback.json`
  - input callback（現行は 1チャネル）
- `pdu/drone-visual-state-pdutypes.json`
  - bridge 側の pdutypes
- `work/hakoniwa-threejs-drone/config/pdudef-fleets-pdutypes.json`
  - viewer 側の pdutypes（`pdu_size` を bridge/publisher と一致させる）

## browser/viewer が参照する設定

- URL パラメータ:
  - `viewerConfigPath=/config/viewer-config-fleets.json`
  - `wsUri=ws://<SIM_IP>:8765`
  - `dynamicSpawn=true`
  - `templateDroneIndex=0`
  - `maxDynamicDrones=<N>`
- `config/viewer-config-fleets.json`
  - scene/pdu/stateInput/ui 設定
- `config/drone_config-compact-1.json`
  - fleets 描画テンプレート（dynamicSpawn で N展開）

## Python external_rpc が参照する設定

- 既定:
  - `config/drone/fleets/services/api-current-service.json`
- 実行スクリプト:
  - `drone_api/external_rpc/apps/run_single_mission.bash`
  - `drone_api/external_rpc/apps/run_square_mission.bash`
- 詳細:
  - `drone_api/external_rpc/README.md`
- tutorial:
  - `docs/fleets/external-rpc-tutorial.md`

MuJoCo 用 runtime の具体的な生成手順は次を参照:

- [MuJoCo Runtime Generation](mujoco-runtime-generation.md)

## 迷ったときの基準

- N依存で変える: `*-current.json`（fleet / pdudef / service）
- 固定で使う: launcher, viewer-config-fleets（値はN依存）
- 値を揃える: visual-state-pdutypes の `pdu_size`（publisher/bridge/viewer）
- 接続先だけ変える: browser URL の `wsUri`
