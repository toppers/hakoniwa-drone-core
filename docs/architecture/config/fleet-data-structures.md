# Fleet Data Structures

## 目的

新方式 config の入力表現を、最小限の構造で扱えるようにする。

ここで定義する構造は、

- validator
- resolver

の間で共有するためのものとする。

最終内部表現は既存 `DroneConfig` を使うため、ここで構造を増やしすぎない。

## 方針

- JSON に近い薄い構造にする
- business logic は持たせない
- 既存 `DroneConfig` の代替にはしない
- type 定義の本体は既存 `DroneConfig` を再利用する

## `DroneInstanceConfig`

fleet 側の 1 機体分を表す。

### 役割

- `drones[i]` 1 要素の保持
- validator 済みの instance 情報を resolver に渡す

### 想定フィールド

```cpp
struct DroneInstanceConfig {
    std::string name;
    std::string type;
    std::array<double, 3> position_meter;
    std::array<double, 3> angle_degree;
};
```

### 備考

- `index` は持たない
- 内部 index は `drones` 配列順で決まる

## `DroneFleetConfig`

fleet JSON 全体を表す。

### 役割

- `types`
- `drones`

をまとめて保持する。

### 想定フィールド

```cpp
struct DroneFleetConfig {
    std::string fleet_filepath;
    std::map<std::string, std::string> types;
    std::vector<DroneInstanceConfig> drones;
};
```

### 備考

- `fleet_filepath` は path resolver の基準として使う
- `types` の value は raw path 文字列で保持してよい
- type path の解決は resolver 側で行う

## `DroneFleetConfigValidator`

### 役割

- raw JSON を検証する
- 必要なら `DroneFleetConfig` を組み立てる前段を担う

### 方針

Phase 1 では次のどちらでもよい。

1. validator が `DroneFleetConfig` を直接返す
2. validator は検証だけ行い、parser が別で `DroneFleetConfig` を生成する

ただし実装を単純にするなら、Phase 1 は

- parse
- validate
- `DroneFleetConfig` 生成

を同じ実装単位で持ってもよい。

## `DroneFleetConfigResolver`

### 役割

- `DroneFleetConfig` を受け取る
- type path を解決する
- type file を既存 `DroneConfig` としてロードする
- instance 情報を適用する
- `std::vector<DroneConfig>` を返す

### 入力

```cpp
std::vector<DroneConfig> resolve(const DroneFleetConfig& fleet);
```

## 持たせないもの

Phase 1 では次を持たせない。

- type 定義専用の別クラス
- instance 側 override 用の map
- warning list
- index フィールド

## 理由

- type 定義は既存 `DroneConfig` で十分
- instance override を広げると設計が崩れる
- index は配列順で足りる
- warning は Phase 1 の必須要件ではない

## 推奨配置

例:

- `include/config/fleet_config.hpp`
- `src/config/impl/fleet_config.cpp`
- `src/config/impl/fleet_validator.cpp`
- `src/config/impl/fleet_resolver.cpp`

ただし、既存レイアウトとの整合性を優先して配置は最終調整してよい。
