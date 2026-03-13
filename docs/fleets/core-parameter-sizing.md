# hakoniwa-core / bridge パラメータ設計（fleets）

## 対象

fleets 構成で機体数 `N` を増やすときに、`hakoniwa-core` と `bridge/publisher` の上限値をどう決めるかを示す。

## 対象パラメータ

### core-pro（コンパイル時）

- `HAKO_RECV_EVENT_MAX`
- `HAKO_SERVICE_CLIENT_MAX`
- `HAKO_SERVICE_MAX`
- `HAKO_PDU_CHANNEL_MAX`
- `HAKO_DATA_MAX_ASSET_NUM`

注記:

- ヘッダはマクロ定義だが、実運用では `build.bash/install.bash` の環境変数から `-D` 注入できる。
  - `ASSET_NUM`
  - `SERVICE_MAX`
  - `RECV_EVENT_MAX`
  - `SERVICE_CLIENT_MAX`
  - `CHANNEL_MAX`（`hakoniwa-core-cpp` 側、`HAKO_PDU_CHANNEL_MAX`）

### bridge/publisher（実行時）

- `config/assets/visual_state_publisher/visual_state_publisher.json`
  - `max_drones_per_packet`
  - `publish_interval_msec`
- `work/hakoniwa-pdu-bridge-core/config/web_bridge_fleets/bridge/bridge.json`
  - `transferPolicies.ticker_20ms.intervalMs`
- visual_state pdudef の `pdu_size`
  - `config/pdudef/drone-visual-state-pdutypes.json`
  - `work/hakoniwa-pdu-bridge-core/config/web_bridge_fleets/pdu/drone-visual-state-pdutypes.json`
  - `work/hakoniwa-threejs-drone/config/pdudef-fleets-pdutypes.json`

## 設計前提（本リポジトリの fleets 運用）

- drone 側 logical channel: 1機体あたり 19
- service 側 channel: 1機体あたり 10（5サービス × req/res）
- viewer 用 channel: 4（固定）

必要 channel 数（core）:

- `channels_required(N) = 29 * N + 4`
- 例: `N=100` のとき `2904`

## 推奨設定ルール

- `HAKO_PDU_CHANNEL_MAX >= next_pow2(29*N + 4)`
- `HAKO_SERVICE_MAX >= next_pow2(5*N)`
- `HAKO_RECV_EVENT_MAX >= max(1024, 4 * HAKO_SERVICE_MAX)`
- `HAKO_SERVICE_CLIENT_MAX >= 128`
- `HAKO_DATA_MAX_ASSET_NUM >= 8`（推奨 16）

bridge/publisher:

- 単一チャネル運用（推奨）:
  - `max_drones_per_packet = N`
  - `required_visual_state_array_channels = 1`
- 分割チャネル運用:
  - `required_visual_state_array_channels = ceil(N / max_drones_per_packet)`
  - `bridge.json` 側の転送対象チャネル群と一致させる
  - `comm/visual-state-shm-callback.json` の受信対象チャネル群とも一致させる
- 周期:
  - `publish_interval_msec = 20`
  - `ticker_20ms.intervalMs = 20`
- `pdu_size`:
  - `recommended_visual_state_pdu_size = next_pow2(64 * max_drones_per_packet)`
  - 例: `max_drones_per_packet=200` -> `12800` -> `16384`
  - 例: `max_drones_per_packet=256` -> `16384`
  - 例: `max_drones_per_packet=320` -> `20480` -> `32768`
  - 例: `max_drones_per_packet=512` -> `32768`

## なぜこのルールか（根拠）

### core-pro

- `HAKO_PDU_CHANNEL_MAX`:
  - 不足すると channel 登録時に失敗し、サービス生成やPDU入出力が連鎖的に不安定化する。
  - `next_pow2` を使うのは、台数増加時の再調整回数を減らし、余裕を持たせるため。
- `HAKO_SERVICE_MAX`:
  - fleets では `5サービス/機体`（SetReady/TakeOff/GoTo/GetState/Land）を前提に増加するため、`5*N` を基準にする。
- `HAKO_RECV_EVENT_MAX`:
  - 並列RPC登録時に最初に詰まりやすい箇所。実測で `recv_event_table_ is full` が再発源だったため、`4 * SERVICE_MAX` の余裕を取る。
- `HAKO_SERVICE_CLIENT_MAX`:
  - クライアント再生成や同時登録の突発増に備えて `next_pow2(N)` を下限にし、最低でも `128` を確保する。
- `HAKO_DATA_MAX_ASSET_NUM`:
  - マルチプロセス化（drone-service複数、publisher、bridge等）で不足しやすいため、運用上は `16` 固定を推奨。

### bridge / publisher

- `max_drones_per_packet = N`（単一チャネル推奨）:
  - chunk 分割と bridge 転送対象の不一致があると、「一部機体だけ更新されない」事象を起こしやすい。
  - 単一チャネル化により、転送対象の取り違えを避ける。
