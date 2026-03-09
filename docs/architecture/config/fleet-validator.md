# Fleet Validator Plan

## 目的

新方式 config の整合性を、起動前に検証できるようにする。

validator は loader とは責務を分ける。

- validator: 新方式かどうかの判定と整合性検証
- loader: 検証済み config を最終 `DroneConfig` 群へ解決する

## Phase 1 のスコープ

まずは起動処理から呼ばれる最小 validator を作る。

対象:

- 新方式 config の判定
- 基本的な整合性検証
- 不正 config の早期エラー化

対象外:

- CLI validator ツール
- 旧方式 config の詳細検証
- 最終 `DroneConfig` 生成

## 公開境界の方針

validator は C++ 実装として `src/config` に配置する。

Phase 1 では C API は持たない。

利点:

- 起動処理からそのまま使える
- 実装を `cpp` 側に隠蔽できる
- 仕様が固まってから外部 API を検討できる

## Phase 1 の検証項目

### 1. 新方式シグネチャ判定

トップレベルに `types` と `drones` があることを、新方式のシグネチャとする。

### 2. 必須項目検証

fleet 側で次が存在することを確認する。

- `types`
- `drones`

各 drone で次が存在することを確認する。

- `name`
- `type`
- `position_meter`
- `angle_degree`

### 3. type 参照検証

- `types` に定義された path が、fleet file 基準で解決できること
- `drones[*].type` が `types` に存在すること

### 4. 基本整合性検証

- `name` が空でないこと
- `name` が重複していないこと
- `position_meter` が 3 要素であること
- `angle_degree` が 3 要素であること

### 5. whitelist 検証

Phase 1 の fleet 側で許可する項目は次のみとする。

- `name`
- `type`
- `position_meter`
- `angle_degree`

それ以外の項目が含まれていた場合はエラーにする。

## エラー方針

- 新方式シグネチャがある場合は、新方式として扱う
- 新方式としての検証に失敗した場合はエラーにする
- 旧方式へのフォールバックは行わない

## Phase 1 の公開形

- `FleetConfigLoadKind`
- `FleetConfigLoadResult`
- `loadFleetConfigFile(const std::string&)`
- `releaseFleetConfigLoadResult(...)`

Phase 1 では、詳細なエラー一覧よりも、起動を止めるための最初の 1 件を返せれば十分とする。

## 起動時の使い方

1. config path を受け取る
2. validator を呼ぶ
3. `ok == 0` ならエラー終了する
4. `kind == Fleet` なら新方式 loader へ進む
5. `kind == Legacy` なら旧方式 loader へ進む
