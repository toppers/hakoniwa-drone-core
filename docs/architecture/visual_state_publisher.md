# DroneVisualStatePublisher 内部設計メモ

## 目的

`DroneVisualStatePublisher` は、箱庭ドローンシミュレータが出力している複数機体分の PDU を読み取り、
可視化専用の `hako_msgs/DroneVisualStateArray` に変換して SHM に書き出す箱庭アセットである。

このドキュメントでは、外部仕様ではなく、実装時に必要となる内部責務と処理フローを整理する。

## 前提

1. 入出力は endpoint config で管理する
2. endpoint config の中で compact `pdudef` を参照する
3. この repo で担当するのは SHM への書き込みまで
4. bridge / WebSocket / browser 側は別プロジェクト
5. Phase 1 では `input_pdudef` / `asset_pdudef` ともに compact 形式のみを対象とする

## 責務分離

### 箱庭ドローン本体

- 各機体の既存 PDU を出力する
- 可視化専用の集約ロジックは持たない

### DroneVisualStatePublisher

- 入力 PDU から複数機体分の state を読み取る
- `DroneVisualState` 配列へ変換する
- `DroneVisualStateArray` として chunk 化する
- SHM/PDU へ publish する

## 内部構造の考え方

最小構成として、以下の責務で分ける。

1. 設定ローダ
   - `asset_name`
   - `input_endpoint_config`
   - `output_endpoint_config`
   - `delta_time_usec`
   - `publish_interval_msec`
   - `max_drones_per_packet`
   - `pwm_duty_count`
   - endpoint config から参照される `input_pdudef` / `asset_pdudef`
   - runtime `input endpoint config`
   - runtime `output endpoint config`
2. 入力 reader
   - 各機体の position / attitude / pwm_duty を読む
   - `pwm_duty` は `motor.controls` の先頭 `pwm_duty_count` 個のみを使う
3. snapshot builder
   - `std::vector<DroneVisualState>` を組み立てる
4. chunk builder
   - `DroneVisualStateArray` へ分割する
5. publisher
   - chunk を SHM に書く

runtime では endpoint config の中にある `pdu_def_path` を読み取り、
input 側は `input_pdudef`、output 側は `asset_pdudef` をそのまま使う。
さらに、dry-run や callback 切替の都合に合わせて runtime 用 endpoint config を生成して使う。
`merged pdudef` は使わない。

Phase 1 では、たとえば次のような配置を想定する。

- 設定 JSON
  - `config/assets/visual_state_publisher/visual_state_publisher.json`
- runtime input endpoint config
  - `config/assets/visual_state_publisher/DroneVisualStatePublisher-input-endpoint.json`
- runtime output endpoint config
  - `config/assets/visual_state_publisher/DroneVisualStatePublisher-output-endpoint.json`

legacy `pdudef` への互換処理は、この asset では持たない。
compact 前提で実装を単純化する。

Phase 1 では class を増やしすぎず、1 asset 実装内の helper 関数として持ってよい。

## 入力データ

入力として最低限必要なのは次の 3 つ。

1. 位置
2. 姿勢
3. PWM duty

どの PDU 名 / channel から取るかは既存のドローン出力定義から確定する。

Phase 1 では、入力元の探索ロジックを asset 側に閉じ込め、ドローン本体へ変更は入れない。

入力探索結果は、少なくとも次の binding 配列として保持する想定である。

1. `drone_name`
2. `pos_channel_id`
3. `motor_channel_id`

asset はこの binding 配列を上から順に走査して snapshot を組み立てる。
Phase 1 の入力は、既存の単機体 `pdudef` では
- `pos_channel_id = 1`
- `motor_channel_id = 0`
の組を使う。

## 出力データ

出力は `hako_msgs/DroneVisualStateArray` で固定する。

1. `sequence_id`
   - 1 publish ごとにインクリメント
2. `chunk_index`
   - 0 始まり
