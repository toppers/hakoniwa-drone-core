# Hakoniwa Drone Simulator v3.7.1 → v3.8.0 アップデート手順

## はじめに

Hakoniwa Drone Simulator v3.8.0 では、**`hakoniwa-core-pro` のデフォルト固定上限を fleets `N=200` 前提に見直し、build 時と実行時に有効パラメータを可視化する変更**を入れました。

今回の更新は、共有メモリ上の service/recv-event テーブルのサイズとレイアウトに影響するため、**非互換変更**です。

特に重要なのは次です。

- `hakoniwa-core-pro` の build defaults を `cmake/hako_build_defaults.conf` に集約
- `HAKO_*_MAX` の既定値を `N=200` 想定に見直し
- `HAKO_CLIENT_NAMELEN_MAX` / `HAKO_SERVICE_NAMELEN_MAX` を CMake から設定可能化
- build/install 時と実行時に build limit と SHM size をログ出力
- Docker イメージで `hakoniwa-core-pro` を source build する方式へ移行
- Ubuntu build script の整理

本ドキュメントでは、v3.7.1 から v3.8.0 へ更新する際の公開変更点と確認項目を説明します。

## v3.8.0 の新機能・変更点

今回のバージョンアップの中心は、**`hakoniwa-core-pro` の固定上限値を運用実態に合わせて整理し、非互換を検出しやすくすること**です。

- `hakoniwa-core-pro` build defaults の導入
  - `thirdparty/hakoniwa-core-pro/cmake/hako_build_defaults.conf` を追加
  - build defaults を 1 箇所で管理するよう変更
- `hakoniwa-core-pro` の既定パラメータ見直し
  - `HAKO_DATA_MAX_ASSET_NUM=16`
  - `HAKO_PDU_CHANNEL_MAX=8192`
  - `HAKO_RECV_EVENT_MAX=4096`
  - `HAKO_SERVICE_CLIENT_MAX=256`
  - `HAKO_SERVICE_MAX=1024`
  - `HAKO_CLIENT_NAMELEN_MAX=64`
  - `HAKO_SERVICE_NAMELEN_MAX=128`
  - これは fleets `N=200` を安全側で収める既定値
- client/service name length の CMake 設定対応
  - `HAKO_CLIENT_NAMELEN_MAX`
  - `HAKO_SERVICE_NAMELEN_MAX`
  を compile definition と build/install script から上書き可能化
- build/install 時の build limit 表示
  - `thirdparty/hakoniwa-core-pro/build.bash`
  - `thirdparty/hakoniwa-core-pro/install.bash`
  で有効パラメータを表示
- 実行時の build limit / SHM size ログ追加
  - `hako::init()`
  - `hako::create_asset_controller()`
  - `hako::get_simevent_controller()`
  で以下をログ出力
  - `asset_num`
  - `channel_max`
  - `recv_event_max`
  - `service_client_max`
  - `service_max`
  - `client_namelen_max`
  - `service_namelen_max`
  - `master_shm_size`
  - `recv_event_table_size`
  - `service_table_size`
  - `pro_shm_size`
- Docker build の見直し
  - `hakoniwa-core-full` apt package ではなく、`hakoniwa-core-pro` を clone して source build / install する方式へ変更
  - `HAKO_CORE_PRO_REPO`
  - `HAKO_CORE_PRO_REF`
  を Docker build argument で指定可能化
  - `/usr/local/hakoniwa/bin` を PATH に追加
- Ubuntu build script の整理
  - `tools/build-ubuntu.bash`
  を `cmake -S/-B` 形式に整理
  - `set -euo pipefail` を導入
  - `HAKO_USE_INSTALLED_CORE_LIBS` を外部から切り替え可能化

## 前提とする環境

- 検証環境:
  - macOS (Apple Silicon)
  - Ubuntu (Windows 11/WSL2)
- 利用ツール:
  - `git`
  - `cmake`
  - `python3`
- 主な利用形態:
  - fleets
  - MuJoCo runtime
  - Python external RPC
  - Docker / Ubuntu build

## アップデート対象リポジトリ

- hakoniwa-drone-pro
  - target version: v3.8.0

既存のローカル変更がある場合は先に退避してください。

`hakoniwa-drone-pro` 配下で以下を実行します。

```bash
git fetch --tags
git checkout v3.8.0
git submodule update --init --recursive
```

## 関連リポジトリ

v3.8.0 では、以下の関連リポジトリを併用する場合があります。

- hakoniwa-core-pro
  - `thirdparty/hakoniwa-core-pro` を利用
- hakoniwa-pdu-python
  - Python external RPC を使う場合
- hakoniwa-pdu-bridge-core
  - fleets viewer / web bridge を使う場合

## v3.8.0 で特に注意すべき互換ポイント

### 1. `hakoniwa-core-pro` の既定上限変更は非互換

今回の変更では、`hakoniwa-core-pro` の service/recv-event 関連の固定上限値と、client/service 名の格納長を変更しています。

- `HAKO_RECV_EVENT_MAX`
- `HAKO_SERVICE_CLIENT_MAX`
- `HAKO_SERVICE_MAX`
- `HAKO_CLIENT_NAMELEN_MAX`
- `HAKO_SERVICE_NAMELEN_MAX`

これにより、共有メモリ上の `recv-event/service` テーブルのサイズとレイアウトが変わります。

旧バイナリと新バイナリが混在すると、

- service client 登録失敗
- shared memory の読み書き不整合
- viewer / bridge / Python runtime との接続不整合

が起こり得ます。

**v3.8.0 への更新時は、関連バイナリを揃えて再ビルドし、shared memory をクリーンにした上で再起動してください。**

