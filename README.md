このリポジトリは、ドローンのプラントモデルおよび制御モデルのシミュレーション環境です。
このシミュレーション環境は、ドローンの動作を物理式ベースで正確にモデル化し、C言語で実装しています。

# アーキテクチャ

![image](docs/images/architecture.png)

# 環境

* サポートOS
  * Arm系Mac
  * Windows 11
  * Windows WSL2
  * Ubuntu 22.0.4

* 利用する環境
  * Python 3.12
  * jq
  * cmake
  * googletest


# 事前準備

```
git clone --recursive https://github.com/toppers/hakoniwa-drone-core.git
```

# ビルド方法

```
cd hakoniwa-drone-core/src
```

```
mkdir cmake-build
```

```
cd cmake-build
```

```
cmake ..
```

```
make
```


# アプリケーションの説明

サンプルアプリケーションとして、以下を用意しています。

- src/main_for_sample
  - service
    - 箱庭なしで、ドローンシミュレーションを実行するサンプルアプリケーションです。
    - main_aircraft_service.cpp
        - 箱庭なしで、PX4と連携するサンプルアプリケーションです。
    - main_drone_service2.cpp
        - 箱庭なしで、制御/物理モデルを実行するサンプルアプリケーションです。
  - hakoniwa
    - 箱庭ありで、ドローンシミュレーションを実行するサンプルアプリケーションです。
    - main_hako_aircraft_service.cpp
        - 箱庭ありで、PX4と連携するサンプルアプリケーションです。
    - main_hako_drone_service.cpp
        - 箱庭ありで、制御/物理モデルを実行するサンプルアプリケーションです。

# シミュレーションの実行方法

```
cd src/cmake-build
```

## 箱庭なしで、ドローンシミュレーションを実行する

### PX4と連携するサンプルアプリケーションを実行する

QGCを起動する。


MAVLINK通信する物理モデルを起動する。

```
 ./main_for_sample/service/aircraft_service 1 ../../config/drone/px4
```

PX4 SITLを起動する。

```
bash ../sim/simstart.bash
```

QGCから操作する。

### 制御/物理モデルを実行するサンプルアプリケーションを実行する

```
export HAKO_CONTROLLER_PARAM_FILE=../../config/controller/param-api-mixer.txt
```

```
 ./main_for_sample/service/drone_service 1 ../../config/drone/ap
```

成功するとこうなります。

```
> Start service
```

コマンドで、ドローンを操作できます。

```
Usage: takeoff <height> | land | move <x> <y> <z> | quit
```

