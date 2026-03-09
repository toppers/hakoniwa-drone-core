# fleets 向け再ビルド・クリーン再起動手順

この手順は、hakoniwa-core の固定上限（`HAKO_*_MAX`）を変更した後に、実行バイナリ差分と SHM 不整合を残さず再起動するための手順です。

## 0. 変更箇所（パラメータ定義）

- `thirdparty/hakoniwa-core-pro/sources/core/include/hako_pro_config.hpp`
  - `HAKO_RECV_EVENT_MAX`
  - `HAKO_SERVICE_CLIENT_MAX`
  - `HAKO_SERVICE_MAX`
- `thirdparty/hakoniwa-core-pro/hakoniwa-core-cpp/src/include/config/hako_config.hpp`
  - `HAKO_PDU_CHANNEL_MAX`
  - `HAKO_DATA_MAX_ASSET_NUM`

値の求め方は `core-parameter-sizing.md` を参照。

重要:

- `thirdparty/hakoniwa-core-pro` だけでなく、以下の同梱コピーも同じ値に揃えること。
  - `work/hakoniwa-pdu-bridge-core/work/hakoniwa-core-pro/...`
  - `work/hakoniwa-pdu-python/work/hakoniwa-core-pro/...`
- どちらか一方だけ更新すると、起動はしても bridge/viewer 接続で不整合が出る。

## 1. 実行中プロセスを停止

- launcher 実行中端末で `Ctrl+C`

## 2. core を再ビルド・インストール（thirdparty）

```bash
cd thirdparty/hakoniwa-core-pro
ASSET_NUM=16 SERVICE_MAX=2048 RECV_EVENT_MAX=8192 SERVICE_CLIENT_MAX=512 CHANNEL_MAX=8192 ./build.bash
ASSET_NUM=16 SERVICE_MAX=2048 RECV_EVENT_MAX=8192 SERVICE_CLIENT_MAX=512 CHANNEL_MAX=8192 bash install.bash
```

補足:

- `ASSET_NUM` は `HAKO_DATA_MAX_ASSET_NUM` の下限に合わせる
- `SERVICE_MAX` / `RECV_EVENT_MAX` / `SERVICE_CLIENT_MAX` / `CHANNEL_MAX` も同一値で build/install に渡す

## 3. drone-pro を再ビルド（mac）

```bash
cd /Users/tmori/project/oss/hakoniwa-drone-pro
bash tools/build-mac.bash build
```

## 4. bridge を再ビルド

```bash
cd work/hakoniwa-pdu-bridge-core
./build.bash
```

## 5. 再起動

```bash
cd /Users/tmori/project/oss/hakoniwa-drone-pro
bash tools/launch-fleets-scale-perf.bash <N>
```

## 6. 確認（任意）

```bash
hako-cmd pmeta
```

確認ポイント:

- `pdu_meta_data.channel_num` が想定範囲に収まる
- 以前のエラー（`recv_event_table_ is full`）が再発しない

## 7. 256台向け追加チェック

- core 上限値:
  - `HAKO_PDU_CHANNEL_MAX = 8192`
  - `HAKO_SERVICE_MAX = 2048`
  - `HAKO_RECV_EVENT_MAX = 8192`
  - `HAKO_SERVICE_CLIENT_MAX = 512`
  - `HAKO_DATA_MAX_ASSET_NUM = 16`
- visual state:
  - `config/assets/visual_state_publisher/visual_state_publisher.json`
    - `max_drones_per_packet = 256`
  - `drone_visual_state_array_0` の `pdu_size` を関連ファイルで一致させる
    - `config/pdudef/drone-visual-state-pdutypes.json`
    - `work/hakoniwa-pdu-bridge-core/config/web_bridge_fleets/pdu/drone-visual-state-pdutypes.json`
    - `work/hakoniwa-threejs-drone/config/pdudef-fleets-pdutypes.json`
