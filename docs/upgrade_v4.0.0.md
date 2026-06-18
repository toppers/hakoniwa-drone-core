# Hakoniwa Drone Simulator v3.8.0 → v4.0.0 アップデート手順

## はじめに

Hakoniwa Drone Simulator v4.0.0 は、v3.8.0 で整理した fleets / hakoniwa-core-pro 基盤の上に、Mac 版バイナリ配布、MuJoCo 3.9.0 対応、制御アーキテクチャの再設計、外部制御アダプター接続、故障・外乱シナリオ連携を追加したメジャーアップデートです。

v3.8.0 では、主に `hakoniwa-core-pro` の build defaults、shared memory layout、fleets `N=200` 運用前提の固定上限整理を行いました。

v4.0.0 では、以下を中心に更新しています。

* 無償版ユーザ向け

  * Mac 版バイナリ配布に向けた実行環境整備
  * MuJoCo 3.9.0 対応
  * Mac 向け MuJoCo install/link ツールの整備
  * `hakoniwa-drone-core` への公開反映ツール更新
  * ローターモデル仕様の整理

* PRO ユーザ向け

  * Controller Orchestrator による制御アーキテクチャ再設計
  * Control Link による外部制御アダプター接続
  * PX4 control adapter 接続対応
  * Scenario Link による故障・外乱・環境条件連携
  * Disturbance PDU を用いたローター故障注入
  * tuning / PX4 autotuning 関連構成の拡張

本ドキュメントでは、v3.8.0 から v4.0.0 へ更新する際の変更点、アップデート手順、確認項目を説明します。

---

## 対象バージョン

* 更新元: `v3.8.0`
* 更新先: `v4.0.0`

`hakoniwa-drone-pro` 配下で以下を実行します。

```bash
git fetch --tags
git checkout v4.0.0
git submodule update --init --recursive
```

---

## 重要な互換ポイント

### 1. v4.0.0 はメジャーアップデート

v4.0.0 では、制御アーキテクチャ、PX4 adapter 連携、Disturbance PDU、ローター故障注入、MuJoCo バージョンなどに大きな変更があります。

既存環境を更新する場合は、古いバイナリや古い MuJoCo ライブラリと混在させず、関連バイナリを揃えて更新してください。

### 2. MuJoCo バージョンが 3.9.0 に更新

v4.0.0 では、MuJoCo の利用バージョンを `3.9.0` に更新しています。

Mac 版バイナリを利用する場合は、同梱または公開されている `MUJOCO_VERSION.txt` と同じバージョンの MuJoCo dylib を利用してください。

### 3. PRO 機能と無償版機能の扱い

v4.0.0 では、無償版で利用する機能と、PRO / オプションライセンスで扱う機能が混在しています。

無償版ユーザは、Mac 版バイナリ、MuJoCo install/link ツール、標準制御、標準箱庭アダプターを中心に利用してください。

Control Link、Scenario Link、PX4 adapter、tuning / autotuning 関連機能は、PRO ユーザ向けまたは個別契約に基づく機能として扱います。

---

# 無償版ユーザ向け変更点

## 1. Mac 版バイナリ配布対応

v4.0.0 では、Mac 版バイナリ配布に向けて、MuJoCo のインストールとリンク修正を行うためのツールを整備しました。

主な関連ツールは以下です。

```text
tools/install-mujoco-mac.bash
tools/link-mujoco-mac.bash
```

`install-mujoco-mac.bash` は、`MUJOCO_VERSION.txt` に記載された MuJoCo バージョンを参照し、macOS universal2 版の MuJoCo を取得して `vendor/mujoco` 配下に配置します。

`link-mujoco-mac.bash` は、配布バイナリが MuJoCo の dylib を参照できるように、実行ファイルの rpath / dylib 参照を調整します。

Mac 版バイナリを利用する場合の基本手順は以下です。

```bash
bash tools/install-mujoco-mac.bash .

bash tools/link-mujoco-mac.bash ./mac --lib-dir ./vendor/mujoco/lib
```

実行後、必要に応じて以下で MuJoCo の参照状態を確認してください。

```bash
otool -L ./mac/<binary-name> | grep -i mujoco
otool -l ./mac/<binary-name> | grep -A2 LC_RPATH
```

## 2. MuJoCo 3.9.0 対応

v4.0.0 では、MuJoCo の利用バージョンを `3.9.0` に更新しました。

このバージョンは `MUJOCO_VERSION.txt` により管理されます。

```text
MUJOCO_VERSION.txt
```

Mac 版バイナリ、ビルド環境、MuJoCo install/link ツールは、このファイルを基準に揃えてください。

## 3. hakoniwa-drone-core への公開反映ツール更新

無償版管理リポジトリである `hakoniwa-drone-core` へ反映するための update ツールを更新しました。

```text
tools/update-hakoniwa-drone-core.bash
```

v4.0.0 では、Mac 版バイナリ実行に必要な以下のファイルも `hakoniwa-drone-core` 側へコピーされます。

```text
tools/install-mujoco-mac.bash
tools/link-mujoco-mac.bash
MUJOCO_VERSION.txt
```

