# Fleet Path Resolver

## 目的

新方式 config と既存 `DroneConfig` の path 解決ルールを共通化する。

扱いたい要件は次の 2 つ。

- 新方式では file-relative を正規仕様にする
- 既存 config 互換のために cwd fallback を残す

## 適用対象

- fleet の `types` 参照
- `controller.moduleDirectory`
- `controller.paramFilePath`
- `components.battery.BatteryModelCsvFilePath`
- `simulation.logOutputDirectory`
- `components.sensors.*.vendor`

## 基本ルール

実装は OS 非依存を前提とし、`std::filesystem::path` ベースで行う。

- 区切り文字の連結を文字列処理で行わない
- `is_absolute()` を使って絶対パス判定する
- `parent_path()` で基準ディレクトリを求める
- path 結合は `base / relative` で行う
- 必要に応じて `lexically_normal()` で正規化する

### 1. 絶対パス

絶対パスなら、そのまま使う。

### 2. 相対パス

相対パスなら、次の順で解決する。

1. 基準ファイルの親ディレクトリ基準
2. プロセスのカレントディレクトリ基準

### 3. fallback

file-relative で見つからず、cwd 基準で見つかった場合は後方互換として許容する。
ただし、将来的には warning を出せる設計にしておく。

## 基準ファイル

### fleet の `types`

- 基準は fleet file

例:

- fleet: `config/drone/fleets/rc-1.json`
- type ref: `types/rc.json`

この場合、解決先は `config/drone/fleets/types/rc.json`

### type 内の path 項目

- 基準は type file

例:

- type: `config/drone/fleets/types/rc.json`
- `controller.moduleDirectory`: `../modules/RadioController`

この場合、まず `config/drone/fleets/types/../modules/RadioController` を試す。

## API 方針

Phase 1 では、小さい API にする。

### C++ 内部 API イメージ

```cpp
enum class PathResolveMode {
    Absolute,
    FileRelative,
    CwdFallback,
    Unresolved
};

struct PathResolveResult {
    bool ok;
    PathResolveMode mode;
    std::string path;
};

PathResolveResult resolve_path(
    const std::string& base_filepath,
    const std::string& raw_path,
    bool must_exist);
```

### 入力

- `base_filepath`
  - fleet file または type file のパス
- `raw_path`
  - config に書かれている path 文字列
- `must_exist`
  - 存在確認が必要かどうか

## `must_exist` の考え方

### `true`

対象:

- fleet の `types` 参照
- `controller.paramFilePath`
- `components.battery.BatteryModelCsvFilePath`

### `false`

対象:

- `controller.moduleDirectory`
- `simulation.logOutputDirectory`
- `components.sensors.*.vendor`

これらは実際のファイル名連結やディレクトリ生成を伴うため、解決時点では存在しなくてもよい場合がある。

## 出力

### `ok = true`

- 解決済み path を返す
- どの方式で解決したかも返す

### `ok = false`

- path 解決に失敗した
- 呼び出し側が validator error または runtime error に変換する

## Phase 1 の実装方針

- まずは C++ 内部 utility として実装する
- validator と resolver の両方から同じ関数を使う
- C API 化は validator 側から先に進める

## 非目標

- path 正規化ポリシーの完全統一
- symlink や canonical path の厳密処理
- warning 出力ポリシーの詳細設計
