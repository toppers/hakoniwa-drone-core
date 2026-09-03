# MuJoCo + PX4 + pymavlink + Three.js（WSL2 / Docker）

WSL2 上で PX4 SITL を起動し、Docker コンテナ内の `hakoniwa-drone-core` と接続して、
Python `pymavlink` から速度指令を送るための手順です。シミュレーション中の機体状態は
Three.js のブラウザビューアで確認できます。

## このドキュメントでできること

- PX4 SITL を WSL2 上で実行する
- MuJoCo のドローンモデルを `hakoniwa-drone-core` でシミュレーションする
- PX4 の Offboard モードへ `pymavlink` から速度指令を送る
- `vx`, `vy`, `vz` による機体移動を確認する
- Drone Core の状態を PDU 経由で取得する
- WebBridge 経由で状態を WebSocket 配信する
- Windows のブラウザ上の Three.js viewer でドローンの移動を可視化する

この構成では、Three.js はビジュアライザです。速度指令はブラウザからではなく、
コンテナへ attach した後に実行する `pymavlink` プログラムから送ります。

## 0. 最初の準備

WSL2 のホームディレクトリなどにワークスペースを作り、その下へリポジトリをcloneします。

```bash
mkdir -p ~/workspace
cd ~/workspace
git clone https://github.com/toppers/hakoniwa-drone-core.git
cd hakoniwa-drone-core
```

既にclone済みの場合は、既存のリポジトリを使用してください。PX4-Autopilotも同じ
ワークスペース配下に置くと、パス管理が簡単になります。

```text
~/workspace/
├─ hakoniwa-drone-core/
└─ px4-controllers/
   └─ c1/PX4-Autopilot/
```

## PX4 のインストールとビルド

PX4-Autopilotをまだ取得していない場合は、サブモジュールを含めてcloneします。

```bash
cd ~/workspace
mkdir -p px4-controllers/c1
git clone --recursive \
  https://github.com/PX4/PX4-Autopilot.git \
  px4-controllers/c1/PX4-Autopilot
```

PX4のビルドは、`hakoniwa-drone-core`のスクリプトへPX4ディレクトリを引数として渡します。
このコマンドは`~/workspace`から実行してください。

```bash
cd ~/workspace
bash hakoniwa-drone-core/tools/px4/build.bash \
  px4-controllers/c1/PX4-Autopilot
```

ビルドが完了すると、次のPX4 SITL実行ファイルが生成されます。

```text
px4-controllers/c1/PX4-Autopilot/build/px4_sitl_default/bin/px4
```

ビルド依存パッケージやWSL2固有の準備で問題が出た場合は、
[`../../docs/tips/wsl/px4-setup.md`](../../docs/tips/wsl/px4-setup.md)とPX4公式の
WSL2セットアップ手順を確認してください。

## アーキテクチャ

```text
WSL2: PX4 SITL
  └─ MAVLink TCP 127.0.0.1:4560
       │
Docker: hakoniwa-drone-core
  ├─ MuJoCo + PX4 aircraft service
  ├─ DroneVisualStatePublisher
  ├─ WebBridge
  └─ Three.js HTTP server
       │
       └─ pymavlink（attach 後に手動実行）
```

## 必要なツールと環境

- WSL2 / Ubuntu
- Docker Engine または Docker Desktop の WSL2 integration
- Git
- CMake、GCC/G++、Make（PX4やDockerイメージを自分でビルドする場合）
- PX4-Autopilot の SITL ビルド済みディレクトリ
- Python 3（Dockerイメージ内に含まれる。ローカルでpymavlinkを動かす場合はPython 3.12推奨）
- `pymavlink`（Dockerイメージに含まれる）
- Windows 側のWebブラウザ
- QGroundControl（QGC、PX4状態確認用。推奨・任意）
- WSLgまたはX11（MuJoCoのネイティブGUIを表示する場合のみ。ブラウザ表示だけなら不要）

PX4 のビルド方法は [`../../docs/tips/wsl/px4-setup.md`](../../docs/tips/wsl/px4-setup.md) を参照してください。

Dockerイメージを自分で作成する場合は、インターネット接続とDockerのビルド機能も必要です。

### QGroundControl