3. `chunk_count`
   - 全 chunk 数
4. `start_index`
   - 全体配列における chunk 先頭の機体 index
5. `valid_count`
   - この chunk の有効件数
6. `drones`
   - `DroneVisualState[]`

## chunk 分割

分割単位は `max_drones_per_packet` とする。

例:

- 全体機体数: 100
- `max_drones_per_packet = 32`
- `pwm_duty_count = 4`

この場合:

- chunk 0: `start_index = 0`, `valid_count = 32`
- chunk 1: `start_index = 32`, `valid_count = 32`
- chunk 2: `start_index = 64`, `valid_count = 32`
- chunk 3: `start_index = 96`, `valid_count = 4`

`chunk_count = 4`

出力 chunk は 1 robot に複数 channel を持たせる。

例:

- `DroneVisualStatePublisher`

Phase 1 では、1 つの robot 名 `DroneVisualStatePublisher` に対して、
chunk ごとに別 channel を割り当てる。
例:

- `channel_id = 0`, `name = drone_visual_state_array_0`
- `channel_id = 1`, `name = drone_visual_state_array_1`
- `channel_id = 2`, `name = drone_visual_state_array_2`

起動時に必要 chunk 数を計算し、`asset_pdudef` 側の channel 数が不足していたらエラーにする。
この不足チェックは runtime で行い、運用で `asset_pdudef` の channel 数を十分に確保する前提とする。

## publish タイミング

asset 自体の step は `delta_time_usec` で進む。

publish は毎 step ではなく、`publish_interval_msec` に従って行う。

考え方:

- `delta_time_usec`
  - asset の update 周期
- `publish_interval_msec`
  - 可視化データの publish 周期

この2つを分けることで、内部更新と可視化更新を独立に調整できる。

## 処理フロー

1. asset 起動時に設定 JSON を読む
2. endpoint config から `input_pdudef` と `asset_pdudef` を特定する
3. runtime `input endpoint config` / runtime `output endpoint config` を生成する
4. runtime endpoint config を使って endpoint を初期化する
5. `input_pdudef` / `asset_pdudef` から binding を構築する
6. 毎 step:
   - 入力 PDU から全機体分の state を読む
   - `DroneVisualState[]` を組み立てる
   - publish 周期に達していなければ終了
   - `max_drones_per_packet` ごとに chunk 分割する
   - `DroneVisualStateArray` を SHM に書く

## sequence_id の扱い

`sequence_id` は publish 単位で 1 回だけ増やす。

同じ snapshot を構成する全 chunk は同じ `sequence_id` を共有する。

## 内部実装方針

Phase 1 は次の方針で十分。

1. 1 asset = 1 publisher instance
2. 1 publish = 1 snapshot
3. drone 順序は `input_pdudef` で確定している順序を使う
4. エラー時は publish をスキップして継続する

## 単体テスト方針

Phase 1 では、箱庭本体や SHM に依存しないように internal cache endpoint を使って確認する。

1. input endpoint に `pos` / `motor` を書く
2. `run()` を 1 回まわす
3. output endpoint から `DroneVisualStateArray` を読む
4. 変換結果と chunk 化結果を検証する

この方針により、PDU I/O の transport と変換ロジックを分離して確認できる。

## 箱庭なし版

優先度は低い。

Phase 1 では箱庭あり版を主系とし、箱庭なし版は考慮しない。

## ファイル配置について

本ドキュメントでは責務と処理フローを主に扱う。

設定 JSON や `pdudef` の最終的な配置場所は、Phase 1 の実装後半で再整理する。
したがって、ここでのファイル配置イメージは暫定であり、内部設計そのものとは切り分けて考える。

## 実装開始時の最小目標

1. 1 機体の `DroneVisualStateArray` を 1 chunk で出す
2. internal cache endpoint を使った単体テストを通す
3. その後複数機体へ拡張する
4. 最後に chunk 分割を有効化する
