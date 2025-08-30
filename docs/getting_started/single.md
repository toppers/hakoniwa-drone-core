[English](single.en.md) | 日本語

# Getting Started: シングルパターン（箱庭なし）

箱庭ドローンシミュレータを **箱庭なし構成（シングルパターン）** で利用する場合、物理モデルおよび制御モデルを**スタンドアロンで直接実行**できます。

この構成では、UnityやUnreal Engine、Pythonスクリプトなどから**直接Cライブラリを呼び出して連携**することが可能です。

---

## ✅ 構成概要

* **箱庭なし（hakoniwa-core不要）**
* クロスプラットフォーム対応（macOS / Windows / Linux）
* GUIや他アセットとの連携なし

用途例：

* PX4/Ardupilotとの単体連携テスト
* CUIによるドローン制御の動作確認
* PythonやUnrealからの直接組み込み

---

## 📦 提供バイナリ一覧

Releasesページから最新バージョンを取得してください：
👉 [🔗 最新バイナリ（Releases）](https://github.com/toppers/hakoniwa-drone-core/releases)

| バイナリ名                              | 概要               |
| ---------------------------------- | ---------------- |
| `<os名>-aircraft_service_px4`       | PX4との通信・連携       |
| `<os名>-aircraft_service_ardupilot` | Ardupilotとの通信・連携 |
| `<os名>-drone_service_rc`           | CUIで操作可能なラジコン風制御 |
| `hako_service_c`                   | Cライブラリ形式で直接利用可能  |

> `os名`は `mac`, `win`, `linux` のいずれかです。

ZIPを展開したディレクトリ内に各バイナリが含まれています。

---

## 1. PX4連携：aircraft_service_px4

```bash
<os名>-aircraft_service_px4 <IPアドレス> 4560 ./config/drone/px4
```

* PX4を別途起動し、QGCと連携させることで遠隔操作も可能です。
* 参考
  * [PX4のビルド方法](/docs/tips/wsl/px4-setup.md)
  * [PX4の起動方法](/docs/tips/wsl/docker-px4.md)

---

## 2. Ardupilot連携：aircraft_service_ardupilot

```bash
<os名>-aircraft_service_ardupilot <ホストPCのIPアドレス> 9002 9003 ./config/drone/ardupilot
```

* Ardupilotとの双方向UDP通信で制御連携を行います。
* Mission Plannerと連携して操作可能です。

Ardupilot起動例：

```bash
./Tools/autotest/sim_vehicle.py -v ArduCopter -f airsim-copter \
  -A "--sim-port-in 9003 --sim-port-out 9002" \
  --sim-address=<ホストPCのIP> \
  --out=udp:<MissionPlannerのIP>:14550
```

* 参考
  * [Ardupilotのビルド方法](/docs/tips/wsl/ardupilot-setup.md)
  * [Ardupilotの起動方法](/docs/tips/wsl/docker-ardupilot.md)


---

## 3. CUI操作：drone_service_rc

箱庭ドローンシミュレータの物理モデルと制御モデルを連携させて、CUIで操作することが可能です。

```bash
drone_service_rc 1 config/drone/rc
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

> 注意：`x` を入力して、アームしないと、ドローンは動作しません。後述する操作は、アーム後に行ってください。

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


---

## 4. Cライブラリ連携：hako_service_c

ライブラリとして組み込みたい場合：

* `include/service/service.h`
* `include/service/drone/drone_service_rc_api.h`

をインクルードして利用できます。

組み込み先の例：

* Unreal Engine（C++）
* Unity（C#＋P/Invoke）
* Python（ctypes / pybind11）


## drone_service_rcのソースとビルド方法

drone_service_rc は、C++で実装されており、以下の手順でビルドできます。

### Ubuntu / macOS でのビルド手順

```bash
cd src
mkdir cmake-build
cd cmake-build
cmake ..
make
```

### Windows でのビルド手順

```powershell
cd src
cmake -G "Visual Studio 17 2022" -A x64 -DHAKO_DRONE_OPTION_FILEPATH="cmake-options\win-cmake-options.cmake" .
cmake --build . --config Release
```


---

## 🚀 参考情報

* PX4連携リポジトリ: [PX4/PX4-Autopilot](https://github.com/PX4/PX4-Autopilot)
* Ardupilot連携: [ArduPilot/ardupilot](https://github.com/ArduPilot/ardupilot)
