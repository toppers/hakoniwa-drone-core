# fleets インストール/配置ガイド

このページは fleets 運用に必要なコンポーネントの配置と、launcher が参照する環境変数を定義する。

## 必要コンポーネント

1. `hakoniwa-drone-pro`（本リポジトリ）
2. `hakoniwa-pdu-bridge-core`（bridge 実行）
3. `hakoniwa-threejs-drone`（viewer web 配信）

## 配置パターン

### A. 同梱（現行デフォルト）

- `work/hakoniwa-pdu-bridge-core`
- `work/hakoniwa-threejs-drone`

この場合、追加設定なしで以下が使える:

```bash
bash tools/launch-fleets-scale-perf.bash <N>
```

### B. 外部配置（独立リポジトリ運用）

`work/` を使わず、任意パスに配置して環境変数で参照する。

```bash
export HAKO_DRONE_PROJECT_PATH=/path/to/hakoniwa-drone-pro
export HAKO_PDU_BRIDGE_CORE_PATH=/path/to/hakoniwa-pdu-bridge-core
export HAKO_THREEJS_VIEWER_PATH=/path/to/hakoniwa-threejs-drone
bash tools/launch-fleets-scale-perf.bash <N>
```

## launcher が使う主要環境変数

- `HAKO_DRONE_PROJECT_PATH`
  - drone service / visual_state_publisher / perf scripts の基準パス
- `HAKO_PDU_BRIDGE_CORE_PATH`
  - bridge 起動 (`tools/run-web-bridge.bash`) の基準パス
- `HAKO_THREEJS_VIEWER_PATH`
  - `python -m http.server 8000` の `cwd`

## 最低確認

起動ログに以下が表示されること:

- `HAKO_DRONE_PROJECT_PATH=...`
- `HAKO_PDU_BRIDGE_CORE_PATH=...`
- `HAKO_THREEJS_VIEWER_PATH=...`

## 補足

- 別PCブラウザから接続する場合は、URL の `wsUri` を Sim Host IP にする。
- 詳細運用は `docs/fleets/operations.md` を参照。