なお、tuning 関連ディレクトリは無償版の公開対象には含めません。

## 4. ローターモデル仕様の整理

ローターコンポーネントの仕様を整理し、最大回転数やバッテリー電圧を考慮したローターダイナミクスについてドキュメントを更新しました。

主な整理点は以下です。

* `components.rotor.max_rad_per_sec` による最大ローター回転数指定
* 未指定時の従来互換動作
* battery voltage aware rotor dynamics
* thrust / anti-torque / motor current の責務整理
* rotor component と thruster component の責務境界整理

---

# PRO ユーザ向け変更点

## 1. Controller Orchestrator による制御アーキテクチャ再設計

v4.0.0 では、制御処理の内部構造を再設計しました。

従来は Flight / Radio などの制御種別ごとに処理が分散していましたが、v4.0.0 では Controller Orchestrator を中心に、制御入力、制御意図、制御実行、ログ生成を整理しています。

主な設計方針は以下です。

* 公開インタフェースとして `IAircraftController` 互換性を維持
* 外部から見える Controller facade と内部制御実行責務を分離
* Flight / Radio / Tuning を Controller 種別ではなく control operation として扱う
* Backend の違いを制御フローではなく BackendSet の差し替えとして扱う
* RawInput を Context / Operation に分解
* common stage execution pipeline により実行順序を共通化

これにより、標準制御、RC操作、tuning、PX4 adapter などの制御経路を、より明確な境界で扱えるようになりました。

## 2. Control Link 対応

v4.0.0 では、箱庭ドローンPROと外部制御システムを接続するための Control Link を追加しました。

Control Link は、Adapter Interface を通して PX4 や独自制御プログラムを箱庭ドローンPROの仮想環境へ接続するためのオプションです。

対象となる主な interface は以下です。

* 高度/水平制御
* 姿勢角度制御
* 姿勢角速度制御
* ミキサー
* EKF

通常ビルドでは Control Link は無効です。

```bash
-DHAKO_ENABLE_CONTROL_LINK=OFF
```

Control Link を有効にする場合は、PX4 adapter などの外部制御アダプターを用意した上で、以下を利用します。

```bash
tools/build-adapter.bash build
```

PX4 adapter のインストール先を指定する場合は、以下のように指定できます。

```bash
tools/build-adapter.bash build /path/to/hakoniwa-drone-control-adapter-px4/install
```

または、

```bash
HAKO_PX4_CONTROL_ADAPTER_ROOT=/path/to/hakoniwa-drone-control-adapter-px4/install \
tools/build-adapter.bash build
```

## 3. PX4 control adapter / PX4-MuJoCo 構成の追加

v4.0.0 では、PX4 control adapter を利用するための設定ファイルやサンプル構成を追加しました。

主な追加対象は以下です。

```text
config/controller/px4-controller-config.json
config/controller/px4-controller-extra.json
config/controller/param-px4-mixer-mujoco.txt
config/drone/mujoco-px4/
config/launcher/drone-rc-px4-mac-mujoco.launch.json
```

これにより、PX4 側の制御パラメータを箱庭ドローンPROの制御 backend に接続し、MuJoCo 構成で動作確認するための土台を追加しています。

## 4. Scenario Link / Disturbance PDU 対応

v4.0.0 では、故障、外乱、センサノイズ、環境条件などを箱庭ドローンPROへ接続・反映するための Scenario Link を追加しました。

Scenario Link では、主に以下の入力を扱います。

* 風外乱
* 温度
* 気圧
* 周辺障害物情報
* センサノイズ
* 故障注入

これらの外乱系入力は、`Disturbance` PDU に集約され、箱庭ドローンPRO本体へ入力されます。

Scenario Link は専用の CMake ビルドオプションでは分離していません。利用可否は、ライセンス契約および提供されるシナリオ連携機能の利用条件によって扱います。

## 5. ローター故障注入の反映処理を追加

v4.0.0 では、`Disturbance` PDU で受け取ったローター故障注入情報を、各ローターの制御入力へ反映する処理を追加しました。

ローターごとに `0.0` から `1.0` の scale を適用し、制御入力を以下のように補正します。

```text
faulty_control = control * scale
```

scale の意味は以下です。

* `1.0`: 正常状態
* `0.0`: 完全故障
* `0.0` から `1.0` の間: 出力低下

scale は安全のため `0.0` から `1.0` の範囲に clamp されます。

これにより、モータ故障、ローター出力低下、片系出力低下などを含む検証シナリオを、機体ダイナミクスへ直接反映できるようになりました。

## 6. 外乱・環境条件の機体モデル反映

Scenario Link / Disturbance PDU の整理により、以下のような入力を機体側へ反映するための構成を追加・整理しました。

* 風外乱

  * 機体の運動計算に反映
  * MuJoCo 構成では相対風速から外力として適用
* 周辺障害物情報

  * 地面、壁、天井などの代表点と法線方向を利用
  * 境界面近接外乱の計算に利用
* 温度

  * バッテリーモデルの入力として利用
