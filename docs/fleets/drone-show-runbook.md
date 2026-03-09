# fleets Drone Show Runbook

このページは、`run_show.bash` を使った fleets ドローンショー実行の運用手順をまとめたものです。

## 何をやっているか（デモの意図）

- `show` JSON でフォーメーション遷移（文字/図形）を定義する
- `run_show.bash` が `show_runner.py` を呼び、複数機体へ `set_ready -> takeoff -> goto` を発行する
- 実行中ログ（`wait_start/wait_done`, `ok/message`）で各ステップ成否を追跡する

## 構成

1. **定義データ**
- `config/drone-show-config/show-*.json`
  - `meta`: ショー名・機体数
  - `options`: `center/scale/base_alt/max_speed/failure_policy`
  - `formation_files`: フォーメーションIDとファイル
  - `timeline`: 遷移順（`formation`, `duration_sec`, `hold_sec`）
- `config/drone-show-config/formations/formation-*.json`
  - 点群データ（`id`, `points[[x,y,z], ...]`）

2. **生成/検証ツール**
- `tools/drone-show/gen_word_formation.py`
- `tools/drone-show/gen_drone_icon_formation.py`
- `tools/drone-show/load_show_config.py`
- `tools/drone-show/plot_show.py`

3. **実行ランナー**
- `drone_api/external_rpc/run_show.bash`
- `drone_api/external_rpc/show_runner.py`

## 実行までの流れ

1. フォーメーション生成（必要時）
2. `load_show_config.py` で JSON 整合チェック
3. `plot_show.py` で 2D 事前確認
4. `run_show.bash` で本実行

## 実行コマンド（代表）

200機・3ステップ（`HAKONIWA -> DRONE_ICON -> DRONE_SHOW!`）:

```bash
bash drone_api/external_rpc/run_show.bash \
  --show-config config/drone-show-config/show-hakoniwa-drone-icon-drone-show-3step-200-ref.json \
  --drone-count 200 \
  --assign-mode nearest
```

`run_show.bash` の `--show-config` は `--show-json` の alias。

## 実績プリセット（2026-03-08）

200機の実測で使用した実行パラメータ（再現用）:

```bash
HAKO_RPC_TRACE=1 \
HAKO_RPC_TRACE_VERBOSE=0 \
HAKO_RPC_REGISTER_RETRY_COUNT=180 \
HAKO_RPC_REGISTER_RETRY_INTERVAL_SEC=0.2 \
/usr/bin/time -p bash drone_api/external_rpc/run_show.bash \
  --show-config config/drone-show-config/show-hakoniwa-drone-icon-drone-show-3step-200-ref.json \
  --drone-count 200 \
  --assign-mode nearest \
  --proc-count 4 \
  --init-concurrency-per-proc 2 \
  --batch-init 256 \
  --batch-goto 256 \
  --speed 20.0 \
  --no-ready-gate
```

## 主要パラメータ

- `--assign-mode index|nearest`
  - `index`: 機体順固定（再現性重視）
  - `nearest`: 移動距離短縮（見た目重視）
- `--batch-init`, `--batch-goto`, `--batch-land`
  - 指令 fan-out の分割粒度
- `--proc-count`, `--init-concurrency-per-proc`
  - multi-process 構成の初期化同時実行数の目安
- `--init-retry-max`, `--init-retry-interval-sec`
  - `set_ready/takeoff` 初期化失敗時の自動再試行
- `--no-ready-gate`
  - `get_state` 到達待ちを無効化

## failure_policy（show JSON 側）

- `abort`: 失敗時に中断（原因切り分け向け）
- `continue`: 失敗機体を無視して継続
- `hold`: 失敗機体を保持して継続

注記:
- 形が「欠けて見える」検証中は `abort` 推奨（脱落を見逃さないため）。

## 200/256運用メモ

- 200機で安定確認済み
- 256機は表示・遷移条件の影響を受けやすいため、まず 200 機でショー定義を詰めてから拡張する
- `PDU size` / `max_drones_per_packet` / bridge転送設定は必ず同期する
  - 詳細: `docs/fleets/core-parameter-sizing.md`

## 関連

- 設計メモ: `docs/fleets/drone-show-design.md`
- external_rpc API一覧: `drone_api/external_rpc/README.md`
- トラブル時: `docs/fleets/troubleshooting.md`