Windows側にQGroundControlをインストールしておくと、PX4 SITLの状態をGUIで確認できます。
今回の速度指令は`pymavlink`から送るため、QGCは必須ではありませんが、次の確認に便利です。

- PX4 heartbeatの受信
- GPS / HOME位置の初期化
- ARM状態とFlight Mode
- Offboard遷移
- failsafeやリンク切断の状態

QGCはWindows側で起動し、GCS用UDP `14550`を監視します。`14540`はこのサンプルの
Offboard API（pymavlink）が接続するOnboard MAVLinkポートで、QGC用とは役割が異なります。
接続設定は実際のPX4コンソールに表示されるMAVLink設定を優先してください。

## 使用する主な設定・プログラム

| 役割 | ファイル / コンポーネント |
|---|---|
| PX4接続設定 | `config/drone/mujoco-px4-1/drone_config_0.json` |
| 1機用PDU定義 | `config/pdudef/drone-pdudef-1.json` |
| MuJoCoモデル | `config/drone/mujoco-ardupilot-1/drone.xml`（PX4設定内の`modelPath`が参照） |
| Docker起動 | `docker/run.bash` |
| コンテナ接続 | `docker/attach.bash` |
| Docker内Launcher | `tools/launch-mujoco-px4-web-bridge-wsl2.bash` |
| Launcher設定 | `config/launcher/mujoco-px4-web-bridge-wsl2.launch.json` |
| 速度指令サンプル | `px4-sample2.py` |
| ブラウザ表示 | `hakoniwa-threejs-drone` |

### この1台構成で使うMuJoCo定義

現在のLauncher [`config/launcher/mujoco-px4-web-bridge-wsl2.launch.json`](../../config/launcher/mujoco-px4-web-bridge-wsl2.launch.json)
は、Drone Serviceへ次のディレクトリを渡します。

```text
config/drone/mujoco-px4-1/
└─ drone_config_0.json
```

この`drone_config_0.json`のMuJoCo設定は次の内容です。

```json
{
  "physicsEquation": "MuJoCo",
  "mujoco": {
    "modelName": "d1_drone_base",
    "propNames": ["d1_prop1", "d1_prop2", "d1_prop3", "d1_prop4"],
    "modelPath": "config/drone/mujoco-ardupilot-1/drone.xml"
  }
}
```

つまり、設定ディレクトリは`mujoco-px4-1`ですが、実際にロードされるXMLは
`config/drone/mujoco-ardupilot-1/drone.xml`です。このXMLには`d1_drone_base`と
`d1_prop1`〜`d1_prop4`が定義されており、`modelName`／`propNames`と一致している必要があります。

なお、単体MuJoCo（PX4なし）の設定では`config/drone/mujoco/drone_config_0.json`が
`config/drone/mujoco/drone.xml`を参照します。今回のPX4構成ではこちらは使用しません。

## 1. Docker イメージを取得する

`hakoniwa-drone-core/docker/Dockerfile` で使用しているイメージを取得します。
このイメージには MuJoCo、Hakoniwa Core、PDU Endpoint、Bridge Core、
VisualStatePublisher 用バイナリ、Three.js viewer、`pymavlink` が含まれています。

```bash
cd ~/workspace/hakoniwa-drone-core
bash docker/pull-image.bash
```

イメージを自分で作成する場合は、次を使用します。

```bash
bash docker/create-image.bash
```

## 2. PX4 SITL を WSL2 で起動する

PX4 は Docker より先に起動します。`tools/px4/run.bash` は親ワークスペースから実行する形式です。

```bash
cd ~/workspace
bash hakoniwa-drone-core/tools/px4/run.bash \
  px4-controllers/c1/PX4-Autopilot 0
```

PX4 のコンソールにシミュレータ接続待ちまたは起動完了が表示されるまで待ちます。

この1台構成の接続契約は次のとおりです。

| 用途 | 接続先 |
|---|---|
| PX4 simulator link（Drone Serviceが接続） | TCP `127.0.0.1:4560` |
| PX4 Offboard API（pymavlinkが接続） | UDP `127.0.0.1:14540` |
| PX4 GCS（QGroundControl） | UDP `127.0.0.1:14550` |

