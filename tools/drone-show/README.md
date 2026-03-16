# tools/drone-show

## 文字を変更する最短手順

1. 文字フォーメーションを生成する

```bash
# 1文字（例: H）
python3 tools/drone-show/gen_letter_formation.py \
  --letter H \
  --count 100 \
  --out config/drone-show-config/formations/formation-H-100.json

# 単語（例: HAKONIWA）
python3 tools/drone-show/gen_word_formation.py \
  --word HAKONIWA \
  --count 100 \
  --letter-width 1.0 \
  --letter-height 2.0 \
  --gap 0.45 \
  --out config/drone-show-config/formations/formation-HAKONIWA-100.json
```

2. `show-*.json` の `formation_files` と `timeline` を更新する

- `formation_files[].id` と `timeline[].formation` の文字列を一致させる
- `meta.drone_count` と生成点数（`--count`）を一致させる

3. 事前確認する

```bash
# 定義整合チェック
python3 tools/drone-show/load_show_config.py \
  --input config/drone-show-config/show-hello-world-100-ref.json \
  --print-resolved

# 2Dプレビュー
python3 tools/drone-show/plot_show.py \
  --input config/drone-show-config/show-hello-world-100-ref.json \
  --out-dir ./tmp/drone-show-preview \
  --mode 2d
```

## load_show_config.py

`show` JSON を読み込み、`formation_files` を解決して検証します。

### 例

```bash
python3 tools/drone-show/load_show_config.py \
  --input config/drone-show-config/show-h-a-16-ref.json \
  --output /tmp/show-h-a-16-resolved.json
```

### 主な検証

- `meta.drone_count > 0`
- `formations` / `formation_files` の重複IDなし
- 各点が `[x, y, z]` 数値
- `timeline[].formation` が既存formationを参照
- `timeline[].duration_sec > 0`, `hold_sec >= 0`
- （デフォルト）各 formation の点数が `drone_count` と一致

### オプション

- `--no-enforce-drone-count`
  - formation点数と `drone_count` の一致チェックを無効化
- `--print-resolved`
  - 解決後JSONを stdout 出力

## plot_show.py

`load_show_config.py` で解決した定義を使って、`timeline` の各ステップを 3D PNG で出力します。

### 例

```bash
python3 tools/drone-show/plot_show.py \
  --input config/drone-show-config/show-h-a-16-ref.json \
  --out-dir /tmp/drone-show-plots
```

100機体例（ラベル非表示デフォルト）:

```bash
python3 tools/drone-show/plot_show.py \
  --input config/drone-show-config/show-h-a-100-ref.json \
  --out-dir ./tmp/drone-show-plots-100
```

俯瞰2D（推奨）:

```bash
python3 tools/drone-show/plot_show.py \
  --input config/drone-show-config/show-h-a-100-ref.json \
  --out-dir ./tmp/drone-show-plots-100 \
  --mode 2d
```

## gen_letter_formation.py

文字の点群フォーメーションを生成します（`H/E/L/O/W/R/D/A` をサポート）。

```bash
python3 tools/drone-show/gen_letter_formation.py \
  --letter H \
  --count 100 \
  --out config/drone-show-config/formations/formation-H-100.json
```

## gen_word_formation.py

単語全体を1つのフォーメーションとして生成します（例: `HELLOWORLD` を同時表示）。

```bash
python3 tools/drone-show/gen_word_formation.py \
  --word HELLOWORLD \
  --count 100 \
  --letter-width 1.0 \
  --letter-height 2.0 \
  --gap 0.45 \
  --out config/drone-show-config/formations/formation-HELLOWORLD-100.json
```

## plot_formations.py

`formation-*.json` を直接プロットします（timelineを使わない）。

```bash
python3 tools/drone-show/plot_formations.py \
  --inputs \
    config/drone-show-config/formations/formation-H-100.json \
    config/drone-show-config/formations/formation-A-100.json \
  --out-dir ./tmp/drone-show-formations \
  --mode 2d
```

## HELLO WORLD サンプル

- show 定義:
  - `config/drone-show-config/show-hello-world-100-ref.json`
  - `config/drone-show-config/show-hello-world-once-100-ref.json`（全字同時）
- 文字フォーメーション:
  - `H/E/L/O/W/R/D` の `formation-*-100.json`
  - `formations/formation-HELLOWORLD-100.json`（全字同時）

可視化:

```bash
python3 tools/drone-show/plot_show.py \
  --input config/drone-show-config/show-hello-world-100-ref.json \
  --out-dir ./tmp/drone-show-hello-world-100-2d \
  --mode 2d
```

全字同時フォーメーションのみ可視化:

```bash
python3 tools/drone-show/plot_formations.py \
  --inputs config/drone-show-config/formations/formation-HELLOWORLD-100.json \
  --out-dir ./tmp/drone-show-formations \
  --mode 2d
```
