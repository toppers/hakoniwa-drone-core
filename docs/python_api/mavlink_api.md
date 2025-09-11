# Python API (Ardupilot / PX4 対応)

## 概要
箱庭ドローンシミュレータを Python から制御する API です。  
MAVLink 経由で Ardupilot / PX4 の両方に対応し、同一の API 呼び出しで制御できます。


## できること
- API 経由での基本制御  
  - ARM / DISARM  
  - 離陸 / 着陸  
  - 指定位置までの移動
- センサ情報の取得  
  - LiDAR データ  
  - カメラ画像  
  - ドローン姿勢（Pose）  
- 複数機体の同時制御  
  - `add_vehicle()` で Ardupilot / PX4 を混在可能  
- 荷物操作（grab / release）

## 仕組み
- MAVLink通信ライブラリは、`pymavlink` を利用
- ゲームエンジン(Unity/Unreal)連携して実現できるセンサデータ(LiDAR/Camera)の取得は、箱庭PDUを介して実装
- フライトスタック固有の差異は `ArduPilotController` / `PX4Controller` が吸収  
- 上位 API は `MavlinkMultirotorClient` が統合的に提供  

## クラス設計概要
### AbstractFlightController
- フライトコントローラ共通の抽象クラス  
- `set_api_mode`, `arm`, `takeoff`, `land`, `go_to_local_ned` を規定

### ArduPilotController / PX4Controller
- AbstractFlightController の具象実装  
- Ardupilot: GUIDED/STABILIZE モード設定や GPS FIX 待ちなどを実装  
- PX4: OFFBOARD モード、スレッドでの setpoint streaming を実装

### MavlinkDrone
- 単一ドローンを表すクラス  
- 接続確立、姿勢取得、切断などを担当

### MavlinkMultirotorClient
- 複数機体を統合管理するクライアント  
- 利用者はこのクラスを介して API を呼び出す  
- 主なメソッド:  
  - `add_vehicle(name, conn, type)`  
  - `enableApiControl`, `armDisarm`, `takeoff`, `land`, `moveToPosition`  
  - `simGetVehiclePose`, `simGetImage`, `getLidarData`, `grab_baggage`

## クラス図

```mermaid
classDiagram
    class MavlinkMultirotorClient {
        - Dict~str, MavlinkDrone~ vehicles
        - FrameConverter converter
        + add_vehicle(name, conn, type)
        + confirmConnection()
        + enableApiControl(enable, vehicle_name)
        + armDisarm(arm, vehicle_name)
        + takeoff(height, vehicle_name, timeout)
        + land(vehicle_name)
        + moveToPosition(x,y,z,speed,yaw,timeout,vehicle_name)
        + simGetVehiclePose(vehicle_name)
        + simGetImage(camera_id, type, vehicle_name)
        + getLidarData(vehicle_name)
        + grab_baggage(grab, timeout, vehicle_name)
    }

    class MavlinkDrone {
        - string name
        - string connection_string
        - AbstractFlightController controller
        + connect()
        + disconnect()
        + get_vehicle_pose()
    }

    class AbstractFlightController {
        <<interface>>
        + init_connection(mavlink_conn)
        + set_api_mode()
        + arm()
        + disarm()
        + takeoff(z)
        + land()
        + go_to_local_ned(x,y,z,yaw)
        + stop_movement()
    }

    class ArduPilotController {
        + init_connection()
        + set_api_mode()
        + arm()
        + disarm()
        + takeoff()
        + land()
        + go_to_local_ned()
        + stop_movement()
    }

    class PX4Controller {
        + init_connection()
        + set_api_mode()
        + arm()
        + disarm()
        + takeoff()
        + land()
        + go_to_local_ned()
        + stop_movement()
    }

    MavlinkMultirotorClient "1" --> "*" MavlinkDrone
    MavlinkDrone "1" --> "1" AbstractFlightController
    AbstractFlightController <|-- ArduPilotController
    AbstractFlightController <|-- PX4Controller
```

## 使用例
実際の実行手順については以下を参照してください。
- [Ardupilotでの複数機体シミュレーション](/docs/multi_drones/ardupilot.md)
- [PX4での複数機体シミュレーション](/docs/multi_drones/px4.md)

