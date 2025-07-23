# 箱庭ドローンシミュレータの使い方

箱庭ドローンシミュレータは、用途に応じて、箱庭なしで利用するケースと箱庭ありで利用するケースがあります。

- 箱庭なしで利用する場合は、物理モデルと制御モデルを独立して実行することが可能です。
- 箱庭ありで利用する場合は、Unityとの連携やデジタルツインとの連携が可能になります。

## 箱庭なしで利用するケース

箱庭なしで利用する場合、箱庭ドローンの物理モデルと制御モデルを独立して実行することが可能です。

補足：箱庭との連携がありませんので、Unityでのビジュアライズはできません。

提供バイナリとしては以下のものがあります。

1. PX4 連携サンプルアプリ(<os名>-aircraft_service_px4)
2. Ardupilot 連携サンプルアプリ(<os名>-aircraft_service_ardupilot)
3. 箱庭ドローンのCUIサンプルアプリ(<os名>-drone_servce_rc)
4. 箱庭ドローンPro Cライブラリ(hako_service_c)

全てクロスプラットフォーム対応しています。リリースページにあるバイナリをダウンロードしてください。

os名は、以下の通りです。

- mac
- win
- linux

### PX4 連携サンプルアプリの利用方法

PX4 連携サンプルアプリを使うと箱庭ドローンシミュレータの物理モデルとPX4を連携することが可能です。

実行方法：
```bash
<os名>-aircraft_service_px4 <IPアドレス> 4560 ./config/drone/px4 
```

この際、PX4を起動することで、PX4と連携することが可能です。

参考：https://github.com/toppers/hakoniwa-px4sim?tab=readme-ov-file#terminal-a

あわせて、QGCと連携することで、遠隔操作が可能です。


### Ardupilot 連携サンプルアプリの利用方法

Ardupilot 連携サンプルアプリを使うと箱庭ドローンシミュレータの物理モデルとArdupilotを連携することが可能です。

実行方法：
```bash
<os名>-aircraft_service_ardupilot <ホストPCのIPアドレス> 9002 9003 ./config/drone/ardupilot 
```

この際、Ardupilotを起動することで、Ardupilotと連携することが可能です。

```bash
./Tools/autotest/sim_vehicle.py -v ArduCopter -f airsim-copter -A "--sim-port-in 9003 --sim-port-out 9002"  --sim-address=<ホストPCのIPアドレス>  --out=udp:<Mission PlannerのIPアドレス>:14550
```

参考：https://github.com/ArduPilot/ardupilot

この際、Mission Plannerと連携することで、遠隔操作が可能です。

### 箱庭ドローンのCUIサンプルアプリの利用方法

箱庭ドローンシミュレータの物理モデルと制御モデルを連携させて、CUIで操作することが可能です。

```bash
service/drone_service_rc 1 config/drone/rc
```

```
 ----- USAGE -----
 ----- STICK -----
|  LEFT  | RIGHT  |
|   w    |   i    |
| a   d  | j   l  |
|   s    |   k    |
 ---- BUTTON ----
 x : radio control button
 p : get position
 r : get attitude
 t : get simtime usec
 f : flip
 b : get battery status
```


実行例：起動直後のログ
```bash
BatteryModelCsvFilePath: ./tmp_battery_model.csv
BatteryModelCsvFilePath does not exist.
Angle rate control is disabled
Angle rate control is disabled
flip_target_time_sec: 0.4
flip_constant_time_sec: 0.1
target_angular_rate_rad_sec: 25.1327
target_angular_rate_delta: 0.167552
target_angular_inc_time_sec: 0.15
target_angular_dec_time_sec: 0.25
INFO: mixer is enabled
timestep_usec: 1000
DroneService::startService: 1000
> Start service
```

この状態で、アームするには、`x`を入力しエンターキーを押下します。

その後、`w`を入力しエンターキーを押下することで、上昇します。

実行例：アームして上昇
```bash
> Start service
x
w
position x=0.0 y=-0.0 z=0.1
position x=0.0 y=-0.0 z=0.2
position x=0.0 y=-0.0 z=0.3
position x=0.0 y=-0.0 z=0.4
position x=0.0 y=-0.0 z=0.5
position x=0.0 y=-0.0 z=0.6
position x=0.0 y=-0.0 z=0.7
position x=0.0 y=-0.0 z=0.8
position x=0.0 y=-0.0 z=0.9
position x=0.0 y=-0.0 z=1.0
position x=0.0 y=-0.0 z=1.1
```