- `publish_interval_msec = 20` / `ticker_20ms.intervalMs = 20`:
  - 100ms はCPUは下がるが可視化がカクつく実測結果があった。
  - 20ms（50Hz）は見た目の連続性とCPU負荷のバランスが最も安定した運用点。
- `pdu_size` を power-of-two にする理由:
  - `max_drones_per_packet` を上げた際に payload 上限を超えると、bridge 側で受信サイズ不整合や欠落更新を起こしやすい。
  - `next_pow2` で余裕を持たせることで、境界付近の設定ミスを減らせる。

## N=100 の採用値（実績）

- `HAKO_PDU_CHANNEL_MAX = 4096`
- `HAKO_SERVICE_MAX = 1024`
- `HAKO_RECV_EVENT_MAX = 4096`
- `HAKO_SERVICE_CLIENT_MAX = 128`
- `HAKO_DATA_MAX_ASSET_NUM = 16`

bridge/publisher:

- `max_drones_per_packet = 100`
- `required_visual_state_array_channels = 1`
- `recommended_visual_state_pdu_size = 8192`
- `publish_interval_msec = 20`
- `ticker_20ms.intervalMs = 20`

## N=200 の採用値（実績）

- `HAKO_PDU_CHANNEL_MAX = 8192`
- `HAKO_SERVICE_MAX = 1024`
- `HAKO_RECV_EVENT_MAX = 4096`
- `HAKO_SERVICE_CLIENT_MAX = 256`
- `HAKO_DATA_MAX_ASSET_NUM = 16`

bridge/publisher:

- `max_drones_per_packet = 200`
- `required_visual_state_array_channels = 1`
- `recommended_visual_state_pdu_size = 16384`
- `publish_interval_msec = 20`
- `ticker_20ms.intervalMs = 20`

## N=256 の採用値（実績）

- `HAKO_PDU_CHANNEL_MAX = 8192`
- `HAKO_SERVICE_MAX = 2048`
- `HAKO_RECV_EVENT_MAX = 8192`
- `HAKO_SERVICE_CLIENT_MAX = 512`
- `HAKO_DATA_MAX_ASSET_NUM = 16`

bridge/publisher:

- `max_drones_per_packet = 256`
- `required_visual_state_array_channels = 1`
- `recommended_visual_state_pdu_size = 16384`
- `publish_interval_msec = 20`
- `ticker_20ms.intervalMs = 20`

## N=320 の採用値（実績）

- `HAKO_PDU_CHANNEL_MAX = 16384`
- `HAKO_SERVICE_MAX = 2048`
- `HAKO_RECV_EVENT_MAX = 8192`
- `HAKO_SERVICE_CLIENT_MAX = 512`
- `HAKO_DATA_MAX_ASSET_NUM = 16`

bridge/publisher（単一チャネル）:

- `max_drones_per_packet = 320`
- `required_visual_state_array_channels = 1`
- `recommended_visual_state_pdu_size = 32768`
- `publish_interval_msec = 20`
- `ticker_20ms.intervalMs = 20`

注意:

- 現在の `web_bridge_fleets` 既定構成は `drone_visual_state_array_0` の単一チャネル転送。
- 分割チャネルに戻す場合は、以下3点を必ず同時更新すること。
  - bridge の `pduKeyGroups`（`_0/_1/...` を列挙）
  - bridge の pdutypes（`drone_visual_state_array_0/_1/...` を定義）
  - viewer 側 pdutypes（同一チャネル名・同一 `pdu_size`）

## N=512 の推奨値（チャレンジ前設定）

- `HAKO_PDU_CHANNEL_MAX = 16384`
- `HAKO_SERVICE_MAX = 4096`
- `HAKO_RECV_EVENT_MAX = 16384`
- `HAKO_SERVICE_CLIENT_MAX = 1024`
- `HAKO_DATA_MAX_ASSET_NUM = 16`

bridge/publisher（単一チャネル）:

- `max_drones_per_packet = 512`
- `required_visual_state_array_channels = 1`
- `recommended_visual_state_pdu_size = 32768`
- `publish_interval_msec = 20`
- `ticker_20ms.intervalMs = 20`

## 値決定ツール

`N` から推奨値を算出する:

```bash
python3 tools/calc_fleet_params.py -n 200
```

例（分割チャネル想定）:

```bash
python3 tools/calc_fleet_params.py -n 256 --max-drones-per-packet 64
```

## 背景ログ（再発防止）

低い上限値のまま `N=4` 以上で service client を並列登録すると、以下エラーが発生した。

- `ERROR: recv_event_table_ is full`
- `Failed to register data receive event for service client`
- `service_id_ is invalid`
- `Failed to register service client`

## 運用注意

- マクロ変更後は、core / drone / bridge を同一設定で再ビルドすること。
- SHM 互換性のため、実行中プロセス停止後にクリーン起動すること。
