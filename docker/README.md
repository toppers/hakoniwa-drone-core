# 目的

`hakoniwa-drone-pro` を clone した直後でも、Docker 内で fleets 構成を起動できるようにする。

## Docker イメージに含めるもの

- `hakoniwa-core-full`
- `hakoniwa-pdu-endpoint`（`/usr/local/hakoniwa` に install）
- `hakoniwa-pdu-bridge-core`（`hakoniwa-pdu-web-bridge` を build/install）
- `web_bridge_fleets` config（`/usr/local/hakoniwa/share/hakoniwa-pdu-bridge/config/web_bridge_fleets`）
- `hakoniwa-threejs-drone`（`/opt/hakoniwa-threejs-drone`）
- `hakoniwa-drone-core` 実行バイナリ（OSS 版）

## 使い方

1. イメージ作成

```bash
bash docker/create-image.bash
```

2. コンテナ起動

```bash
bash docker/run.bash
```

fleets launcher は bridge を `/usr/local/hakoniwa/bin/hakoniwa-pdu-web-bridge` から起動し、
viewer 配信パスは `/opt/hakoniwa-threejs-drone` を優先して使用する。
