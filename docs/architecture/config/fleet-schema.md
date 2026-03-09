# Fleet Config Schema

## 目的

100 台同時 Sim 向けに、ドローン設定を次の 2 層で表現する。

- type 定義
- fleet 定義

新方式では、共通設定を type 側に寄せ、個体差分は fleet 側に限定する。

## 設計方針

- 共通設定は type 側に置く
- 個体差分は fleet 側に置く
- Phase 1 の fleet 側項目は最小 whitelist に限定する
- 迷う項目は type 側に寄せる

## Type 定義

### 役割

機体タイプごとの共通設定を定義する。

### 配置例

- `config/drone/fleets/types/rc.json`
- `config/drone/fleets/types/api.json`

### 必須項目

- `name`
- `simulation`
- `components`
- `controller`

### Type 側に置く項目

- `simulation.*`
- `components.droneDynamics.*` のうち位置・姿勢以外
- `components.battery.*`
- `components.rotor.*`
- `components.thruster.*`
- `components.sensors.*`
- `controller.*`

Phase 1 では、controller 設定はすべて type 側に置く。
個体別の controller override は許可しない。

### 例

```json
{
  "name": "rc-default",
  "simulation": {
    "lockstep": true,
    "timeStep": 0.001,
    "logging": {
      "mode": "csv"
    },
    "location": {
      "latitude": 47.641468,
      "longitude": -122.140165,
      "altitude": 121.321
    }
  },
  "components": {
    "droneDynamics": {
      "physicsEquation": "BodyFrame",
      "useQuaternion": true,
      "collision_detection": true,
      "enable_disturbance": true,
      "manual_control": false,
      "airFrictionCoefficient": [0.5, 0.0],
      "inertia": [0.01169962, 0.01184215, 0.02104691],
      "mass_kg": 0.68240503,
      "body_size": [0.1, 0.1, 0.01],
      "body_boundary_disturbance_power": 1.0
    },
    "battery": {},
    "rotor": {},
    "thruster": {},
    "sensors": {}
  },
  "controller": {
    "moduleName": "RadioController",
    "paramFilePath": "config/controller/param-api-mixer.txt"
  }
}
```

## Fleet 定義

### 役割

複数機体インスタンスを列挙する。

### 配置例

- `config/drone/fleets/rc-10.json`
- `config/drone/fleets/rc-100.json`
- `config/drone/fleets/rc-1.json`

### 必須項目

- `types`
- `drones`

### `types`

type ID から type 定義ファイルへの参照を持つ。

### `drones`

各機体インスタンスの配列。

### Fleet 側に置く項目

Phase 1 では次のみを許可する。

- `name`
- `type`
- `position_meter`
- `angle_degree`

### 例

```json
{
  "types": {
    "rc": "config/drone/fleets/types/rc.json"
  },
  "drones": [
    {
      "name": "drone0",
      "type": "rc",
      "position_meter": [0, 0, 0],
      "angle_degree": [0, 0, 0]
    },
    {
      "name": "drone1",
      "type": "rc",
      "position_meter": [5, 0, 0],
      "angle_degree": [0, 0, 0]
    }
  ]
}
```

## 最終解決ルール

1. fleet の `types` から type 定義を引く
2. 各 drone は `type` を使って type 定義を参照する
3. type 定義をベースに、fleet 側の instance 情報を適用する
4. `drones` 配列の順番を内部 index として採用する
5. 最終的に 1 機体 1 個の内部 `DroneConfig` 相当へ解決する

## Phase 1 の制約

- fleet 側 override は whitelist 方式にする
- `simulation` の個体別 override は許可しない
- `components` の個体別 override は許可しない
- `controller` の個体別 override は許可しない

特に `controller.moduleName`, `controller.paramFilePath`, `controller.mixer` などは、
すべて type 側固定とする。

## 判定方針

- 新方式のシグネチャがある場合は、新方式として扱う
- 新方式としてのロードに失敗した場合はエラーにする
- 新方式のシグネチャが無い場合のみ、旧方式へフォールバックする

Phase 1 では、新方式のシグネチャとしてトップレベルの `types` と `drones` を用いる。

## 実例

このリポジトリ内の具体例:

- `config/drone/fleets/types/rc.json`
- `config/drone/fleets/rc-1.json`

## logging の扱い

- type 定義では `simulation.logging.mode` を明示することを推奨する
- 既定値は `csv` だが、新方式では未指定に頼らず明示する

## パス指定の方針

Phase 1 では、type 定義内の既存 path 項目も含めて、path 解決ルールを共通化する。

- `controller.moduleDirectory`
- `controller.paramFilePath`
- `components.battery.BatteryModelCsvFilePath`
- `simulation.logOutputDirectory`

これらの相対パスは、次の順で解決する。

1. type 定義ファイル基準
2. 後方互換のためのカレントディレクトリ基準 fallback

つまり、新方式では file-relative を正規仕様としつつ、既存 config 互換のために cwd fallback を許容する。

fleet の `types` で参照する type 定義ファイル path は、fleet file 基準で解決する。
