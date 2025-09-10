# テスト方法

2機同時飛行テスト

## Ardupilot

### 1. 箱庭起動(docker)

```bash
bash hakoniwa-drone-core/docker/tools/run-hako.bash ardupilot hakoniwa-drone-core/config/pdudef/webavatar-2.json 2
```

### 2. Ardupilot 起動(WSL2)


```bash
bash -x hakoniwa-drone-core/tools/ardupilot/run.bash ardupilot-controllers/c1/ardupilot/ 192.168.2.193 0
```

```bash
 bash -x hakoniwa-drone-core/tools/ardupilot/run.bash ardupilot-controllers/c2/ardupilot 192.168.2.193 1
```

IPアドレスはホストIPアドレス

上記スクリプトでは、以下のポート番号、IPアドレスでMAVLink通信を行うように設定している。
```bash
MAVLINK_OUT_PORT=$((14550 + 10 * INSTANCE))
--out=udp:127.0.0.1:${MAVLINK_OUT_PORT} \
--out=udp:${HOST_IP}:${MAVLINK_OUT_PORT}
```

- １台目は、14550ポート、２台目は14560ポート
- ホスト向けは、Mission Planner用。
- 127.0.0.1 は、dockerコンテナ内のpythonスクリプト用

GPSが有効になってから次のステップへ

### 3. pythonスクリプト実行

```bash
cd hakoniwa-drone-core/drone_api/pymavlink
```

```bash
python3 -m hakosim_mavlink --name Drone --connection udp:127.0.0.1:14550 --type ardupilot
```

```bash
 python3 -m hakosim_mavlink --name Drone1 --connection udp:127.0.0.1:14560 --type ardupilot
 ```

### 4. 動作確認

Mission Plannerで、2台のドローンが離陸し、3角形に移動することを確認する。



## PX4

### 1. 箱庭起動(docker)

```bash
bash hakoniwa-drone-core/docker/tools/run-hako.bash ardupilot hakoniwa-drone-core/config/pdudef/webavatar-2.json 2
```

### 2. PX4 起動(WSL2)


```bash
bash -x hakoniwa-drone-core/tools/px4/run.bash px4-controllers/c1/PX4-Autopilot  0
```

```bash
 bash -x hakoniwa-drone-core/tools/px4/run.bash px4-controllers/c2/PX4-Autopilot  1
```


- １台目は、14540ポート、２台目は14541ポート

GPSが有効になってから次のステップへ

### 3. pythonスクリプト実行

```bash
cd /hakoniwa-drone-core/drone_api/pymavlink
```

```bash
python3 -m hakosim_mavlink --name Drone --connection udp:127.0.0.1:14540 --type px4
```

```bash
 python3 -m hakosim_mavlink --name Drone1 --connection udp:127.0.0.1:14541 --type px4
 ```

### 4. 動作確認

QGCで、2台のドローンが離陸し、3角形に移動することを確認する。
