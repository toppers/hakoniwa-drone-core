# fleets 機体数依存コンフィグ範囲（N依存整理）

## 目的

機体数 `N` を変更する際に、どの設定を生成/更新対象にするかを明確化する。

- 対象: fleets + compact
- 非対象: legacy

## 前提

- 命名規約: `Drone-<ID>`（`ID=1..N`）
- 現運用（N一般）: VisualState は 1チャネル固定
  - `drone_visual_state_array_0` のみ使用
  - `max_drones_per_packet = N`
  - `pdu_size = next_pow2(64 * N)` を推奨

## 生成対象（N依存）

1. Fleet instance
- `config/drone/fleets/api-current.json`
- 依存項目: `drones[]` 件数 / `name` / `position_meter` / `angle_degree`

2. Sim入力 pdudef（compact）
- `config/pdudef/drone-pdudef-current.json`
- 依存項目: `robots[]` 件数 / `name`

3. Service config（機体名展開）
- `config/drone/fleets/services/api-current-service.json`
- 依存項目: service 名の `Drone-<ID>` 展開

## 固定参照側（launcher/asset）

- launcher:
  - `config/launcher/fleets-scale-perf.launch.json`
  - `*-current.json` を固定参照
- visual_state_publisher:
  - input endpoint `pdu_def_path` は current pdudef を参照
  - callback 定義 (`input_shm_callback.json`, `output_shm_callback.json`) は現行N依存なし（`io.robots=[]`）

## N一般で原則固定の設定（値のみ更新）

- `config/pdudef/drone-visual-state-pdutypes.json`
- `config/pdudef/drone-visual-state.json`
- `config/assets/visual_state_publisher/visual_state_publisher.json`
  - `max_drones_per_packet = N` に更新
  - `publish_interval_msec` は 20 を推奨
- `config/pdudef/drone-visual-state-pdutypes.json`
  - `drone_visual_state_array_0.pdu_size` を `next_pow2(64 * N)` に更新
  - bridge/viewer 側の同名 pdutypes も同値に同期

## 生成ツール

- `tools/gen_fleet_scale_config.py`
  - 生成: fleet / pdudef / service current
  - レイアウト: `legacy-rings` / `packed-rings`

## バリデーション観点（最低限）

- `drones[].name` 重複なし
- fleet の `drones[].name` と pdudef の `robots[].name` が一致
- `drone_visual_state_array_0` が存在
- `drone_visual_state_array_0.pdu_size` が publisher/bridge/viewer で一致
- launcher が current 生成先を参照