### 2. Python external RPC の client 名は従来互換を維持

`HAKO_CLIENT_NAMELEN_MAX` は `64` としたため、`external_rpc` / `async_shared` の client naming は短縮していません。

つまり、従来の

- `{service_type}Client_{safe_drone}`
- `{service_type}AsyncSharedClient_{safe_drone}`

という命名をそのまま使えます。

### 3. Docker での core 導入方式が変わった

Docker イメージでは `hakoniwa-core-full` の apt install ではなく、`hakoniwa-core-pro` の source build / install に切り替わっています。

そのため、Docker 利用時は

- core の取得元 repo
- branch / tag
- install prefix

を Dockerfile の build argument と install 先前提で確認してください。

## アップデート後のセットアップ手順

### 1. `hakoniwa-core-pro` を再ビルド・再インストール

既定値のまま使う場合:

```bash
cd thirdparty/hakoniwa-core-pro
./build.bash
bash install.bash
```

明示的に同じ値を渡す場合:

```bash
cd thirdparty/hakoniwa-core-pro
ASSET_NUM=16 \
CHANNEL_MAX=8192 \
RECV_EVENT_MAX=4096 \
SERVICE_CLIENT_MAX=256 \
SERVICE_MAX=1024 \
CLIENT_NAMELEN_MAX=64 \
SERVICE_NAMELEN_MAX=128 \
./build.bash

ASSET_NUM=16 \
CHANNEL_MAX=8192 \
RECV_EVENT_MAX=4096 \
SERVICE_CLIENT_MAX=256 \
SERVICE_MAX=1024 \
CLIENT_NAMELEN_MAX=64 \
SERVICE_NAMELEN_MAX=128 \
bash install.bash
```

### 2. drone-pro 本体を再ビルド

macOS:

```bash
bash tools/build-mac.bash build
```

Ubuntu:

```bash
bash tools/build-ubuntu.bash build
```

### 3. fleets 関連コンポーネントを再ビルド

fleets viewer / bridge / Python runtime を使う場合は、`hakoniwa-core-pro` の固定上限と shared memory レイアウトを前提にするコンポーネントも揃えて更新してください。

特に次を併用している場合は、再ビルド・再起動を推奨します。

- `work/hakoniwa-pdu-bridge-core`
- `work/hakoniwa-pdu-python`

詳細は `docs/fleets/rebuild-and-restart.md` を参照してください。

### 4. shared memory をクリーンにした上で再起動

実行中プロセスを停止し、旧 shared memory を掴んだままのプロセスが残っていないことを確認してから再起動してください。

fleets launcher を使う場合の例:

```bash
bash tools/launch-fleets-scale-perf.bash <N>
```

## アップデート後の確認項目

### 1. build/install 時のパラメータ確認

`thirdparty/hakoniwa-core-pro/build.bash` / `install.bash` 実行時に、以下が期待値で出ることを確認します。

- `ASSET_NUM is 16`
- `CHANNEL_MAX is 8192`
- `RECV_EVENT_MAX is 4096`
- `SERVICE_CLIENT_MAX is 256`
- `SERVICE_MAX is 1024`
- `CLIENT_NAMELEN_MAX is 64`
- `SERVICE_NAMELEN_MAX is 128`

### 2. 実行時ログで build limit と SHM size を確認

起動時に、以下の 2 系統のログが出ることを確認します。

- `build_limits`
- `shm_sizes`

例:

```text
INFO: hako::create_asset_controller() build_limits asset_num=16 channel_max=8192 recv_event_max=4096 service_client_max=256 service_max=1024 client_namelen_max=64 service_namelen_max=128
INFO: hako::create_asset_controller() shm_sizes master_shm_size=... recv_event_table_size=... service_table_size=... pro_shm_size=...
```

異なるバイナリで値が食い違う場合は、その時点で再ビルド対象が揃っていないと判断できます。

### 3. `external_rpc` / `async_shared` の client 登録確認

Python external RPC を使う場合は、client 名が従来どおり登録できることを確認します。

確認対象の例:

- `DroneSetReadyClient_Drone`
- `DroneSetReadyAsyncSharedClient_Drone_1`

### 4. `mmap-0x101.bin` のサイズ確認

今回の既定値では、`recv-event/service` 用 shared memory は従来の大規模 defaults より大幅に小さくなります。

`N=200` 想定既定値では、`mmap-0x101.bin` は理論上およそ次です。

- `23,327,756 byte`
- 約 `22.25 MiB`
- `ls -lh` ではおおむね `22M` から `23M`

実測例:

- `mmap-0x100.bin`: `2.3M`
- `mmap-0x101.bin`: `22M`
- `mmap-0xff.bin`: `3.9M`

`mmap-0x101.bin` の実測 `22M` は、今回の

- `HAKO_RECV_EVENT_MAX=4096`
- `HAKO_SERVICE_CLIENT_MAX=256`
- `HAKO_SERVICE_MAX=1024`
- `HAKO_CLIENT_NAMELEN_MAX=64`
- `HAKO_SERVICE_NAMELEN_MAX=128`

という既定値と整合します。


## まとめ

v3.8.0 は、`hakoniwa-core-pro` の既定上限を fleets `N=200` 運用に寄せつつ、**共有メモリ不整合を build 時と実行時のログで見つけやすくしたリリース**です。

一方で、今回の変更は shared memory レイアウトに影響するため、**単なる差し替えではなく、再ビルド・再インストール・クリーン再起動が前提**です。

既存環境を更新する場合は、`hakoniwa-core-pro` 本体だけでなく、bridge / Python runtime / fleets 周辺も含めて同じ build limits に揃えてください。
