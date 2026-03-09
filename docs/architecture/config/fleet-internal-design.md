# Fleet Internal Design

## 目的

新方式 config を導入しても、既存の実行系内部構造はできるだけ変更しない。

特に、

- `aircraft_factory`
- `aircraft_controller_factory`
- `service`
- 既存の `DroneConfig` accessor 群

は、そのまま使い続けることを基本方針とする。

## 基本方針

- 新方式の変更は config 入口に閉じる
- 最終内部表現は既存 `DroneConfig` を使い回す
- 新規クラスは fleet 入力と解決処理に限定する

つまり、新方式 config は最終的に

- `std::vector<DroneConfig>`

へ解決されればよい。

その後の処理は既存実装をそのまま利用する。

## 変更しないもの

Phase 1 では、次の内部構造は変更対象にしない。

- `DroneConfig` の既存 accessor 群
- `aircraft_factory`
- `aircraft_controller_factory`
- `DroneService`
- `IAirCraft`
- `IAircraftController`

## 追加するもの

Phase 1 で追加する責務は次の 3 つに絞る。

### 1. Fleet 入力表現

fleet JSON を表す軽量構造を持つ。

想定責務:

- `types`
- `drones`

### 2. Instance 入力表現

fleet 側の 1 機体分を表す軽量構造を持つ。

想定項目:

- `name`
- `type`
- `position_meter`
- `angle_degree`

### 3. Resolver

新方式 config を既存 `DroneConfig` 群へ解決する。

想定責務:

1. fleet を読む
2. type ファイルを読む
3. 共通の path resolver で type path を fleet file 基準で解決する
4. type 側の JSON を既存 `DroneConfig` としてロードする
5. `DroneConfig` 内の既存 path 項目も、共通 path resolver で file-relative first / cwd fallback で解決する
6. instance 側の `name`, `position_meter`, `angle_degree` を適用する
7. `drones` 配列の順番を内部 index として採用する
8. `std::vector<DroneConfig>` を返す

## `DroneConfig` 再利用の考え方

type 定義ファイルは、新方式専用の全く別形式にはしない。

できるだけ既存 `DroneConfig` の JSON 形を維持しつつ、

- `name`
- 位置
- 姿勢

のような instance 情報だけを fleet 側へ移す。

これにより、

- 既存の `DroneConfig` parser
- 既存の getter
- 既存 factory 群

をそのまま再利用しやすくする。

## 推奨クラス構造

### `DroneConfig`

- 既存のまま使う
- 最終的な 1 機体分の内部表現

### `DroneInstanceConfig`

- fleet 側の 1 機体分
- 薄い入力表現

### `DroneFleetConfig`

- fleet JSON 全体
- `types` と `drones` を保持

### `DroneFleetConfigResolver`

- fleet + type 定義から `std::vector<DroneConfig>` を生成する
- type path と既存 path 項目の解決に、共通 path resolver を使う

### `DroneFleetConfigValidator`

- 新方式 config の整合性を検証する
- loader とは責務を分離する

## 避けるべき設計

以下は Phase 1 では避ける。

- 新方式を全部 `DroneConfig` に直接詰め込む
- `DroneConfig` に fleet / type の両責務を持たせる
- factory 側で type 解決や fleet 解決を始める
- 実行系の内部表現を新方式専用に置き換える

## 処理フロー

1. config path を受け取る
2. validator が新方式シグネチャを判定する
3. 新方式なら validator で整合性を確認する
4. resolver が fleet と type 定義を解決する
5. `std::vector<DroneConfig>` を生成する
6. 以後は既存の `DroneConfigManager` 相当の流れに乗せる

## 設計上の利点

- 既存実装の変更範囲が小さい
- 新方式の責務が入口に閉じる
- 後方互換を持ちやすい
- 問題が起きても config 層で切り分けやすい
- 将来 validator CLI を追加しやすい
