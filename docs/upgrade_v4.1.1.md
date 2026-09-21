# Hakoniwa Drone Simulator v4.1.0 → v4.1.1 アップデート手順

## はじめに

Hakoniwa Drone Simulator v4.1.1は、v4.1.0公開後の修正を取り込み、
MuJoCo 3.13.0対応とWindows版`DroneVisualStatePublisher`の配布を追加する
パッチリリースです。

既存のv4.1.0タグは変更しません。v4.1.1では、検証済みの新しいコミットと
OS別バイナリを`v4.1.1`として配布します。

## 対象バージョン

- 更新元: `v4.1.0`
- 更新先: `v4.1.1`
- MuJoCo: `3.9.0` → `3.13.0`

## 無償版の更新方法

無償版はソースではなく、次のOS別バイナリをGitHub Releasesから取得します。

| ファイル | 対象環境 |
| --- | --- |
| `mac.zip` | macOS Arm |
| `lnx.zip` | Ubuntu 22.04 / 24.04 |
| `win.zip` | Windows 11 |

既存のv4.1.0ディレクトリへ上書きせず、v4.1.1を新しいディレクトリへ展開して
設定を移行することを推奨します。異なるMuJoCoバージョンのヘッダ、共有ライブラリ、
実行ファイルを混在させないでください。

## 主な変更

### 箱庭ランタイム更新

箱庭ランタイムの修正を取り込みました。無償版では、ソースではなくv4.1.1の
OS別バイナリに検証済みのランタイムが含まれます。

### MuJoCo 3.13.0

`MUJOCO_VERSION.txt`を`3.13.0`へ更新しました。ビルド、インストール、Dockerは
このファイルを参照して各OS向けの公式MuJoCo SDKを取得します。

MuJoCo 3.13.0では`mjv_moveCamera()`のAPIから`mjvScene*`引数が削除されたため、
サンプルViewerを新しいAPIへ対応させています。

箱庭ドローンのリポジトリには配布対象のMJBファイルを含みません。利用者が以前の
MuJoCoで作成した外部MJBを使用している場合は、MuJoCo 3.13.0で再生成してください。

### Windows版DroneVisualStatePublisher

v4.1.1から、`win.zip`に次の実行ファイルを収録します。

```text
win/win-drone_visual_state_publisher.exe
```

これにより、macOS、Linux、Windowsの3環境でVSPの配布バイナリを利用できます。

| OS | VSP実行ファイル |
| --- | --- |
| macOS | `mac/mac-drone_visual_state_publisher` |
| Linux | `lnx/linux-drone_visual_state_publisher` |
| Windows | `win/win-drone_visual_state_publisher.exe` |

## 更新後の確認項目

- `VERSION.txt`が`4.1.1`
- `MUJOCO_VERSION.txt`が`3.13.0`
- 使用中のMuJoCo共有ライブラリが3.13.0
- 主要MJCF/XMLをロードできる
- 標準機体で離陸、ホバリング、着陸できる
- 地面接触と代表的な衝突ケースで異常がない
- サンプルViewerで回転、移動、ズームできる
- 利用OSのZIPにVSPが収録されている
- WindowsではVSPに必要な非システムDLLが解決できる

## まとめ

v4.1.1は、v4.1.0の機能範囲を維持しながら、MuJoCo 3.13.0への更新、
公開後の修正、Windows版VSPの配布をまとめた互換性・配布改善リリースです。