`14540`はPython側の接続文字列で待ち受けるポート、`14550`はPX4がGCSへ送信する宛先です。
PX4ログに別のlisten/remoteポートが表示される場合は、実際のログを優先してください。

## 3. Docker 内の Hakoniwa runtime を起動する

別の WSL2 ターミナルで実行します。

```bash
cd ~/workspace/hakoniwa-drone-core
bash docker/run.bash \
  --launcher tools/launch-mujoco-px4-web-bridge-wsl2.bash
```

このLauncherは次の順に起動します。

1. MuJoCo + PX4 Drone Service
2. DroneVisualStatePublisher
3. `web_bridge_fleets`
4. シミュレーション開始
5. Three.js HTTP server（TCP `8000`）

WSL2 では `docker/run.bash` が host network を選択するため、Docker内のDrone Serviceから
WSL2上のPX4へ `127.0.0.1:4560` で接続します。

## 4. コンテナへ attach する

さらに別のターミナルで実行します。

```bash
cd ~/workspace/hakoniwa-drone-core
bash docker/attach.bash
```

コンテナ内ではプロジェクトが `/root/workspace` にマウントされています。

## 5. pymavlink で速度指令を送る

コンテナ内で実行します。

```bash
cd /root/workspace/drone_api/mavsdk
python3 px4-sample2.py --udp udp:127.0.0.1:14540
```

成功時の最初の表示例:

```text
[INFO] Connecting: udp:127.0.0.1:14540
[INFO] Heartbeat from sys 1 comp 0
[INFO] OFFBOARD started
```

このサンプルは次の操作を行います。

1. PX4 heartbeat 待ち
2. Offboard 切り替え前に位置setpointを1.5秒（20Hz）送信
3. ARM
4. Offboard モード開始
5. 速度setpointによる離陸
6. `LOCAL_POSITION_NED.x/y`を確認しながら、一辺10m・合計30mの三角移動
7. LAND

速度指令は `MAV_FRAME_LOCAL_NED` の `vx`, `vy`, `vz` です。`vz < 0` が上昇方向です。
Offboard では setpoint の継続送信が必要なため、サンプルは一定周期で指令を送ります。

速度指令部分を再利用する場合は、[`px4-sample2.py`](./px4-sample2.py) の
`send_vel_ned()` と `hold_vel()` を参照してください。

### コードの概要

`px4-sample2.py`は、PX4のMAVLink UDPエンドポイントへ接続し、次の処理を行う小さな
単一機体用サンプルです。

- `connect()`
  - `mavutil.mavlink_connection()`で接続し、heartbeatを待つ
- `arm()`
  - `MAV_CMD_COMPONENT_ARM_DISARM`を送る
  - ACKを待ってsetpoint streamを止めない
- `set_mode_offboard()`
  - `MAV_CMD_DO_SET_MODE`でPX4をOffboardへ切り替える
- `send_vel_ned()`
  - `SET_POSITION_TARGET_LOCAL_NED`を送る
  - `MAV_FRAME_LOCAL_NED`を使用する
  - `MASK_VEL_YAW = 0x09C7`で速度（vx/vy/vz）とyawだけを有効にする
- `hold_vel()`
  - Offboardのsetpoint切れを防ぐため、指定Hzで速度指令を繰り返す
- `takeoff()`
  - 上向きの速度setpointを継続送信して離陸する
  - `LOCAL_POSITION_NED.z`を監視し、目標高度に到達した場合だけ成功扱いにする
  - 高度に到達しなければ水平速度デモへ進まずエラーにする（lockstepのため最大60秒待機）
- `land()`
  - `MAV_CMD_NAV_LAND`で着陸させる

速度は次の意味です。

```text
vx: North方向 [m/s]
vy: East方向  [m/s]
vz: Down方向  [m/s]
```

そのため、`vz < 0`は上昇、`vz > 0`は下降です。Offboardでは一定周期のsetpoint送信が
必要なので、単発のMAVLink送信ではなく`hold_vel()`のようなループを使います。

離陸処理を別の制御プログラムから再利用する場合は、次のように呼び出します。

```python
takeoff(m, t0, height_m=2.0, climb_speed_m_s=0.8)
```

