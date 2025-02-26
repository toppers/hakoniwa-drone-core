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

# Mission Plannerメモ

Mission Planner は Windowsと相性がとても良いので、Windowsを準備しましょう。

## 転送設定方法

Mission Plannerで受信している MAVLinkのUDPパケットは、転送することができます。

まず、CTRL+F を実行すると以下の設定画面が出ます。

![スクリーンショット 2025-02-26 12 07 17](https://github.com/user-attachments/assets/91469353-a403-43f4-b3f1-77482f8bc974)

色々ありますが、左上にある `Mavlink`をクリックします。

![スクリーンショット 2025-02-26 12 08 10](https://github.com/user-attachments/assets/e303826b-109e-4333-bbe8-fbe4e7021a84)

選択リストから、`UDP Client` を選択し、接続をクリック。

![スクリーンショット 2025-02-26 12 09 02](https://github.com/user-attachments/assets/2c0139f7-f7c7-4dad-af0d-ed5ef29a78c1)

転送先のRemote HostのIPアドレスを入力。

![スクリーンショット 2025-02-26 12 09 26](https://github.com/user-attachments/assets/0ae4af96-e34a-4cc1-a880-9802fda3d132)

転送先のUDPポート番号を入力。


