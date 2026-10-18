# Hakoniwa Drone Simulator v4.1.1 → v4.2.0 アップデート手順

## はじめに

Hakoniwa Drone Simulator v4.2.0は、MuJoCo 3.16.0への更新と、PX4 SITL・ArduPilot SITLで実機に近い
センサーの届き方を再現する機能を標準にしたリリースです。機体設定に、設定の版と、設定を確かめた環境の
記録を足しました。

既存のv4.1.1タグは変更しません。v4.2.0は新しいコミットとOS別バイナリとして配布します。

## 対象バージョン

- 更新元: `v4.1.1`
- 更新先: `v4.2.0`
- MuJoCo: `3.13.0` → `3.16.0`

## 無償版の更新方法

無償版はソースではなく、次のOS別バイナリをGitHub Releasesから取得します。

| ファイル | 対象環境 |
| --- | --- |
| `mac.zip` | macOS Arm |
| `lnx.zip` | Ubuntu 22.04 / 24.04 |
| `win.zip` | Windows 11 |

既存のv4.1.1ディレクトリへ上書きせず、v4.2.0を新しいディレクトリへ展開して設定を移行することを
推奨します。異なるMuJoCoバージョンのヘッダ、共有ライブラリ、実行ファイルを混在させないでください。

## 主な変更

### MuJoCo 3.16.0

MuJoCoを3.13.0から3.16.0へ更新しました。`.mjb`はMuJoCoの版に依存するため、正本の`.xml`から
作り直してください（[MuJoCo XMLとMJB](architecture/config/aircraft-param.md#mujoco-xmlとmjb)）。

### 機体設定の版と、確かめた環境の記録

機体設定（`drone_config_*.json`）に、次の2項目を足しました。どちらも省略できます。

- `configVersion`：設定の形の版（例 `"4.2"`）。ない設定はv4.1.x以前の設定として、今までどおり読みます。
- `validatedWith`：その設定を作って確かめた環境（MuJoCoの版など）の記録。起動時にMuJoCoの版を比べ、違えば
  警告を出します。

v4.1.xの設定をそのまま使うと、起動時に次の警告が1行ずつ出ますが、動作には影響しません。

```text
WARNING: drone config has no configVersion; treating it as v4.1 or earlier
WARNING: drone config has no validatedWith metadata
```

詳しくは[機体のパラメータ説明](architecture/config/aircraft-param.md)の「設定の版と確かめた環境」を見てください。

### SITLで実機に近いセンサーの届き方を再現する機能

次の機能を標準にしました。どれも**設定を書いたときだけ効きます**。書かなければ今までどおりに動きます。

- センサーの遅れ（`delayMsec`。GNSSの解の遅れ、気圧計のフィルタなど）
- PX4へセンサーを送る周期（`simulation.sitl.sensor_period_msec`。物理1 ms・センサー4 msなど）
- センサーごとの更新の周期（`updatePeriodMsec`）
- GPSが申告する精度（`gps.accuracy`。旧`eph`/`epv`/`sacc`は非推奨）
- ジャイロのドリフト

PX4 SITL・ArduPilot SITLで使う設定は、[SITLで使う設定](architecture/config/aircraft-param.md#sitlで使う設定)に
まとめています。

## 更新後の確認項目

- 起動時に、MuJoCo 3.16.0が読み込まれること（`validatedWith.mujoco`を書いた設定では、版の違いの警告が出ないこと）。
- v4.1.1の設定で、今までどおりに飛ぶこと（上の2つの警告は出てよい）。
- `.mjb`を使っている場合は、3.16.0で作り直したこと。

## まとめ

v4.2.0は、MuJoCo 3.16.0への更新と、SITLで実機に近いセンサーの届き方を再現する機能を標準にしたリリースです。
v4.1.1の設定はそのまま使えます。SITLで飛ばす場合は、[SITLで使う設定](architecture/config/aircraft-param.md#sitlで使う設定)
を足してください。
