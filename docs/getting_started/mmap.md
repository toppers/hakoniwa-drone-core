[English](mmap.en.md) | 日本語

# 箱庭ありで利用するケース

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

ラジコン操作方法は、[こちら](/drone_api/README-ja.md)を参照ください。



シミュレーション実行手順：

1. UnityエディタでAvatarシーンを開く。
2. 箱庭ドローンのサンプルアプリを起動する。
3. Unityエディタで、STARTボタンを押下する。
4. ラジコン操作用のPythonスクリプトを起動する。
5. ゲームコントローラで、箱庭ドローンを操作する。


#### フライトプラン操作のサンプルアプリ

箱庭ドローンの [Python API](/drone_api/libs/README.md) を利用して、フライトプランを実行することが可能です。


実行方法：
```bash
<os名>-main_hako_drone_servce  ./config/drone/api <path/to/hakoniwa-unity-drone>/simulation/avatar-drone.json
```

この際、フライトプラン操作用のPythonスクリプトを利用することで、箱庭ドローンを操作できます。

Pythonスクリプトの実行方法は、[こちら](/drone_api/README-ja.md)を参照ください。

シミュレーション実行手順：

1. UnityエディタでAvatarシーンを開く。
2. 箱庭ドローンのサンプルアプリを起動する。
3. Unityエディタで、STARTボタンを押下する。
4. フライトプラン操作用のPythonスクリプトを起動する。

