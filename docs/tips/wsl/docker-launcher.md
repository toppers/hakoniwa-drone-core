[English](docker-launcher.en.md) | 日本語

# TIPS

## WSL2/Docker 環境で launcher を使って起動する

このページでは、`docker/run.bash --launcher ...` を使って、コンテナ起動時に container 内 launcher をそのまま実行する方法を説明します。

## できること

この導線を使うと、WSL2 側から以下を 1 コマンドで起動できます。

- Docker コンテナ
- container 内の launcher script
- container 内の MuJoCo / drone service / bridge

例:

```bash
bash docker/run.bash -p lnx --launcher tools/launch-mujoco-web-bridge-ubuntu.bash
```

## 使い方

基本形は以下です。

```bash
bash docker/run.bash [docker options] --launcher <script> [-- launcher_args...]
```

例:

```bash
bash docker/run.bash --launcher tools/launch-mujoco-web-bridge-ubuntu.bash
```

launcher に引数を渡す場合:

```bash
bash docker/run.bash --launcher tools/launch-fleets-scale-perf.bash -- 100 "" 4
```

## 仕組み

`docker/run.bash` は、Dockerfile の `ENTRYPOINT` を変えずに、`docker run IMAGE <command>` の `<command>` 部分だけを差し替えます。

つまり、

- entrypoint ではバイナリ上書きなどの前処理だけ行う
- その後に container 内で launcher script を実行する

という流れです。

このため、従来の

```bash
bash docker/run.bash
```

の挙動はそのまま維持されます。

## `-p lnx` との組み合わせ

MuJoCo / drone service を OSS 向け配布バイナリで動かす場合は、通常 `-p lnx` を付けます。

```bash
bash docker/run.bash -p lnx --launcher tools/launch-mujoco-web-bridge-ubuntu.bash
```

これは、`lnx` ディレクトリまたは `lnx.zip` を container に渡し、entrypoint で `/usr/local/bin/hakoniwa/linux-*` を更新するためです。

## WSL2 と Docker でのバイナリパス差

`tools/launch-mujoco-web-bridge-ubuntu.bash` は、`HAKO_DRONE_SERVICE_BIN` を以下の順で決定します。

1. 環境変数で明示された値
2. `/usr/local/bin/hakoniwa/linux-main_hako_drone_service`
3. `${PROJECT_ROOT}/lnx/linux-main_hako_drone_service`

このため、

- Docker 内では entrypoint 後の `/usr/local/bin/hakoniwa/...`
- WSL2 直接実行では repo 配下の `lnx/...`

を自動で使い分けできます。

## 非 TTY 実行時の動作

launcher 配下など、非 TTY 実行時の `docker/run.bash` は detached 起動に切り替わります。

これにより、

- parent launcher から安全に起動できる
- `Ctrl+C` 時に container cleanup しやすい

という利点があります。

TTY 動作は `DOCKER_TTY_MODE` で切り替えできます。

```bash
DOCKER_TTY_MODE=auto
DOCKER_TTY_MODE=always
DOCKER_TTY_MODE=never
```

## 終了

launcher 実行中の端末で `Ctrl+C` を押すと、`docker/run.bash` が container を停止します。

残っていないかを確認するには:

```bash
docker ps --filter "name=$(cat docker/image_name.txt)"
```

## 関連ドキュメント

- [WSL2 での Docker セットアップ](docker-setup.md)
- [WSL2/Docker + Windowsゲームパッドで RC Endpoint を使う](docker-rc-endpoint.md)
