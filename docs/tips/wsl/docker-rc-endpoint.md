[English](docker-rc-endpoint.en.md) | 日本語

# TIPS

## WSL2/Docker + Windowsゲームパッドで RC Endpoint を使う

この手順は、以下の構成を前提にしています。

- シミュレータ本体: WSL2/Ubuntu 上の Docker コンテナ
- Web bridge / drone service: コンテナ内で起動
- ゲームパッド入力: Windows 側 Python で `rc-endpoint.py` を実行
- 全体起動: WSL2 側 launcher で統合実行

## 前提

- Windows 11
- WSL2 / Ubuntu
- WSL2 内で docker が利用可能
- PS4 / PS5 系コントローラを Windows に接続済み
- 事前に `hakoniwa-drone-core` と `hakoniwa-pdu-endpoint` を clone 済み
- `hakoniwa-drone-core` と `hakoniwa-pdu-endpoint` を同じ親ディレクトリ配下に配置

例:

```bash
/home/<user>/project/hakoniwa-drone-core
/home/<user>/project/hakoniwa-pdu-endpoint
```

例:

```bash
cd /home/<user>/project
git clone https://github.com/toppers/hakoniwa-drone-core.git
git clone https://github.com/hakoniwalab/hakoniwa-pdu-endpoint.git
```

## 1. Docker 側の準備

WSL2 側でコンテナ起動ができる状態にしてください。

```bash
bash docker/run.bash -p lnx
```

`lnx` の配置や docker 自体のセットアップは以下を参照してください。

- [WSL2 での Docker セットアップ](docker-setup.md)
- [バイナリ ZIP の入手方法](../../../README.md#-バイナリの入手方法)

## 2. Windows 側 RC 実行環境のインストール

WSL2 側で以下を実行します。

```bash
bash tools/install-rc-endpoint-win.bash 'C:\project\rc-endpoint'
```

このコマンドは以下を行います。

- `C:\project\rc-endpoint` に `rc-endpoint.py` と関連 config をコピー
- Windows 側に `pygame` をインストール
- 隣接 repo の `hakoniwa-pdu-endpoint/install-python-win.ps1` を呼び出し、
  `hakoniwa-pdu` / `hakoniwa-pdu-endpoint` / runtime bundle をインストール
- `launch-rc-endpoint-win.ps1` を生成

既定の配置先 `%LOCALAPPDATA%\Hakoniwa\rc-endpoint` を使う場合は、引数なしでも実行できます。

```bash
bash tools/install-rc-endpoint-win.bash
```

## 3. 統合 launcher で起動

WSL2 側で以下を実行します。

```bash
bash tools/launch-docker-mujoco-web-bridge-rc.bash
```

この launcher は以下を起動します。

- `before_start`
  - `docker/run.bash -p lnx --launcher tools/launch-mujoco-web-bridge-ubuntu.bash`
- `after_start`
  - Windows 側 `launch-rc-endpoint-win.ps1`

## 4. 終了

統合 launcher を実行している WSL2 端末で `Ctrl+C` を押してください。

現在の実装では、終了時に以下もまとめて停止します。

- launcher 配下の Windows RC プロセス
- Docker コンテナ

## 5. 主な環境変数

RC 側の既定値を変更したい場合は、WSL2 側で環境変数を付けて起動できます。

```bash
RC_ENDPOINT_INSTALL_DIR_WIN='C:\project\rc-endpoint' \
RC_ENDPOINT_RC_CONFIG='drone_api/rc/rc_config/ps4-control.json' \
RC_ENDPOINT_PERIOD_SEC='0.01' \
bash tools/launch-docker-mujoco-web-bridge-rc.bash
```

主な変数:

- `RC_ENDPOINT_INSTALL_DIR_WIN`
- `RC_ENDPOINT_LAUNCHER_WIN`
- `RC_ENDPOINT_RC_CONFIG`
- `RC_ENDPOINT_ROBOT_NAME`
- `RC_ENDPOINT_JOYSTICK_INDEX`
- `RC_ENDPOINT_PERIOD_SEC`

### コントローラ設定の切り替え

既定のコントローラ設定は `drone_api/rc/rc_config/ps4-control.json` です。

PS5 など別のコントローラを使う場合は、`RC_ENDPOINT_RC_CONFIG` を切り替えてください。

例:

```bash
RC_ENDPOINT_RC_CONFIG='drone_api/rc/rc_config/ps5-control.json' \
bash tools/launch-docker-mujoco-web-bridge-rc.bash
```

Windows 側 launcher を直接起動する場合は、`-RcConfig` でも変更できます。

```powershell
.\launch-rc-endpoint-win.ps1 -RcConfig 'drone_api/rc/rc_config/ps5-control.json'
```

利用可能な設定ファイルは主に以下です。

- `drone_api/rc/rc_config/ps4-control.json`
- `drone_api/rc/rc_config/ps5-control.json`
- `drone_api/rc/rc_config/hori4mini-control.json`

必要に応じて `drone_api/rc/rc_config/` 配下へ独自設定を追加してください。

## トラブルシュート

### `launch-rc-endpoint-win.ps1` が見つからない

インストール先が既定値と異なる場合は、`RC_ENDPOINT_INSTALL_DIR_WIN` を指定してください。

```bash
RC_ENDPOINT_INSTALL_DIR_WIN='C:\project\rc-endpoint' \
bash tools/launch-docker-mujoco-web-bridge-rc.bash
```

### Windows installer で DLL コピーに失敗する

`hakoniwa_pdu_endpoint.dll` を使っている Python プロセスが残っている可能性があります。
Windows 側で RC 実行中の Python を停止してから再実行してください。

### joystick のイベントログが出ない

インストール済みの `rc-endpoint.py` が古い可能性があります。再度以下を実行してください。

```bash
bash tools/install-rc-endpoint-win.bash 'C:\project\rc-endpoint'
```

## 関連ドキュメント

- [WSL2 での Docker セットアップ](docker-setup.md)
- [WSL2/Docker 環境で launcher を使って起動する](docker-launcher.md)
