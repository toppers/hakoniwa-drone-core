# Hakoniwa Drone Simulator v3.6.1 → v3.7.0 アップデート手順

## はじめに

Hakoniwa Drone Simulator v3.7.0 では、**箱庭の新しい endpoint アーキテクチャを使って、WSL2/Docker 上の MuJoCo シミュレータを Windows 側のゲームパッドから RC 操作できる統合導線**を追加しました。

今回の要となるのは、`hakoniwa-pdu-endpoint` です。

`hakoniwa-pdu-endpoint` は、Hakoniwa PDU 通信を Python から直接扱うための endpoint 基盤であり、

- endpoint を開く
- PDU をそのまま送受信する
- WebSocket bridge や shared memory などの transport と接続する

ための低レベルな接続点を提供します。

今回のアップデートでは、この endpoint 基盤を利用することで、

- Windows 側でしか安定認識しにくい `pygame + PS4/PS5 controller`
- WSL2/Ubuntu 上の Docker コンテナで動作する MuJoCo / drone service / web bridge

を、OS 境界をまたいで一体運用できるようにしました。

従来、この種の構成で Linux 側からゲームパッドを直接扱おうとすると、

- `usbipd-win` による USB デバイスの WSL2 アタッチ
- WSL2 側でのコントローラ認識確認
- `pygame` / SDL の Linux 側入力相性対応

が必要になり、セットアップと運用の負担が大きいという課題がありました。

v3.7.0 では、コントローラ入力を Windows 側で安定して扱い、その結果だけを endpoint bridge で箱庭へ渡す構成にしたことで、
この pain point を大きく減らしています。

今回のリリースでは、単に `rc-endpoint.py` を追加しただけではなく、

- Docker 側の MuJoCo / drone service / web bridge 起動
- Windows 側の RC endpoint 実行環境インストール
- WSL2 launcher からの統合起動
- `Ctrl+C` 時の Docker cleanup
- RC ログの標準出力連携

までを一連の運用フローとして整備しています。

本ドキュメントでは、v3.6.1 から v3.7.0 へ更新する際の変更点と確認項目を説明します。

## v3.7.0 の新機能・変更点

今回のバージョンアップの中心は、**箱庭の endpoint アーキテクチャを使った、MuJoCo + Docker/WSL2 + Windows gamepad の実運用導線の追加**です。

今回の価値は、単に Windows でゲームパッドが使えるようになったことではありません。

- Windows ネイティブ入力
- WSL2 上の Linux 環境
- Docker コンテナ内の MuJoCo シミュレータ
- WebSocket bridge
- Hakoniwa PDU endpoint

を、launcher ベースで一体運用できるようにした点が本質です。

特に `pygame + PS4/PS5 controller` は、現実的には Windows 側で扱う方が安定します。
一方でシミュレータ本体は、WSL2/Docker 側で動かしたいケースが多くあります。

v3.7.0 では、この分断されやすい構成を `hakoniwa-pdu-endpoint` により bridge 接続し、
箱庭の新しいアーキテクチャとして統合しました。

この構成により、`usbipd-win` を前提に WSL2 側へゲームパッドを直接渡す方式に比べて、

- 導入手順が短い
- Windows 側での入力安定性を保てる
- Linux 側はシミュレータ実行に集中できる

という運用上の利点があります。

- RC endpoint ベースの Windows gamepad 操作対応
  - `drone_api/rc/rc-endpoint.py`
  - `config/endpoint/*`
  - `config/pdudef/webavatar.json`
- Windows 側 RC installer を追加
  - `tools/install-rc-endpoint-win.bash`
  - `rc-endpoint.py` / `rc_config` / endpoint config 一式を Windows 側へ配置
  - 隣接 repo の `hakoniwa-pdu-endpoint/install-python-win.ps1` を呼び出し
- 複数コントローラ設定の切り替えに対応
  - 既定は `drone_api/rc/rc_config/ps4-control.json`
  - `RC_ENDPOINT_RC_CONFIG` または `-RcConfig` で切り替え可能
  - PS4 / PS5 / HORI など `rc_config` 差し替えで対応
- WSL2 統合 launcher を追加
  - `tools/launch-docker-mujoco-web-bridge-rc.bash`
  - `config/launcher/docker-mujoco-web-bridge-rc-win.launch.json`
  - `tools/launch-rc-endpoint-win.bash`
- MuJoCo + web bridge の Docker 起動導線を整理
  - `docker/run.bash --launcher ...`
  - `tools/launch-mujoco-web-bridge-ubuntu.bash`
  - `config/launcher/drone-mujoco-web-bridge-ubuntu.launch.json`
- Docker launcher 運用の安定化
  - 非 TTY 実行時は detached 起動
  - `Ctrl+C` / launcher abort 時の container cleanup を追加
- Windows RC ログの可視化改善
  - `rc-endpoint` の axis / button event を標準出力へ表示
  - `python -u` / `PYTHONUNBUFFERED=1` によるバッファ抑制
- MuJoCo viewer のリサイズ追従
  - fixed viewport を廃止し、framebuffer size を毎フレーム反映

## 前提とする環境

- Windows 11
- WSL2 / Ubuntu
- WSL2 内で docker が利用可能
- PS4 / PS5 系コントローラ
- 箱庭ドローンシミュレータのアーキテクチャパターン:
  - コンテナパターン
  - Windows host + WSL2 + Docker の混在運用

## アップデート対象リポジトリ

