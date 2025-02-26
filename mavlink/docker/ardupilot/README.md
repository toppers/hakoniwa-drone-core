# これは何？

Ardupilot の開発環境を構築するための Docker 環境です。

# 使い方

## Docker イメージのビルド

```bash
cd mavlink/docker/ardupilot
bash create-image.bash
```

## Docker コンテナの起動

```bash
bash run.bash
```

## Docker コンテナへの接続

```bash
bash attach.bash
```

## Ardupilot の起動

ドローンとローバーの起動方法は以下の通りです。

ミッションプランナーのIPアドレスを out オプションで指定してください。

### ArduCopter

```bash
 ./Tools/autotest/sim_vehicle.py  -v ArduCopter --out=udp:192.168.2.107:14550
```

### Rover

```bash
 ./Tools/autotest/sim_vehicle.py  -v Rover --out=udp:192.168.2.107:14550
```

