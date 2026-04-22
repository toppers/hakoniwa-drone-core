# Drone Show Design (fleets)

## 目的

- 100+ 機体で「文字/図形」フォーメーションを安全に再現する。
- 本番制御前に Python で点群シミュレーションし、危険なショー定義を事前に排除する。
- 同一 JSON を `offline simulator` と `Hakoniwa show runner` の両方で使い回す。

## 全体アーキテクチャ

1. `show.json` を読み込む
2. `show_sim.py` でオフライン点群シミュレーション
3. 検証OKなら `apps/show_runner.py` で fleets 実行
4. threejs で可視化・ログ計測

## コンポーネント

- `show schema`
  - フォーメーション点群、タイムライン、制約条件を定義
- `planner/assigner`
  - 機体と目標点の割当を計算
- `offline simulator`
  - 補間・速度制限・最小距離チェック
- `runtime runner`
  - `FleetRpcController` を用いて実機体(仮想)へ指令

## JSON仕様（最小）

```json
{
  "meta": {
    "name": "demo_show",
    "version": "1.0",
    "drone_count": 100
  },
  "options": {
    "center": [0.0, 0.0, 0.0],
    "scale": 1.0,
    "base_alt": 4.0,
    "min_distance": 0.8,
    "max_speed": 2.0
  },
  "formations": {
    "H": { "points": [[-2, -2, 0], [-2, 2, 0], [2, -2, 0], [2, 2, 0]] },
    "A": { "points": [[0, 3, 0], [-2, -2, 0], [2, -2, 0], [0, 0, 0]] }
  },
  "timeline": [
    { "formation": "H", "duration_sec": 4.0, "hold_sec": 1.0 },
    { "formation": "A", "duration_sec": 4.0, "hold_sec": 1.0 }
  ]
}
```

## JSON仕様（推奨: フォーメーション分離）

- `show` 本体はタイムラインとオプションのみを持つ
- フォーメーション点群は `formation-*.json` に分離する

例:

```json
{
  "meta": { "name": "sample_h_a_16_ref", "version": "1.0", "drone_count": 16 },
  "options": { "center": [0, 0, 0], "scale": 1.0, "base_alt": 4.0, "min_distance": 0.8, "max_speed": 2.0 },
  "formation_files": [
    { "id": "H", "path": "formations/formation-H-16.json" },
    { "id": "A", "path": "formations/formation-A-16.json" }
  ],
  "timeline": [
    { "formation": "H", "duration_sec": 4.0, "hold_sec": 1.0 },
    { "formation": "A", "duration_sec": 4.0, "hold_sec": 1.0 }
  ]
}
```

## 実行モード

- `offline`
  - 入力: `show.json`
  - 出力: 2D/3Dアニメ、メトリクス（最小距離/最大速度/逸脱量）
- `runtime`
  - 入力: `show.json`, `--drone-count`, `--service-config`
  - 出力: `wait_start/wait_done`, 各機体 `ok/message`

## 割当戦略

- Phase A（PoC）: index 順割当
- Phase B: 最近傍割当（距離短縮）
- Phase C: 最小コスト割当（交差/総移動量最小化）

## 安全制約

- 機体間最小距離 `min_distance` を下回る計画を拒否
- `max_speed` 超過が必要な遷移を拒否
- 到達失敗時ポリシー
  - `continue`: 失敗機体を除外して継続
  - `abort`: 即中断
  - `hold`: 現在位置で待機

## 推奨実装ステップ

1. `show_sim.py` を実装（JSON読込 + 補間 + 可視化）
2. `apps/show_runner.py` を実装（`FleetRpcController` 連携）
3. `apps/run_show.bash` を追加（CLI統一）
4. `H -> A` の2フォーメーションで 100 機体検証
5. issue に受け入れ結果を反映

## 受け入れ条件（初版）

- 同一 `show.json` が `offline` と `runtime` の両方で動く
- 100 機体で2フォーメーション遷移を完走できる
- `min_distance` と `max_speed` の検証結果がレポートされる
