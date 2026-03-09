# Fleet Validator Checklist

## 目的

Phase 1 の fleet validator を、実装しやすい順序で具体化する。

validator は最初の 1 件のエラーを返す前提とし、検証順序を固定する。

## 検証順序

### Step 1: 入力 path の存在確認

- `path` が空でないこと
- `path` が存在すること

ここで失敗した場合:

- `ok = 0`
- `format = HAKO_DRONE_CONFIG_FORMAT_UNKNOWN`

## Step 2: 新方式シグネチャ判定

新方式のシグネチャ:

- top-level に `types`
- top-level に `drones`

判定結果:

- 両方ある: 新方式
- 片方もしくは両方ない: 旧方式へフォールバック候補

この段階では、シグネチャなしはエラーにしない。

## Step 3: fleet 基本構造の検証

新方式シグネチャありの場合、次を確認する。

- `types` が object であること
- `drones` が array であること
- `drones` が空でないこと

失敗した場合:

- `ok = 0`
- `format = HAKO_DRONE_CONFIG_FORMAT_FLEET`

## Step 4: `types` の検証

各 `types[key]` について確認する。

- key が空でないこと
- value が string であること
- fleet file 基準で path 解決できること

失敗した場合:

- `ok = 0`
- `format = HAKO_DRONE_CONFIG_FORMAT_FLEET`

## Step 5: drone 必須項目検証

各 `drones[i]` について確認する。

- `name`
- `type`
- `position_meter`
- `angle_degree`

失敗した場合:

- `ok = 0`
- `format = HAKO_DRONE_CONFIG_FORMAT_FLEET`

## Step 6: whitelist 検証

各 `drones[i]` の許可項目は次のみ。

- `name`
- `type`
- `position_meter`
- `angle_degree`

これ以外の key がある場合はエラー。

## Step 7: 値の整合性検証

各 `drones[i]` について確認する。

- `name` が string で空でないこと
- `type` が string であること
- `position_meter` が number 3 要素 array であること
- `angle_degree` が number 3 要素 array であること

## Step 8: 参照整合性検証

各 `drones[i]` について確認する。

- `type` が `types` に存在すること

## Step 9: 一意性検証

- `name` が重複していないこと

## 戻り値ルール

### 新方式として妥当

- `ok = 1`
- `format = HAKO_DRONE_CONFIG_FORMAT_FLEET`

### 新方式ではない

- `ok = 1`
- `format = HAKO_DRONE_CONFIG_FORMAT_LEGACY`

### 新方式として不正

- `ok = 0`
- `format = HAKO_DRONE_CONFIG_FORMAT_FLEET`

### 入力自体が不正

- `ok = 0`
- `format = HAKO_DRONE_CONFIG_FORMAT_UNKNOWN`

## エラーメッセージの方針

メッセージは、人が直しやすいものにする。

例:

- `fleet config: missing top-level key 'drones'`
- `fleet config: drones[0].type is not defined in types`
- `fleet config: drones[2].position_meter must have 3 elements`
- `fleet config: unsupported key 'controller' in drones[1]`

## Phase 1 の非目標

- すべてのエラーを一度に返すこと
- type file の内部 JSON 妥当性まで検証すること
- 既存 `DroneConfig` の全項目妥当性まで検証すること