- hakoniwa-drone-core
  - target version: v3.7.0

既存のローカル変更がある場合は先に退避してください。

`hakoniwa-drone-core` 配下で以下を実行します。

```bash
git fetch --tags
git checkout v3.7.0
git submodule update --init --recursive
```

> `main` を使う運用の場合は `git pull origin main` でも可。

## 関連リポジトリ

v3.7.0 では、Windows 側 RC 実行環境のために以下も利用します。

- hakoniwa-pdu-endpoint
  - GitHub URL: https://github.com/hakoniwalab/hakoniwa-pdu-endpoint

`hakoniwa-drone-core` と `hakoniwa-pdu-endpoint` は、同じ親ディレクトリ配下に clone してください。

例:

```bash
cd /home/<user>/project
git clone https://github.com/toppers/hakoniwa-drone-core.git
git clone https://github.com/hakoniwalab/hakoniwa-pdu-endpoint.git
```

## 配布バイナリと Docker イメージ

OSS 向けの配布バイナリは `hakoniwa-drone-core` 側の Releases を前提とします。

- Linux 用配布バイナリ: `lnx.zip`
- リリース URL: https://github.com/toppers/hakoniwa-drone-core/releases

Docker イメージも更新してください。

```bash
bash docker/pull-image.bash
```

確認:

```bash
docker images | grep hakoniwa-drone-core
```

## v3.7.0 で特に注意すべき互換ポイント

### 1. Windows RC 実行には `hakoniwa-pdu-endpoint` が追加で必要

従来の `hakoniwa-drone-core` 単体 clone では、Windows 側 `rc-endpoint.py` 実行環境は完結しません。

v3.7.0 では、WSL2 側 RC installer が隣接 repo の
`hakoniwa-pdu-endpoint/install-python-win.ps1`
を呼び出す前提です。

### 2. 統合起動の入口が launcher ベースになった

今回の推奨起動方法は、個別に

- `docker/run.bash ...`
- PowerShell で `rc-endpoint.py`

を別々に起動する方法ではなく、以下の統合 launcher です。

```bash
bash tools/launch-docker-mujoco-web-bridge-rc.bash
```

### 3. Docker launcher 実行時の非 TTY 動作が変わった

`docker/run.bash` は、launcher 配下などの非 TTY 実行時に detached 起動へ切り替わります。
これにより、`Ctrl+C` 時に container が残る問題を回避しています。

## アップデート後のセットアップ手順

### 1. Linux 配布バイナリを配置

`hakoniwa-drone-core` 配下に `lnx/` または `lnx.zip` を配置してください。

### 2. Windows 側 RC 実行環境をインストール

WSL2 側で以下を実行します。

```bash
bash tools/install-rc-endpoint-win.bash 'C:\project\rc-endpoint'
```

このコマンドは以下を行います。

- Windows 側へ `rc-endpoint.py` と関連 config をコピー
- Windows 側へ `pygame` をインストール
- `hakoniwa-pdu-endpoint` 側 installer を呼び出し
- `hakoniwa-pdu` / `hakoniwa-pdu-endpoint` / runtime bundle をインストール
- `launch-rc-endpoint-win.ps1` を生成

### 3. 統合 launcher で起動

```bash
bash tools/launch-docker-mujoco-web-bridge-rc.bash
```

コントローラ設定を切り替える場合は、`RC_ENDPOINT_RC_CONFIG` を指定してください。

例:

```bash
RC_ENDPOINT_RC_CONFIG='drone_api/rc/rc_config/ps5-control.json' \
bash tools/launch-docker-mujoco-web-bridge-rc.bash
```

## アップデート後の確認項目

### 1. Docker 内 MuJoCo / web bridge 起動確認

以下で container 側が起動することを確認します。

```bash
bash docker/run.bash -p lnx --launcher tools/launch-mujoco-web-bridge-ubuntu.bash
```

### 2. Windows 側 RC 単体起動確認

以下で Windows 側 RC launcher が起動することを確認します。

```bash
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\project\rc-endpoint\launch-rc-endpoint-win.ps1"
```

### 3. 統合 launcher 起動確認

以下で Docker 側と Windows 側がまとめて起動することを確認します。

```bash
bash tools/launch-docker-mujoco-web-bridge-rc.bash
```

確認ポイント:

- MuJoCo viewer が起動する
- Windows 側 gamepad 入力で機体が反応する
- `axis event` / `button event` が標準出力に出る

### 4. 終了確認

統合 launcher 実行中に `Ctrl+C` して、Docker コンテナが残らないことを確認します。

```bash
docker ps --filter "name=$(cat docker/image_name.txt)"
```

## 参考ドキュメント

- [WSL2/Docker + Windowsゲームパッドで RC Endpoint を使う](./tips/wsl/docker-rc-endpoint.md)
- [WSL2 での Docker セットアップ](./tips/wsl/docker-setup.md)
- [コンテナパターンのチュートリアル](./getting_started/container.md)

## v3.7.0 の成果サマリ

今回のリリースで、以下の導線が成立しました。

- WSL2/Ubuntu 上の Docker コンテナで MuJoCo シミュレータを起動
- Windows 側のゲームパッド入力を `rc-endpoint.py` で送信
- launcher ベースで Docker と Windows RC を一体運用
- `Ctrl+C` で後始末まで含めて停止

つまり v3.7.0 は、**MuJoCo を RC 操作で Windows 連携しながら実運用できるようにしたリリース**です。
