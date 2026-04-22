# Hakoniwa Drone Simulator v3.7.0 → v3.7.1 アップデート手順

## はじめに

Hakoniwa Drone Simulator v3.7.1 では、**MuJoCo ベースの箱庭ドローンシミュレータを、RC 操作だけでなく Python external RPC から複数機体で扱えるようにする導線**を強化しました。

主な更新内容は、

- MuJoCo 複数機 runtime 生成ツールの追加
- fleets compact config からの MuJoCo instance override
- `external_rpc` を使った MuJoCo 2 機サンプルと quickstart 整備
- MuJoCo `3.5.0 → 3.7.0` への更新

です。

本ドキュメントでは、v3.7.0 から v3.7.1 へ更新する際の変更点と確認項目を説明します。

## v3.7.1 の新機能・変更点

今回のバージョンアップの中心は、**MuJoCo + fleets + Python API の実運用導線の追加**です。

- MuJoCo version update
  - MuJoCo を `3.5.0 → 3.7.0` に更新
  - `MUJOCO_VERSION.txt` による version 一元管理を強化
  - build/install/link script と GitHub Actions を `MUJOCO_VERSION.txt` 参照に統一
- MuJoCo fleets runtime generation
  - `tools/gen_fleet_scale_config.py`
    - `--type-config-path`
    - `--enable-mujoco-overrides`
    に対応
  - `tools/gen_mujoco_multidrone_xml.py`
    - scene template + drone body template から multi-drone `drone.xml` を生成
- fleet instance の MuJoCo override 対応
  - `config/drone/fleets/types/api-mujoco.json`
  - `config/drone/fleets/api-mujoco-instance-2.json`
  - fleets instance 側に optional `mujoco` extension を持てるようにし、
    `modelName` / `propNames` を instance ごとに上書き可能に
- MuJoCo scene template 導入
  - `config/drone/fleets/types/mujoco-scene.xml.template`
  - `config/drone/fleets/types/mujoco-drone.xml.template`
  - `__DRONE_BODIES__` プレースホルダに多機体 drone body を差し込む方式を導入
  - landmark / building / obstacle をユーザが scene template 側に追記可能
- MuJoCo viewer の複数機 follow 対応
  - `main_hako_drone_service --mujoco-viewer`
  - fleets config から follow 対象 body 名を取得
  - `c` で follow / free camera を切り替え可能
  - `v` で camera orientation を reset
  - `1`〜`9` キーで follow 対象機体を切り替え可能
- Python external RPC の MuJoCo サンプル整備
  - `drone_api/external_rpc/samples/mujoco_two_drone_demo.py`
  - `FleetRpcController(..., use_async_shared=True)` を使った 2 機制御サンプルを追加
- external_rpc の整理
  - `drone_api/external_rpc/`
    - library
  - `drone_api/external_rpc/samples/`
    - sample scripts
  - `drone_api/external_rpc/apps/`
    - show / mission runner
  - `drone_api/external_rpc/obsolete/`
    - legacy single-command scripts
- `FleetRpcController.get_status()` の追加
  - `hako_msgs/DroneStatus` を direct PDU read で取得可能
  - `collided_counts` などの status 確認が可能
- `DroneLand` timeout/cancel 調整
  - landing 中 cancel を server 側で受け付けるよう改善
  - Python 側では timeout/cancel をより分かる形で扱うよう整理

## 前提とする環境

- 検証環境:
  - macOS (Apple Silicon)
  - Ubuntu (Windows 11/WSL2)
- 利用ツール:
  - `git`
  - `python3`
- Python 動作確認:
  - Python 3.12 系
- 主な利用形態:
  - Hakoniwa fleets config
  - MuJoCo runtime
  - Python external RPC

> 本ドキュメントのコマンド例は、**macOS 上で配布済みバイナリを使うケース**を前提にしています。
> Ubuntu/WSL2 ではパスや実行ファイル名が異なる場合があります。

## アップデート対象リポジトリ

- hakoniwa-drone-core
  - target version: v3.7.1

既存のローカル変更がある場合は先に退避してください。

`hakoniwa-drone-core` 配下で以下を実行します。

```bash
git fetch --tags
git checkout v3.7.1
git submodule update --init --recursive
```

> `main` を使う運用の場合は `git pull origin main` でも可。

## 関連リポジトリ

v3.7.1 では、以下の関連リポジトリを併用する場合があります。

- hakoniwa-pdu-python
  - Python external RPC や `async_shared` runtime を使う場合
- hakoniwa-pdu-endpoint
  - v3.7.0 系の RC endpoint 運用を継続する場合

## v3.7.1 で特に注意すべき互換ポイント

### 1. MuJoCo バージョン更新に伴う実行環境の不整合に注意

MuJoCo を `3.7.0` に更新したため、既存の `3.5.0` 系ライブラリや古い配布バイナリをそのまま使うと、

- 異常な rigid-body mass / COM が出る
- `--mujoco-viewer` 起動時に segfault する

などの不整合が起こる可能性があります。

MuJoCo を使う場合は、`3.7.0` に対応した配布済み実行環境を利用してください。

