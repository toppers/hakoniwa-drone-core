# Fleet Validator Public Boundary

## 目的

新方式 config の validator の公開境界を整理する。

Phase 1 では、起動前チェックに必要な最小インターフェースのみを扱う。

## 設計方針

- C API は採用しない
- C++ 実装を `src/config` に配置し、公開ヘッダは最小限にする
- Phase 1 では最初の 1 件のエラーだけ返す
- 詳細な error list や warning list は後続段階で追加する

## 扱う判定

- 新方式シグネチャがあるか
- 新方式 config として妥当か
- 旧方式へフォールバックすべきか

## Phase 1 の公開形

現行は C++ の loader/validator 境界のみを公開する。

対象:

- `FleetConfigLoadKind`
- `FleetConfigLoadResult`
- `loadFleetConfigFile(...)`
- `releaseFleetConfigLoadResult(...)`

## エラー方針

- 新方式シグネチャあり + 検証失敗
  - `ok == 0`
  - `format == HAKO_DRONE_CONFIG_FORMAT_FLEET`
  - 旧方式へフォールバックしない

- 新方式シグネチャなし
  - `kind == Legacy`

## Phase 1 の非目標

- 複数エラーの列挙
- warning の返却
- JSON text 直接入力 API
- validator の stateful handle API
- C API の提供
