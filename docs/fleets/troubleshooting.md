# fleets トラブルシューティング

このページは、fleets 運用で実際に発生した問題と対処をまとめたものです。

## 1. viewerConfigPath が 404 になる

### 症状

- ブラウザコンソールに `failed to load ... viewer-config-fleets.json`
- URL に `/work/.../viewer-config-fleets.json` を指定している

### 原因

- web server ルートは `HAKO_THREEJS_VIEWER_PATH`。`/work/...` を URL に直書きすると公開ルート外。

### 対処

- URL は必ず `/config/...` を使う。
  - 正: `viewerConfigPath=/config/viewer-config-fleets.json`

## 2. WebSocket 接続できない（別PC）

### 症状

- `ws://127.0.0.1:8765` で別PCブラウザが接続失敗

### 原因

- `127.0.0.1` は閲覧PC自身を指す。

### 対処

- `wsUri=ws://<SIM_HOST_IP>:8765` に変更
- `8000/tcp` と `8765/tcp` の到達性を確認

## 3. 一部機体が原点に残る / 動かない（N一般）

### 症状

- 実行機体の一部が更新されず原点に残る
- `Drone-33..` 以降に pose が来ない

### 原因

- `max_drones_per_packet` / chunk 構成と bridge 転送対象が不一致
- もしくは `drone_visual_state_array_0.pdu_size` が publisher/bridge/viewer で不一致

### 対処

- 1チャネル方針なら:
  - `config/assets/visual_state_publisher/visual_state_publisher.json`
  - `max_drones_per_packet=N` に設定
  - `config/pdudef/drone-visual-state-pdutypes.json`
  - `work/hakoniwa-pdu-bridge-core/config/web_bridge_fleets/pdu/drone-visual-state-pdutypes.json`
  - `work/hakoniwa-threejs-drone/config/pdudef-fleets-pdutypes.json`
  - 上記3箇所の `drone_visual_state_array_0.pdu_size` を一致させる
- bridge 再ビルド・再起動後に再確認

即チェック（257台以上）:
- `max_drones_per_packet = N`（単一チャネル）になっているか
- bridge の転送対象が `drone_visual_state_array_0` と運用方針で一致しているか
- `visual-state-shm-callback.json` の受信チャネル定義が bridge 転送チャネルと一致しているか

## 4. `recv_event_table_ is full` で mission が落ちる

### 症状

- `ERROR: recv_event_table_ is full`
- 続いて `Failed to register service client`

### 原因

- hakoniwa-core 固定上限マクロが不足（recv event / service / channel）。

### 対処

- `docs/fleets/core-parameter-sizing.md` の推奨値へ変更
- [rebuild-and-restart.md](./rebuild-and-restart.md) の手順で再ビルド + クリーン再起動

## 5. `Service call returned no response` / `drone_name mismatch`

### 症状

- 並列ミッション時に no response
- もしくは一部機体で `drone_name mismatch`

### 原因

- service client の登録/再利用状態が不整合
- 旧設定キャッシュや再起動不十分で発生しやすい

### 対処

- launcher 一式を停止して再起動
- `api-current-service.json` の機体名展開が `Drone-<ID>` になっているか確認
- 問題切り分け時は `--serial` で再現差を確認

## 6. 100ms/50ms にするとカクつく

### 症状

- CPU は下がるが表示がカクつく

### 原因

- publish/転送間隔が描画体感に対して粗すぎる

### 対処

- 現行推奨は 20ms:
  - `visual_state_publisher.publish_interval_msec=20`
  - bridge `ticker_20ms.intervalMs=20`

## 7. `maxDynamicDrones` を変えてもその場で反映されない

### 症状

- URL を編集しても即時台数が変わらない

### 原因

- 現行は起動時パラメータとして読み込み（ホット変更未対応）

### 対処

- URL 更新後、ページ再読込する

## 8. `maxDynamicDrones` と実行台数が不一致で表示がおかしい

### 症状

- 余分な機体が見える
- 実際に飛行している台数と表示台数が合わない

### 原因

- `maxDynamicDrones` が、実際に実行した `N` と一致していない

### 対処（運用回避）

- URL の `maxDynamicDrones` を実行台数 `N` に合わせる
- 合っていない場合は URL を見直して再読込する

## 9. どの設定を見ればよいか迷う

### 対処

- 参照マップ: [config-runtime-map.md](./config-runtime-map.md)
- 運用手順: [operations.md](./operations.md)
- 5分手順: [quickstart.md](./quickstart.md)

## 10. core を更新したのに browser が繋がらない（今回の失敗パターン）

### 症状

- `thirdparty/hakoniwa-core-pro` は更新したのに、bridge/viewer 接続が成立しない

### 原因

- `work` 配下の内包 `hakoniwa-core-pro` が旧値のまま残っている

### 対処

- 以下3系統の core マクロ値を同一に揃える:
  - `thirdparty/hakoniwa-core-pro`
  - `work/hakoniwa-pdu-bridge-core/work/hakoniwa-core-pro`
  - `work/hakoniwa-pdu-python/work/hakoniwa-core-pro`
- その後、core/drone/bridge を再ビルドし、再起動
