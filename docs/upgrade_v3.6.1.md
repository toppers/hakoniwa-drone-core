# Hakoniwa Drone Simulator v3.6.0 → v3.6.1 アップデート手順

## はじめに

Hakoniwa Drone Simulator v3.6.1 では、v3.6.0 で導入した fleets（100台+同時シミュレーション）基盤をさらに実用化し、
以下を強化しています。

- Python service 制御の初期化コスト削減
- `show_asset_runner` による箱庭アセット実行
- `DroneVisualStatePublisher` の分散可視化対応
- Hakoniwa Conductor(simple) を使った server/client 分散可視化
- 配布バイナリへの `DroneVisualStatePublisher` 同梱

本ドキュメントでは、v3.6.0 から v3.6.1 へ更新する際の変更点と確認項目を説明します。

## v3.6.1 の新機能・変更点

今回のバージョンアップの中心は、**大規模 fleets の実運用導線の強化**です。

- Python fleets 制御の高速化
  - `async_shared` RPC runtime を追加
  - Python 側の service registration 固定コストを削減
  - `show_runner --use-async-shared` を追加
- 箱庭アセットとしての drone show 実行
  - `drone_api/external_rpc/show_asset_runner.py`
  - `drone_api/external_rpc/run_show_asset.bash`
  - launcher から `show-asset-runner` を起動可能に
- `DroneVisualStatePublisher` の機能拡張
  - `global_drone_count`
  - `global_start_index`
  - `local_start_index`
  - `local_drone_count`
  - `output_chunk_base_index`
  - `max_drones_per_packet`
  - `sequence_id == 0` の初期 packet 出力
- three.js 可視化の安全化
  - `sequence_id == 0` を無効 packet として無視
  - invalid packet / index 範囲外 / `NaN` / `inf` を無視
  - packed visual state `_0 / _1 / ...` の複数 source を前提に改善
- bridge / PDU 定義の拡張
  - `drone_visual_state_array_1` を追加
  - `_0 / _1` の 2 チャネル配管に対応
- Conductor(simple) による分散可視化対応
  - `work/hakoniwa-conductor-pro/eu-config/eu-input.fleets.json`
  - `generated-fleets/`
  - server/client の launcher 運用を追加
- binary 配布の改善
  - `DroneVisualStatePublisher` を `mac/`, `lnx/`, `win/` 配下の配布バイナリへ追加
  - launcher は既定で配布済み VSP バイナリを使うように変更

## 前提とする環境

- 検証環境:
  - macOS (Apple Silicon)
  - Windows 11 / WSL2 Ubuntu
- 箱庭ドローンシミュレータのアーキテクチャパターン:
  - 共有メモリパターン
  - fleets 構成
  - 必要に応じて Conductor(simple) 分散構成

## アップデート対象リポジトリ

- hakoniwa-drone-core
  - target version: v3.6.1

既存のローカル変更がある場合は先に退避してください。

`hakoniwa-drone-core` 配下で以下を実行します。

```bash
git fetch --tags
git checkout v3.6.1
git submodule update --init --recursive
```

> `main` を使う運用の場合は `git pull origin main` でも可。

## 関連リポジトリ（fleets / 分散可視化運用時）

v3.6.1 では、以下の関連リポジトリも利用します。

- hakoniwa-core-pro
- hakoniwa-core-cpp
- hakoniwa-pdu-python
- hakoniwa-pdu-bridge-core
- hakoniwa-threejs-drone
- hakoniwa-conductor-pro

`work/` 配下運用、または環境変数での外部配置を前提とします。

## v3.6.1 で特に注意すべき互換ポイント

### 1. visual-state-publisher の設定項目が増えた

`config/assets/visual_state_publisher/visual_state_publisher.json` を独自管理している場合は、
以下の項目追加に追従してください。

- `global_drone_count`
- `global_start_index`
- `local_start_index`
- `local_drone_count`
- `output_chunk_base_index`
- `max_drones_per_packet`

特に分散可視化では、

- `local_start_index`: ローカル入力配列の読み取り開始位置
- `global_start_index`: 可視化上の global index 開始位置

を分けて扱う必要があります。

### 2. sequence_id=0 は未初期化 packet 扱い