* 気圧

  * センサおよび機体運動に関係する環境条件として利用
* センサノイズ / 故障注入

  * `d_user_custom` の拡張領域を利用

---

# ビルド手順

## 通常ビルド

macOS:

```bash
bash tools/build-mac.bash build
```

Ubuntu:

```bash
bash tools/build-ubuntu.bash build
```

Windows:

```powershell
.\tools\build-win.ps1
```

## Control Link / PX4 adapter 有効ビルド

PX4 adapter を利用する場合は、PX4 adapter を事前にインストールした上で以下を実行します。

```bash
tools/build-adapter.bash build
```

インストール先を明示する場合:

```bash
tools/build-adapter.bash build /path/to/hakoniwa-drone-control-adapter-px4/install
```

または、

```bash
HAKO_PX4_CONTROL_ADAPTER_ROOT=/path/to/hakoniwa-drone-control-adapter-px4/install \
tools/build-adapter.bash build
```

---

# アップデート後の確認項目

## 1. バージョン確認

```bash
cat VERSION.txt
```

期待値:

```text
4.0.0
```

```bash
cat MUJOCO_VERSION.txt
```

期待値:

```text
3.9.0
```

## 2. Mac 版 MuJoCo インストール確認

```bash
bash tools/install-mujoco-mac.bash .
```

以下が作成されることを確認します。

```text
vendor/mujoco/MuJoCo.framework
vendor/mujoco/include/mujoco
vendor/mujoco/lib/libmujoco.3.9.0.dylib
```

## 3. Mac 版バイナリの MuJoCo link 確認

```bash
bash tools/link-mujoco-mac.bash ./mac --lib-dir ./vendor/mujoco/lib
```

確認例:

```bash
otool -L ./mac/<binary-name> | grep -i mujoco
otool -l ./mac/<binary-name> | grep -A2 LC_RPATH
```

## 4. 通常ビルド確認

macOS:

```bash
bash tools/build-mac.bash build
```

Ubuntu:

```bash
bash tools/build-ubuntu.bash build
```

## 5. Control Link ビルド確認

Control Link / PX4 adapter を利用する場合:

```bash
tools/build-adapter.bash build
```

または、

```bash
HAKO_PX4_CONTROL_ADAPTER_ROOT=/path/to/hakoniwa-drone-control-adapter-px4/install \
tools/build-adapter.bash build
```

## 6. ローター故障注入の動作確認

Scenario Link / Disturbance PDU を利用する構成では、ローターごとの fault scale が機体挙動へ反映されることを確認してください。

確認観点:

* `scale=1.0` では通常挙動と一致すること
* `scale=0.0` では対象ローターが完全故障相当になること
* `0.0 < scale < 1.0` では対象ローターの出力低下として挙動すること
* scale が `0.0` から `1.0` の範囲に clamp されること

## 7. hakoniwa-drone-core 反映確認

無償版管理リポジトリへ反映する場合:

```bash
bash tools/update-hakoniwa-drone-core.bash /path/to/hakoniwa-drone-core
```

反映後、`hakoniwa-drone-core` 側で以下を確認します。

```bash
ls tools/install-mujoco-mac.bash
ls tools/link-mujoco-mac.bash
ls MUJOCO_VERSION.txt
```

また、tuning 関連が無償版側へ混入していないことを確認します。

```bash
find . -path "*tuning*" -print
find . -path "*pid_tuning*" -print
find . -path "*px4-autotuning*" -print
```

---

# 既知の注意点

## Mac 版バイナリの実行パス

Mac 版バイナリを展開するパスには、日本語や空白を含めないことを推奨します。

## MuJoCo dylib の参照

Mac 版バイナリが MuJoCo dylib を見つけられない場合は、以下を確認してください。

* `MUJOCO_VERSION.txt` と dylib のバージョンが一致しているか
* `vendor/mujoco/lib/libmujoco.3.9.0.dylib` が存在するか
* `tools/link-mujoco-mac.bash` を実行済みか
* `otool -L` で MuJoCo 参照が確認できるか
* `otool -l` で rpath が確認できるか

## PRO 機能の利用範囲

Control Link、Scenario Link、PX4 adapter、tuning / autotuning 関連機能は、PRO ユーザ向けまたは個別契約に基づく機能として扱います。

無償版ユーザ向けの `hakoniwa-drone-core` へ反映する際は、tuning 関連資産が含まれないようにしてください。

---

# まとめ

v4.0.0 は、v3.8.0 の fleets / core-pro 基盤整理を前提に、Mac 版バイナリ配布と MuJoCo 3.9.0 対応を進めるとともに、PRO 向けには外部制御接続と故障・外乱シナリオ検証を大きく拡張したメジャーアップデートです。

無償版ユーザにとっては、Mac での導入・実行導線が整備されたリリースです。

PRO ユーザにとっては、Controller Orchestrator、Control Link、Scenario Link、PX4 adapter、ローター故障注入により、制御ソフトウェアや故障・外乱条件を含む検証シナリオを、より明確な構成で扱えるようになったリリースです。
