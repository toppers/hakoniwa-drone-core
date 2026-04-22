# fleets 運用手順（hakoniwa-drone-pro 利用者向け）

この手順は、`hakoniwa-drone-pro` を使って fleets 構成を実行し、別PCブラウザで可視化し、性能計測まで行うための最短手順です。

前提となる配置/環境変数は `docs/fleets/installation.md` を参照してください。
参照コンフィグの全体像は `docs/fleets/config-runtime-map.md` を参照してください。

## 1. 事前準備

- 作業ディレクトリ: リポジトリルート（`hakoniwa-drone-pro`）
- 利用ポート:
  - `8000/tcp`（viewer web）
  - `8765/tcp`（WebSocket bridge）
- 別PCから可視化する場合は、Sim Host の IP 到達性を確認する
- 機体数を大きく変える場合（例: 100→200/256）は、先に推奨値を算出:

```bash
python3 tools/calc_fleet_params.py -n <N>
```

算出値の適用先は `docs/fleets/core-parameter-sizing.md` を参照。

## 2. fleets 起動（Sim Host）

機体数 `N` を指定して起動します（内部で current 設定を自動生成）。

```bash
bash tools/launch-fleets-scale-perf.bash <N>
```

密集レイアウト例:

```bash
LAYOUT=packed-rings RING_SPACING_METER=0.55 bash tools/launch-fleets-scale-perf.bash <N>
```

## 3. 可視化（View Host = 別PCブラウザ）

`SIM_IP` を Sim Host の IP に置換して開きます。

```text
http://SIM_IP:8000/index.html?viewerConfigPath=/config/viewer-config-fleets.json&wsUri=ws://SIM_IP:8765&wireVersion=v2&dynamicSpawn=true&templateDroneIndex=0&maxDynamicDrones=<N>
```

注意:

- `viewerConfigPath` は `/config/...` を使う（`/work/...` は 404 になりやすい）
- `maxDynamicDrones` は起動時パラメータ（変更時はページ再読込）

## 4. ミッション実行（任意）

複数機体 square mission（位相ずらし対応）:

```bash
bash drone_api/external_rpc/apps/run_square_mission.bash --drone-count <N> --phase-step 1
```

詳細オプションは以下を参照:

- [drone_api/external_rpc/README.md](../../drone_api/external_rpc/README.md)

## 5. 計測（任意）

### 5.1 収集

```bash
bash tools/start-host-perf-monitor.bash <N> fleets_scale_n<N> 3600
```

### 5.2 集計

```bash
python tools/perf/aggregate_metrics.py --input logs/perf --output logs/perf/summary.csv
```

### 5.3 グラフ

```bash
python tools/perf/plot_summary.py --input logs/perf/summary.csv --output-dir logs/perf
```

## 6. トラブルシュート

- 症状: 3Dビューで機体が更新されない
  - `wsUri=ws://SIM_IP:8765` の指定ミス、またはポート未到達を確認
- 症状: viewer config 読み込み 404
  - `viewerConfigPath=/config/viewer-config-fleets.json` か確認
- 症状: service client 登録失敗（`recv_event_table_ is full`）
  - `docs/fleets/core-parameter-sizing.md` の固定パラメータを確認し、core/drone/bridge を同一設定で再ビルド

## 関連

- 固定パラメータ設計: `docs/fleets/core-parameter-sizing.md`
- 性能ツール詳細: `tools/perf/README.md`
- 実験タスク管理: `issue-scale-experiment.md`
