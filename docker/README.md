# 目的

`hakoniwa-drone-pro` を clone した直後でも、Docker 内で fleets 構成を起動できるようにする。

## Docker イメージに含めるもの

- `hakoniwa-core-pro` を source build / install した実行環境
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

## hakoniwa-core の導入方式

この Docker イメージでは、`hakoniwa-core-full` debian パッケージは使わず、
`hakoniwa-core-pro` を clone して Dockerfile 内で CMake build / install する。

その際、Docker 内の実行互換性を保つために、インストール先は次の前提に寄せている。

- binary: `/usr/local/hakoniwa/bin`
- config: `/etc/hakoniwa`
- offset: `/usr/share/hakoniwa/offset`

対象リポジトリは `docker/Dockerfile` 内の build argument で切り替えられる。

- `HAKO_CORE_PRO_REPO`
- `HAKO_CORE_PRO_REF`
- `HAKO_PDU_ENDPOINT_REPO`
- `HAKO_PDU_ENDPOINT_REF`
- `HAKO_PDU_BRIDGE_CORE_REPO`
- `HAKO_PDU_BRIDGE_CORE_REF`
- `HAKO_THREEJS_DRONE_REPO`
- `HAKO_THREEJS_DRONE_REF`

各 `*_REF` は実際に checkout される。既定値は相互に検証したcommitへ固定しており、
依存を更新する場合はCore、Endpoint、BridgeのCMake package契約をまとめて確認する。

Bridgeは `docker/config/hakoniwa-pdu-bridge-core.yaml` を使って
`hako.py build/install`する。イメージに必要なWebBridgeだけを有効化し、
tests、examples、monitor、standalone bridgeはDocker imageのビルド対象に含めない。

このDockerイメージの `/usr/local/hakoniwa` は、コンテナ内で完結する実行環境用prefixである。
Business Packから利用する場合のFoundationは、Business Packのworking directory配下へ
`hako.py build/install`で構築する別の契約であり、ホストの`/usr/local/hakoniwa`を前提にしない。