`takeoff()`はPX4のOffboardモードへ切り替えた後に呼び出します。PX4はOffboardへ入る前に
2Hz超のsetpointを1秒超受信する必要があります。サンプルは互換性を優先し、1.5秒間の
位置setpoint送信→ ARM → Offboard → `takeoff()`の順で実行します。既定の離陸高度は2.0mで、
開始時の`LOCAL_POSITION_NED.z`を基準に判定します。ARM/OFFBOARDのACKは
非ブロッキングで扱い、setpoint streamを途切れさせません。

### 速度指令デモの流れ

離陸後は位置移動ではなく、`hold_vel()`で速度を継続送信します。

```python
hold_vel(m, t0, vx=5.0, vy=0.0, vz=0.0, yaw_deg=0.0, seconds=2.0, hz=10.0)
hold_vel(m, t0, vx=-2.5, vy=4.330, vz=0.0, yaw_deg=0.0, seconds=2.0, hz=10.0)
hold_vel(m, t0, vx=-2.5, vy=-4.330, vz=0.0, yaw_deg=0.0, seconds=2.0, hz=10.0)
```

各速度ベクトルの大きさは約5m/sです。実装では各頂点に到達するまで送信するため、各辺は10m、
合計移動距離は約30mです（上記の2秒は理想速度時の目安です）。

`MASK_VEL_YAW`はMAVLink `POSITION_TARGET_TYPEMASK`の定義に従い、位置（bits 0--2）、
加速度/force（bits 6--9）、yaw_rate（bit 11）をignoreし、速度（bits 3--5）とyaw
（bit 10）だけを有効にする`0x09C7`です。

## 6. Three.js で状態を確認する

Windows 側のブラウザで次のURLを開き、画面の `Connect` を押します。

```text
http://127.0.0.1:8000/index.html?viewerConfigPath=/config/viewer-config-fleets.json&wsUri=ws://127.0.0.1:8765&wireVersion=v2
```

1機構成では`dynamicSpawn`、`templateDroneIndex`、`maxDynamicDrones`は不要です。これらは
複数機を動的生成するfleets quickstart用のオプションです。

使用するポートは次のとおりです。

- HTTP viewer: `127.0.0.1:8000`
- WebBridge WebSocket: `127.0.0.1:8765`

ブラウザ上のドローン状態が更新され、速度指令に対応して機体が移動すれば、
PX4 → Drone Core / MuJoCo → PDU → WebBridge → Three.js の経路が確認できています。

## 停止手順

1. pymavlink スクリプトを `Ctrl+C` で停止
2. attach shell から `exit`
3. Docker Launcher のターミナルで `Ctrl+C`
4. PX4 のターミナルを `Ctrl+C` で停止

Launcher の終了後、必要に応じて次を確認します。

```bash
docker ps
ss -ltnp | rg '8000|8765'
```

他のユーザー・プロセスを巻き込む広域な `kill` は使用しないでください。

## トラブルシュート

### Heartbeat が来ない

まず PX4 のOnboard MAVLinkポートを確認します。PX4の本構成では機体0は通常 `14540` です。

```bash
ss -lunp | rg '14540|14550'
```

`14550` はQGCなどGCS向けの宛先です。pymavlinkの接続先はこのレシピでは`14540`です。

### Drone Service が終了する

- PX4 が先に起動しているか確認する
- PX4 simulator link が `127.0.0.1:4560` で待機しているか確認する
- DockerがWSL2のhost networkで起動しているか確認する
- `config/drone/mujoco-px4-1` と `config/pdudef/drone-pdudef-1.json` が存在するか確認する

### ブラウザが表示されない

- Docker Launcherが終了していないか確認する
- TCP `8000` と `8765` がlistenしているか確認する
- URLの `viewerConfigPath`、`wsUri`、`wireVersion=v2` が一致しているか確認する
- ブラウザ画面の `Connect` を押す

### 速度指令を変更したい

`px4-sample2.py` の `hold_vel()` 呼び出しを変更します。

```python
hold_vel(m, t0, vx=1.0, vy=0.0, vz=0.0,
         yaw_deg=0.0, seconds=5.0, hz=10.0)
```

座標系はLocal NEDです。実機接続や物理機体へのARMを行う手順ではなく、PX4 SITLとMuJoCoのシミュレーション専用です。
