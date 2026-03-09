# Hakoniwa Drone Simulator v3.5.0 → v3.6.0 アップデート手順

## はじめに

Hakoniwa Drone Simulator v3.6.0 では、fleets（100台+同時シミュレーション）対応を中心に、
設定方式、Python同時制御、可視化パイプライン、Docker運用を強化しています。

本ドキュメントでは、v3.5.0 から v3.6.0 へ更新するための手順を説明します。

## v3.6.0 の新機能・変更点

今回のバージョンアップのメインは、**fleets 運用の実用化**です。

- MuJoCo 連携の更新
  - MuJoCo バージョンを `3.4.0 → 3.5.0` に更新
  - `MUJOCO_VERSION.txt` を更新
- compact 設定対応の強化（今回の推しポイント）
  - fleets の設定を compact 前提で運用可能に
  - 型定義（types）と機体定義（instances/services）を分離し、100台+運用時の保守性を改善
- fleets 設定方式の導入
  - `config/drone/fleets/types/*`（共通タイプ定義）
  - `config/drone/fleets/api-current*.json`（機体インスタンス定義）
  - `config/drone/fleets/services/*`（外部RPCサービス定義）
- 複数機体同時制御の強化（Python）
  - `drone_api/external_rpc/fleet_rpc.py`
  - `drone_api/external_rpc/show_runner.py`
  - `drone_api/external_rpc/run_show.bash`
- DroneVisualStateArray による可視化連携強化
  - `assets/visual_state_publisher/*`
  - `config/assets/visual_state_publisher/*`
  - `config/pdudef/drone-visual-state*.json`
- ドローンショー基盤の追加
  - `config/drone-show-config/*`（formation/show JSON）
  - `tools/drone-show/*`（ローダー/生成/プロット）
- fleets 向け運用ドキュメント整備
  - `docs/fleets/*`
- Docker 導線の更新
  - fleets 構成で必要な bridge/endpoint/viewer 導線を改善

## 前提とする環境

- 検証環境: macOS（Apple Silicon）  
  （本リリースの fleets 検証は Mac 環境で実施）
- 箱庭ドローンシミュレータのアーキテクチャパターン:
  [コンテナパターン](https://github.com/toppers/hakoniwa-drone-core/blob/main/docs/getting_started/container.md)

## アップデート手順

### アップデート対象リポジトリ

- hakoniwa-drone-core
  - target version: v3.6.0

既存のローカル変更がある場合は先に退避してください。

`hakoniwa-drone-core` 配下で以下を実行します。

```bash
git fetch --tags
git checkout v3.6.0
git submodule update --init --recursive
```

> `main` を使う運用の場合は `git pull origin main` でも可。

## 追加で利用する関連リポジトリ（fleets 運用時）

fleets 構成では、以下を併用します（`work/` 配下運用または環境変数で外部配置）。

- hakoniwa-pdu-bridge-core
  - GitHub URL: https://github.com/hakoniwalab/hakoniwa-pdu-bridge-core
- hakoniwa-threejs-drone
  - GitHub URL: https://github.com/hakoniwalab/hakoniwa-threejs-drone

## アップデート対象ライブラリ等

- hakoniwa-core-full debian パッケージ（必要時）
- hakoniwa-pdu Python ライブラリ（必要時）
- hakoniwa-drone-core docker イメージ
  - target version: `v2.5.0`

### Docker イメージのアップデート手順

```bash
bash docker/pull-image.bash
```

確認:

```bash
docker images | grep hakoniwa-drone-core
```

### host 環境の hakoniwa-pdu 更新（必要時）

```bash
pip install --upgrade hakoniwa-pdu
pip show hakoniwa-pdu
```

### host 環境の hakoniwa-core-full 更新（必要時）

```bash
sudo apt-get update
sudo apt-get install --only-upgrade hakoniwa-core-full
dpkg -s hakoniwa-core-full | grep Version
```

## v3.6.0 で特に確認すべき項目

### 1. fleets 起動確認

```bash
bash tools/launch-fleets-scale-perf.bash 100
```

### 2. 外部RPC（複数機体）確認

```bash
bash drone_api/external_rpc/run_square_mission.bash --drone-count 2
```

### 3. ドローンショー実行確認

```bash
bash drone_api/external_rpc/run_show.bash \
  --show-config config/drone-show-config/show-hakoniwa-drone-icon-drone-show-3step-200-ref.json \
  --drone-count 200 \
  --assign-mode nearest
```

## 補足ドキュメント

- compact 設定の内部設計:
  [docs/architecture/config/README.md](./architecture/config/README.md)
- fleets クイックスタート:
  [docs/fleets/quickstart.md](./fleets/quickstart.md)
- fleets インストール:
  [docs/fleets/installation.md](./fleets/installation.md)
- fleets 運用:
  [docs/fleets/operations.md](./fleets/operations.md)
- core パラメータ設計:
  [docs/fleets/core-parameter-sizing.md](./fleets/core-parameter-sizing.md)
- 再ビルド手順:
  [docs/fleets/rebuild-and-restart.md](./fleets/rebuild-and-restart.md)
- 性能レポート:
  [docs/fleets/performance-report.md](./fleets/performance-report.md)

## 変更差分（参考）

`v3.5.0..HEAD` 集計:

- 40 commits
- 249 files changed
- +93225 / -532

詳細は以下を参照:

- [changelog.md](../changelog.md)
