
[English](README.md) ｜ 日本語

# これは何？

箱庭のプラントモデルを Python プログラムで制御するためのAPIを提供しています。

箱庭API(`hakosim`)は、基本的に、[AirSim](https://microsoft.github.io/AirSim/)のAPIのシグネチャを踏襲しています。

箱庭の Python API 概要は、[こちら](/drone_api/libs/README.md)を参照ください。

# サンプルプログラム

Python API の利用方法を理解するための[API コール用サンプルプログラム](/drone_api/rc/api_control_sample.py)を用意しています。

サンプルプログラムでは、以下の機能を実行しています。

* ドローンのテイクオフ
* ドローンの移動
* ドローンの位置情報のデバッグ表示
* 荷物の搬送
* ドローン前方のカメラ画像の取得とファイル保存
* 3DLiDARデータの取得とデバッグ表示
* ドローンの着陸

また、[ラジコン操作用のサンプルプログラム](drone_api/rc/rc-custom.py)で、ゲームコントローラ(PS4/5)や、プロポ等でドローン操縦するためのサンプルプログラムも用意しています。


# インストール方法

以下のコマンドを実行してください。

```
pip install hakoniwa-pdu
```

補足：バージョンアップ方法

```
pip install --upgrade hakoniwa-pdu
```

# Pythonプログラムの実行方法

drone_api/rc ディレクトリに移動して、以下のコマンドを実行してください。

```bash
cd drone_api/rc
```

シミュレーション実行完了後であれば、任意のタイミングで、Pythonプログラムを実行して、箱庭APIを呼び出すことができます。

API コール用サンプルプログラムを実行する場合は、以下のコマンドを実行してください。
```bash
python3 -m api_control_sample ../../config/pdudef/webavatar.json
```

ラジコン操作用のサンプルプログラムを実行する場合は、以下のコマンドを実行してください。
```bash
python3 -m rc-custom ../../config/pdudef/webavatar.json rc_config/ps4-control.json
```

第三引数は、PS4コントローラの設定ファイルです。他のゲームコントローラやプロポを利用する場合は、適宜設定ファイルを変更してください。

# 箱庭ドローンのコンフィグファイル

Unity上で実現された箱庭ドローンにはさまざまなセンサ/アクチュエータがあります。これらの機能はパラメータを持っており、[hakoniwa-unity-drone](https://github.com/hakoniwalab/hakoniwa-unity-drone)/simulation 直下にパラメータ定義ファイル(drone_config.json)を配置することで、パラメータ反映させることができます。


設定例：
```json
{
    "drones": {
        "DroneTransporter": {
            "audio_rotor_path": "file:///Users/tmori/Downloads/spo_ge_doron_tobi_r01.mp3",
            "LiDARs": {
                "LiDAR": {
                    "Enabled": false,
                    "NumberOfChannels": 16,
                    "RotationsPerSecond": 10,
                    "PointsPerSecond": 10000,
                    "MaxDistance": 10,
                    "X": 0.45, "Y": 0, "Z": -0.3,
                    "Roll": 0, "Pitch": 0, "Yaw" : 0,
                    "VerticalFOVUpper": 5,
                    "VerticalFOVLower": -5,
                    "HorizontalFOVStart": -5,
                    "HorizontalFOVEnd": 5,
                    "DrawDebugPoints": true
                }
            }
        }
    }
}
```

* audio_rotor_path: ドローンのローター音源のファイルパス。ファイルが存在する場合、ローター音を流すことができます。
* LiDARs: ドローンに搭載されたLiDARの設定
* Enabled: LiDARの有効化または無効化。trueは有効、falseは無効。
* NumberOfChannels: LiDARのチャンネル数
* RotationsPerSecond: LiDARの回転速度(回転数/秒)
* PointsPerSecond: LiDARの秒間の総ポイント数
* MaxDistance: LiDARで計測可能な最大距離（単位：メートル）
* X, Y, Z: LiDARの配置位置（ドローンの位置座標からの相対）（単位：メートル）
* Roll, Pitch, Yaw: LiDARの配置姿勢（ロール、ピッチ、ヨーの角度）
* VerticalFOVUpper: LiDARの上方向のFOV（視野角）
* VerticalFOVLower: LiDARの下方向のFOV（視野角）
* HorizontalFOVStart: LiDARの水平方向のFOVの開始角度
* HorizontalFOVEnd: LiDARの水平方向のFOVの終了角度
* DrawDebugPoints: LiDARのデバッグポイント描画の有無（Unityエディタを利用している場合のみ）

なお、箱庭のLiDARの基本スペックは以下を上限としています。

```
周波数：5Hz
水平：-90° 〜 90°
垂直：-30° 〜 30°
分解能：1°
```

上記で計算されるPDUデータサイズを上限サイズとしていますのでパラメータ定義は以下の制約があります。

* NumberOfChannels: 61
* HorizontalPointsPerRotation = 181
  * PointsPerRotation = PointsPerSecond / RotationsPerSecond
  * HorizontalPointsPerRotation = PointsPerRotation / NumberOfChannels

水平方向と垂直方向の分解能は以下の計算式で求めています。

* 水平方向：HorizontalRanges / HorizontalPointsPerRotation
  * HorizontalRanges = HorizontalFOVEnd - HorizontalFOVStart
* 垂直方向：VerticalRanges / param.NumberOfChannels
  * VerticalRanges = VerticalFOVUpper - VerticalFOVLower