`DroneVisualStatePublisher` は起動時に全 output chunk へ zero packet を書き込みます。
three.js 側では `sequence_id == 0` を無効 packet として無視します。

独自 viewer や bridge を使っている場合は、この前提に合わせてください。

### 3. fleets launcher は VSP 配布バイナリを既定で使う

`tools/launch-fleets-scale-perf.bash` は、既定で以下を使います。

- macOS: `mac/mac-drone_visual_state_publisher`
- Linux: `lnx/linux-drone_visual_state_publisher`

独自バイナリを使う場合のみ、`HAKO_VISUAL_STATE_PUBLISHER_BIN` を設定してください。

## 配布バイナリ運用時の変更点

v3.6.1 では、`DroneVisualStatePublisher` も配布バイナリに含まれます。

例:

- `mac/mac-main_hako_drone_service`
- `mac/mac-drone_visual_state_publisher`
- `lnx/linux-main_hako_drone_service`
- `lnx/linux-drone_visual_state_publisher`
- `win/win-main_hako_drone_service.exe`

source build の場合は、以下で package 出力まで行えます。

```bash
bash tools/build-mac.bash build
bash tools/build-ubuntu.bash build
pwsh tools/build-win.ps1
```

## Conductor(simple) 分散可視化での固定前提

v3.6.1 時点の運用前提は以下です。

- time transfer policy:
  - `atomic-immediate`
- conductor(simple):
  - `delta_time_usec = 10000`
  - `max_delay_time_usec = 20000`
- drone simulator asset:
  - `delta_time = 1ms`
- `DroneVisualStatePublisher`:
  - `delta_time_usec = 20000`
  - `publish_interval_msec = 20`

`atomic=false` や `throttle` は、現時点では `EBUSY` や時刻停止を起こすため採用しません。

## アップデート後の確認項目

### 1. fleets 単一ノード起動確認

```bash
bash tools/launch-fleets-scale-perf.bash 100
```

### 2. async_shared show 実行確認

```bash
PYTHONPATH=work/hakoniwa-pdu-python/src \
bash drone_api/external_rpc/run_show.bash \
  --show-config config/drone-show-config/show-hakoniwa-100-ref.json \
  --drone-count 100 \
  --assign-mode nearest \
  --proc-count 1 \
  --batch-init 100 \
  --batch-goto 100 \
  --speed 14.0 \
  --use-async-shared
```

### 3. show asset 実行確認

```bash
SHOW_ASSET_JSON=config/drone-show-config/show-hakoniwa-100-ref.json \
bash tools/launch-show-asset-scale-bench.bash --view 100 1
```

### 4. visual-state-publisher の global/local index 分離確認

```bash
ENABLE_WEB_BRIDGE=1 \
ENABLE_VIEWER_WEBSERVER=1 \
VISUAL_STATE_GLOBAL_DRONE_COUNT=100 \
VISUAL_STATE_GLOBAL_START_INDEX=50 \
VISUAL_STATE_LOCAL_START_INDEX=0 \
VISUAL_STATE_LOCAL_DRONE_COUNT=50 \
VISUAL_STATE_OUTPUT_CHUNK_BASE_INDEX=1 \
bash tools/launch-show-asset-scale-bench.bash --view 100 1
```

### 5. Conductor(simple) 分散起動確認

server 側:

```bash
bash tools/test-server.bash
```

client 側:

```bash
bash tools/test-client.bash
```

## v3.6.1 の成果サマリ

今回のリリースで、以下の実用導線が成立しました。

- `async_shared` による fleets Python 制御の高速化
- `show_asset_runner` による asset 実行
- single-PC 疑似分散可視化
- Conductor(simple) による server/client 分散可視化
- 2 ノード 512 + 512 = 1024 機体構成の実行確認

## 補足ドキュメント

- fleets ドキュメント索引:
  [docs/fleets/README.md](./fleets/README.md)
- 性能レポート:
  [docs/fleets/performance-report.md](./fleets/performance-report.md)
- DroneVisualStatePublisher 設計:
  [docs/architecture/visual_state_publisher.md](./architecture/visual_state_publisher.md)
- External RPC Driver:
  [drone_api/external_rpc/README.md](../drone_api/external_rpc/README.md)
