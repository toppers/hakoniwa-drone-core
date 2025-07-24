# Hakoniwa API ドキュメント

## 概要

### 名前空間: `hako::drone`

`hakoniwa` コンポーネントは、これまで見てきた `service` レイヤーを、箱庭シミュレーションフレームワークに統合し、シミュレーション全体のライフサイクルを管理する最上位のレイヤーです。

ドローンサービスを箱庭の「アセット」として登録し、シミュレーション全体の時間進行を同期させる役割を担います。

---

### クラス設計

#### **`IHakoniwaDroneService`**

-   **役割:** `IDroneService` や `IAircraftServiceContainer` といったサービスコンテナを、箱庭シミュレーションのアセットとして登録するためのインターフェースです。
-   **主な機能:**
    -   `registerService`: サービスコンテナを、指定したアセット名 (`asset_name`) で箱庭に登録します。
    -   `setPduIdMap`: サービスが利用するPDU (`ServicePduDataIdType`) と、箱庭の物理的な通信チャネルIDとをマッピングします。
    -   `startService`: 登録されたアセットのシミュレーションを開始します。

#### **`HakoniwaConductor`**

-   **役割:** 箱庭シミュレーション全体の実行を司る「指揮者」です。静的クラスとして実装され、グローバルなシミュレーションの開始と停止を制御します。
-   **主な機能:**
    -   `startService`: 登録されている全てのアセットのシミュレーションを一斉に開始します。これにより、箱庭シミュレータのコアエンジンが時間の進行を開始します。
    -   `stopService`: シミュレーションを停止します。

---

## クラス図

```mermaid
classDiagram
    class HakoniwaConductor {
        <<static>>
        +startService(delta_time_usec, max_delay_usec)
        +stopService()
    }
    class IHakoniwaDroneService {
        <<interface>>
        +create() : shared_ptr
        +registerService(asset_name, config_path, service_container)
        +startService()
        +setPduIdMap(pdu_id, channel_id)
    }
    class IServiceContainer {
        <<interface>>
    }

    IHakoniwaDroneService ..> IServiceContainer : uses
    HakoniwaConductor ..> IHakoniwaDroneService : controls
```

## シーケンス図

ドローンサービスを準備し、箱庭アセットとして登録、シミュレーションを開始するまでの一連の流れを示します。

```mermaid
sequenceDiagram
    participant User
    participant DroneService as "IDroneService"
    participant HakoniwaService as "IHakoniwaDroneService"
    participant Conductor as "HakoniwaConductor"
    participant HakoniwaCore as "Hakoniwa Core Engine"

    User->>DroneService: create(aircraft, controller)
    Note right of User: 1. まず、独立したドローンサービスを準備

    User->>HakoniwaService: create()
    activate HakoniwaService
    User->>HakoniwaService: registerService("DroneAsset1", config, DroneService)
    Note right of HakoniwaService: 2. ドローンサービスを箱庭アセットとして登録
    User->>HakoniwaService: setPduIdMap(TAKEOFF_CMD, 0)
    User->>HakoniwaService: startService()

    User->>Conductor: startService(delta, delay)
    activate Conductor
    Note right of Conductor: 3. シミュレーション全体の開始を指示
    Conductor->>HakoniwaCore: Asset Run
    activate HakoniwaCore
    Note right of HakoniwaCore: 時間進行が開始され、各アセットの\n`advanceTimeStep()`が周期的に呼ばれる
    HakoniwaCore-->>Conductor:
    deactivate HakoniwaCore
    deactivate Conductor
    deactivate HakoniwaService
```