実行例：前進
```bash
i
position x=0.1 y=0.0 z=1.2
position x=0.2 y=0.0 z=1.3
position x=0.3 y=0.0 z=1.3
position x=0.4 y=0.0 z=1.3
position x=0.5 y=0.0 z=1.3
position x=0.6 y=0.0 z=1.3
```

### 箱庭ドローンPro Cライブラリの利用方法

箱庭ドローンシミュレータは、Cライブラリ(hako_service_c)としてバイナリ公開しています。

以下のヘッダファイルをインクルードすることで、ビルド＆リンク可能です。

- include/service/service.h

なお、C APIヘッダは以下です。

- include/service/drone/drone_service_rc_api.h

## 箱庭ありで利用するケース

箱庭ありで利用する場合、箱庭なしの機能に加えて、以下が可能になります。

1. Unity連携: [hakoniwa-unity-drone](https://github.com/hakoniwalab/hakoniwa-unity-drone)を利用
2. デジタルツイン連携: [Zenoh/ROS2箱庭ブリッジ](https://github.com/toppers/hakoniwa-bridge)を利用
3. Mission Planner連携: [MAVLink箱庭ブリッジ](mavlink/bridge/README.md)を利用
4. 箱庭ドローンのAR共有シミュレーション: [箱庭Webサーバー](https://github.com/toppers/hakoniwa-webserver)および[箱庭ARブリッジ](https://github.com/toppers/hakoniwa-ar-bridge)を利用

箱庭あり版の提供バイナリとしては以下のものがあります。

1. PX4 連携のサンプルアプリ(<os名>-main_hako_aircraft_service_px4)
2. Ardupilot 連携のサンプルアプリ(<os名>-main_hako_aircraft_service_ardupilot)
3. 箱庭ドローンのサンプルアプリ(<os名>-main_hako_drone_servce)

全てクロスプラットフォーム対応しています。リリースページにあるバイナリをダウンロードしてください。

os名は、以下の通りです。

- mac
- win
- linux

### 箱庭コア機能のインストール

箱庭あり版を利用する場合は、事前に、[hakoniwa-core-cpp-client](https://github.com/toppers/hakoniwa-core-cpp-client)をインストールしてください。

Windowsの場合は、WSL2で、以下のコマンドを実行してください。

```bash
dd if=/dev/zero of=/mnt/z/mmap/mmap-0x100.bin bs=1M count=5
```

理由：ramdisk上の mmap ファイルのサイズが足りないため。(5MB以上必要)

### Unityエディタの準備

箱庭あり版を利用する場合は、事前に、[hakoniwa-unity-drone](https://github.com/hakoniwalab/hakoniwa-unity-drone)のsimulatinプロジェクトをUnityエディタで開く必要があります。

Unityエディタ起動後、Avatarシーンを開いてください。

![image](/docs/images/unity-editor.png)

このシーンでは、箱庭ドローンの位置と姿勢情報およびローターのPWMデューティ値を受信し、ドローンの動きをビジュアライズします。

箱庭あり版のサンプルアプリと連携することで、Unityエディタ上で箱庭ドローンの動きを確認できます。

また、シミュレーションを開始するには、下図にある START ボタンを押下してください。

![image](/docs/images/unity-sim.png)

### PX4 連携サンプルアプリの利用方法

PX4 連携サンプルアプリを使うと箱庭ドローンシミュレータの物理モデルとPX4を連携することが可能です。

実行方法：
```bash
<os名>-main_hako_aircraft_service_px4 <IPアドレス> 4560 ./config/drone/px4 <path/to/hakoniwa-unity-drone>/simulation/avatar-drone.json
```

* 補足：
  * Windowsの場合、IPアドレスは、Power Shellで、ipconfigを実行したときのWSLのIPアドレスを指定してください。
  * イーサネット アダプター vEthernet (WSL (Hyper-V firewall)):


この際、PX4を起動することで、PX4と連携することが可能です。

参考：https://github.com/toppers/hakoniwa-px4sim?tab=readme-ov-file#terminal-a

あわせて、QGCと連携することで、遠隔操作が可能です。


シミュレーション実行手順：

1. UnityエディタでAvatarシーンを開く。
2. PX4 連携サンプルアプリを起動する。
3. PX4 を起動する。
4. Unityエディタで、STARTボタンを押下する。
5. QGCを起動し、PX4と接続し、遠隔操作を行う。


### Ardupilot 連携サンプルアプリの利用方法

Ardupilot 連携サンプルアプリを使うと箱庭ドローンシミュレータの物理モデルとArdupilotを連携することが可能です。

実行方法：
```bash
<os名>-main_hako_aircraft_service_ardupilot <ホストPCのIPアドレス> 9002 9003 ./config/drone/ardupilot <path/to/hakoniwa-unity-drone>/simulation/avatar-drone.json
```

この際、Ardupilotを起動することで、Ardupilotと連携することが可能です。

```bash
./Tools/autotest/sim_vehicle.py -v ArduCopter -f airsim-copter -A "--sim-port-in 9003 --sim-port-out 9002"  --sim-address=<ホストPCのIPアドレス>  --out=udp:<Mission PlannerのIPアドレス>:14550
```

参考：https://github.com/ArduPilot/ardupilot

この際、Mission Plannerと連携することで、遠隔操作が可能です。

シミュレーション実行手順：

1. UnityエディタでAvatarシーンを開く。
2. Ardupilot 連携サンプルアプリを起動する。
3. Ardupilot を起動する。
4. Unityエディタで、STARTボタンを押下する。
5. Mission Planner を起動し、Ardupilot と接続し、遠隔操作を行う。


### 箱庭ドローンのサンプルアプリの利用方法

箱庭ドローンのサンプルアプリを使うと、箱庭ドローンシミュレータの物理モデルと制御モデルを連携させて、CUIで操作することが可能です。

箱庭ドローンのサンプルアプリは、以下の２種類あります。

1. ラジコン操作のサンプルアプリ
2. フライトプラン操作のサンプルアプリ

#### ラジコン操作のサンプルアプリ

お使いのゲームコントローラで箱庭ドローンを操作することが可能です。

実行方法：
```bash
<os名>-main_hako_drone_servce  ./config/drone/rc <path/to/hakoniwa-unity-drone>/simulation/avatar-drone.json
```

この際、ラジコン操作用のPythonスクリプトを利用することで、箱庭ドローンを操作できます。

```bash
python rc/rc-custom.py <path/to/hakoniwa-unity-drone>/simulation/avatar-drone.json rc/rc_config/ps4-control.json
```

最後の引数(ps4-control.json)は、お使いのゲームコントローラに合わせて変更してください。

シミュレーション実行手順：

1. UnityエディタでAvatarシーンを開く。
2. 箱庭ドローンのサンプルアプリを起動する。
3. Unityエディタで、STARTボタンを押下する。
4. ラジコン操作用のPythonスクリプトを起動する。
5. ゲームコントローラで、箱庭ドローンを操作する。


#### フライトプラン操作のサンプルアプリ

箱庭ドローンの [Python API](/drone_api/libs/README.md) を利用して、フライトプランを実行することが可能です。

フライトプラン操作のサンプルアプリ：[sample.py](/drone_api/rc/sample.py)

実行方法：
```bash
<os名>-main_hako_drone_servce  ./config/drone/api <path/to/hakoniwa-unity-drone>/simulation/avatar-drone.json
```

この際、フライトプラン操作用のPythonスクリプトを利用することで、箱庭ドローンを操作できます。

```bash
python rc/sample.py <path/to/hakoniwa-unity-drone>/simulation/avatar-drone.json
```

シミュレーション実行手順：

1. UnityエディタでAvatarシーンを開く。
2. 箱庭ドローンのサンプルアプリを起動する。
3. Unityエディタで、STARTボタンを押下する。
4. フライトプラン操作用のPythonスクリプトを起動する。

## TIPS

- [Windows で 箱庭あり版PX4/Ardupilot連携する場合について](/docs/tips/wsl/hakoniwa-wsl.md)
- [WSL で、Ardupilot を起動すると Warning, time moved backwards. Restarting timer.が出た時の対処方法](/docs/tips/wsl/warning-timer.md)
- [Ardupilot SITL のセットアップ方法](/docs/tips/wsl/ardupilot-setup.md)
- [WSL/docker 環境のセットアップ方法](/docs/tips/wsl/docker-setup.md)
- [WSL/docker 環境で箱庭&PX4連携方法](/docs/tips/wsl/docker-px4.md)
- [WSL/docker 環境で箱庭&Ardupilot連携方法](/docs/tips/wsl/docker-ardupilot.md)
- [WSL/docker 環境で箱庭&Python API連携方法](/docs/tips/wsl/docker-python-api.md)
- [WSL/docker 環境で箱庭&ゲームパッド操作方法](/docs/tips/wsl/docker-gamepad.md)