### 2. `FleetRpcController` の既定値は後方互換のため `use_async_shared=False`

`FleetRpcController` は既定では従来どおり同期 client を thread pool で並べる経路です。
これは既存スクリプトとの互換性を保つためであり、多機体向けの推奨経路ではありません。

複数機を新規に扱う場合は、次を推奨します。

```python
FleetRpcController(["Drone-1", "Drone-2"], use_async_shared=True)
```

`use_async_shared=False` は互換用と考えてください。

### 3. fleet instance の `mujoco` は optional extension

今回追加した `mujoco` key は、fleets compact config 全体を変更するものではありません。

- 非 MuJoCo runtime
  - 従来どおり `name/type/position_meter/angle_degree`
- MuJoCo runtime
  - 必要に応じて `mujoco.modelName` / `mujoco.propNames`

という位置付けです。

## アップデート後のセットアップ手順

### 1. fleets config / service config / pdudef を生成

```bash
python3 tools/gen_fleet_scale_config.py \
  -n 2 \
  --layout packed-rings \
  --ring-spacing-meter 1 \
  --type-name api-mujoco \
  --type-config-path config/drone/fleets/types/api-mujoco.json \
  --fleet-path config/drone/fleets/api-current.json \
  --pdudef-path config/pdudef/drone-pdudef-current.json \
  --service-config-path config/drone/fleets/services/api-current-service.json \
  --service-out-path config/drone/fleets/services/api-current-service.json \
  --enable-mujoco-overrides
```

### 2. MuJoCo XML を生成

```bash
python3 tools/gen_mujoco_multidrone_xml.py \
  -n 2 \
  --scene-template-path config/drone/fleets/types/mujoco-scene.xml.template \
  --drone-template-path config/drone/fleets/types/mujoco-drone.xml.template \
  --output-path config/drone/mujoco-current/drone.xml
```

### 3. MuJoCo simulator を起動

viewer あり:

```bash
./mac/mac-main_hako_drone_service \
  config/drone/fleets/api-current.json \
  config/pdudef/drone-pdudef-current.json \
  --real-sleep-msec 1 \
  --mujoco-viewer
```

viewer なし:

```bash
./mac/mac-main_hako_drone_service \
  config/drone/fleets/api-current.json \
  config/pdudef/drone-pdudef-current.json \
  --real-sleep-msec 1
```

### 4. Python external RPC サンプルを実行

```bash
python3 drone_api/external_rpc/samples/mujoco_two_drone_demo.py
```

## アップデート後の確認項目

### 1. MuJoCo 2 機 runtime 生成確認

以下が生成されることを確認します。

- `config/drone/fleets/api-current.json`
- `config/drone/fleets/services/api-current-service.json`
- `config/pdudef/drone-pdudef-current.json`
- `config/drone/mujoco-current/drone.xml`

### 2. MuJoCo viewer の follow 切り替え確認

`--mujoco-viewer` 付き起動後に、

- `c`: follow / free camera 切り替え
- `v`: camera orientation reset
- `1` / `2`: 2 機構成での follow target の切り替え

を確認します。

viewer 自体は `1`〜`9` キーに対応していますが、この quickstart では 2 機構成なので `1` / `2` を使います。

### 3. Python からの 2 機制御確認

`mujoco_two_drone_demo.py` で、

- `set_ready`
- `takeoff`
- `goto`
- `get_state`
- `get_status`

が通ることを確認します。

### 4. scene template の差し替え確認（オプション）

`mujoco-scene.xml.template` に landmark / building / obstacle を追加し、
再生成後の `drone.xml` に反映されることを確認します。

## 補足ドキュメント

- リポジトリ内の MuJoCo runtime generation:
  [docs/fleets/mujoco-runtime-generation.md](./fleets/mujoco-runtime-generation.md)
- リポジトリ内の MuJoCo + external RPC quickstart:
  [docs/fleets/mujoco-external-rpc-quickstart.md](./fleets/mujoco-external-rpc-quickstart.md)
- リポジトリ内の External RPC README:
  [drone_api/external_rpc/README.md](../drone_api/external_rpc/README.md)
- リポジトリ内の External RPC tutorial:
  [docs/fleets/external-rpc-tutorial.md](./fleets/external-rpc-tutorial.md)
- リポジトリ内の External RPC API reference:
  [docs/fleets/external-rpc-api-reference.md](./fleets/external-rpc-api-reference.md)
- リポジトリ内の MuJoCo fleets runtime design:
  [docs/architecture/config/fleet-mujoco-runtime-design.md](./architecture/config/fleet-mujoco-runtime-design.md)

## v3.7.1 の成果サマリ

今回のリリースで、以下の導線が成立しました。

- fleets compact config から MuJoCo multi-drone runtime を生成
- MuJoCo scene template に障害物や landmark を自由に追加
- `main_hako_drone_service` の MuJoCo viewer で複数機を follow
- Python external RPC から MuJoCo 2 機を制御
- `external_rpc` を library / samples / apps / obsolete に整理

つまり v3.7.1 は、**MuJoCo を fleets と Python API で実運用できる形に整えたリリース**です。
