# Docker イメージの使い方

Docker イメージは保守者が作成し、Docker Hubで公開します。このリポジトリには
Dockerfileやイメージ作成スクリプトを公開しません。

## イメージを取得する

`docker/latest_version.txt`に記載された版をDocker Hubから取得します。

```bash
bash docker/pull-image.bash
```

## コンテナを起動する

```bash
bash docker/run.bash
```

fleets launcher は bridge を `/usr/local/hakoniwa/bin/hakoniwa-pdu-web-bridge` から起動し、
viewer 配信パスは `/opt/hakoniwa-threejs-drone` を優先して使用する。
