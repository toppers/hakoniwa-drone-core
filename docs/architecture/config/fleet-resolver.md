# Fleet Resolver

## 目的

新方式 config を、既存の実行系がそのまま使える

- `std::vector<DroneConfig>`

へ解決する。

## 前提

- type 定義本体は既存 `DroneConfig` を再利用する
- fleet 側は `name`, `type`, `position_meter`, `angle_degree` だけを持つ
- 内部 index は `drones` 配列順を使う

## 入力

```cpp
std::vector<DroneConfig> resolve(const DroneFleetConfig& fleet);
```

## 出力

- 1 機体ごとの `DroneConfig`
- 順序は `fleet.drones` と同じ

## 処理フロー

1. `fleet.types` から type ID に対応する raw path を取得する
2. path resolver で fleet file 基準の type file path に解決する
3. type file を既存 `DroneConfig` としてロードする
4. type file 基準で既存 path 項目を解決する
5. instance の `name`, `position_meter`, `angle_degree` を適用する
6. 解決済み `DroneConfig` を vector に積む

## 重要な設計判断

### 1. `DroneConfig` は再利用する

resolver は、新方式専用の最終表現を作らない。
既存の `DroneConfig` を最終表現として使う。

### 2. `DroneConfig` には最小 extension が必要

現状の `DroneConfig` は getter 中心で、

- `name`
- `components.droneDynamics.position_meter`
- `components.droneDynamics.angle_degree`

を外から上書きする API を持っていない。

そのため、resolver を実装するには次のどちらかが必要。

1. `DroneConfig` に最小 setter を追加する
2. `DroneConfig` に `json` ベースの初期化 API を追加する

Phase 1 では、変更範囲を小さくするため、最小 setter の方が素直である。

想定 setter:

```cpp
void setRoboName(const std::string& name);
void setCompDroneDynamicsPosition(const std::array<double, 3>& position);
void setCompDroneDynamicsAngle(const std::array<double, 3>& angle);
```

### 3. path 解決は resolver 側で行う

type file をロードした後、既存 path 項目も file-relative first / cwd fallback で解決する。

対象:

- `controller.moduleDirectory`
- `controller.paramFilePath`
- `components.battery.BatteryModelCsvFilePath`
- `simulation.logOutputDirectory`
- `components.sensors.*.vendor`

## エラー方針

- type path が解決できない: runtime error
- type file がロードできない: runtime error
- instance 適用に失敗する: runtime error

validator 済み入力を前提とするので、resolver は構築失敗だけを扱えばよい。

## `DroneConfigManager` との関係

resolver の責務は `std::vector<DroneConfig>` を返すところまで。

その後は、

- `DroneConfigManager` が保持する
- 既存の factory / service が使う

という現在の流れに合流させる。

## 非目標

- type 定義専用クラスの導入
- fleet 側 override の一般化
- `DroneConfig` の全面再設計
