# threejs / map-viewer fleets 対応方針（後方互換）

## 背景

`hakoniwa-threejs-drone` は複数描画実装を持つが、入力経路は legacy 前提が強く、fleets の `DroneVisualStateArray` を直接扱う経路が弱かった。
このため、単機互換を維持しながら fleets 多数機体を扱える構成へ整理した。

## 目的

1. `legacy` モードの非破壊（既存構成を維持）
2. `fleets` モード追加（`DroneVisualStateArray` 入力）
3. 機体描画を固定台数依存から分離
4. `hakoniwa-map-viewer` 側も同一設定モデルへ統一

## 完了済み

- `legacy` / `fleets` のモード分離
- fleets での `dynamicSpawn` 運用（1テンプレートからN機体描画）
- `viewer-config-fleets` の共通利用（N=1/10/100）
- Sim Host / View Host 分離（別PCブラウザ）で接続成立
- 原点ゴースト事象（100機体時）を解消
  - 原因: bridge 側で chunk0 のみ転送
  - 対応: 1チャネル方針維持 + `max_drones_per_packet=100`

## 継続課題

- `maxDynamicDrones` 過大指定時の過剰生成抑止
- N=1 で余剰機体を生成しない厳密保証
- `maxDynamicDrones` の非リロード更新（必要時）
- dynamicSpawn 導入前後の N=1 描画負荷同等性の定量確認

## 運用指針

- fleets 可視化は以下 URL パラメータを明示する:
  - `dynamicSpawn=true`
  - `templateDroneIndex=0`
  - `maxDynamicDrones=<N>`
- `maxDynamicDrones` は現行実装では起動時パラメータ（変更時はリロード）
