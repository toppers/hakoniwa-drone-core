# Hakoniwa Drone Simulator v4.0.1 → v4.1.0 アップデート手順

## はじめに

Hakoniwa Drone Simulator v4.1.0 は、v4.0.1 の Control Link / Scenario Link 基盤を拡張し、**ローター故障時の制御差し替え、可変ローター数、SITL 時刻同期、ArduPilot/PX4 周辺の実運用導線、MuJoCo/Viewer、tuning、納品パッケージ作成**を強化したマイナーアップデートです。

特に PRO ユーザ向けには、次の変更が中心です。

- 単一ローター故障時の Control Allocation 差し替えサンプル
- `ControlAllocationInput` から現在姿勢 `roll/pitch/yaw` と body-frame 角速度 `p/q/r` を参照可能化
- 4 ローター固定から最大 16 ローターまで扱える可変ローター数対応
- PX4 / ArduPilot SITL の actuator-event-driven 実行と箱庭時刻同期
- PX4 へ pymavlink から速度指令を送る Offboard サンプルの追加
- MuJoCo MJB 読み込み、FPV picture-in-picture などの実行環境改善
- PID tuning / autotune の profile・timing 周辺改善
- `full` ZIP / `source` tar.xz の 2 種類の納品アーカイブ作成対応

本ドキュメントでは、v4.0.1 から v4.1.0 へ更新する際の変更点、互換上の注意、更新後の確認方法を説明します。

---

## 対象バージョン

- 更新元: `v4.0.1`
- 更新先: `v4.1.0`

### 顧客向けアップデート方法

顧客環境では GitHub からの `git clone` / `git checkout` は前提としません。箱庭ラボから納品された v4.1.0 の ZIP を受領し、新しいディレクトリへ展開して利用してください。

納品 ZIP の例:

```text
hakoniwa-drone-pro-v4.1.0.zip
hakoniwa-drone-pro-v4.1.0.zip.sha256
```

更新時は、既存の v4.0.1 ディレクトリへ直接上書きせず、v4.1.0 を別ディレクトリへ展開することを推奨します。必要に応じて、顧客固有の設定ファイルや利用中の機体設定を新しい環境へ移してください。

ZIP 内の `DELIVERY_REVISION.txt` には、納品対象の tag、commit SHA、submodule SHA が記録されています。SHA-256 ファイルと併せて納品物を確認できます。

今回の更新では CMake option、Control Adapter、Aircraft/SITL 周辺の型・実装が変更されているため、既存 build tree の使い回しは避け、クリーンビルドを推奨します。

macOS:

```bash
bash tools/build-mac.bash clean
bash tools/build-mac.bash build
```

Ubuntu:

```bash
bash tools/build-ubuntu.bash clean
bash tools/build-ubuntu.bash build
```

---

## 重要な互換ポイント

### 1. 可変ローター数は PRO ビルドオプションで制御

v4.1.0 では、ローター数を固定 4 基から拡張し、最大 16 基まで扱える内部構造を導入しました。

PRO 側のビルドオプションは次です。

```text
HAKO_ENABLE_VARIABLE_ROTOR_COUNT
```

有効時は機体定義の `rotorPositions` 数に応じて Mixer / Aircraft / Thrust Dynamics / SITL actuator mapping を構成します。

無効時は従来互換の 4 ローター構成のみを受け付け、4 基以外の機体定義は起動時に拒否します。

既定の PRO build manifest では次の設定です。

```yaml
features:
  variable_rotor_count: true
```

既存の 4 ローター機体定義はそのまま利用できます。

### 2. SITL 時刻同期 option の整理

従来の PX4 固有 option から、PX4 / ArduPilot 共通の SITL 時刻同期へ整理しました。

新しい option は次です。

```text
HAKO_SITL_ASSET_TIME_SYNC
```

既定値は `ON` です。

```yaml
features:
  sitl_asset_time_sync: true
```

SITL actuator 受信を起点に機体物理を進め、箱庭側 asset time との barrier で同期します。これにより、PX4 と ArduPilot を共通の Aircraft Service 同期モデルで扱えるようになりました。

旧 `HAKO_PX4_EVENT_DRIVEN_LOCKSTEP` を独自 build script や manifest から指定している場合は、新しい option へ移行してください。

### 3. Aircraft / Mixer 周辺を利用する独自コードは再ビルド推奨

可変ローター数対応に伴い、ローター構成・ローターダイナミクスの内部保持が固定配列から可変長構造へ変更されています。また、Control Allocation 周辺の入力にも現在状態が追加されています。

PRO の公開ヘッダや `src/` 内部クラスを直接利用している独自コードがある場合は、v4.1.0 のヘッダで再ビルドしてください。

### 4. `p/q/r` は Euler 角速度ではなく body-frame 角速度

Control Allocation へ追加された `p/q/r` は、body FRD 座標系で表現した角速度 `[rad/s]` です。

```text
p : body +X (Forward) 軸まわり
q : body +Y (Right) 軸まわり
r : body +Z (Down) 軸まわり
```

`roll_dot / pitch_dot / yaw_dot` ではありません。

姿勢は body FRD の local NED に対する Euler 姿勢として、次で取得できます。

```cpp
input.attitude.roll_rad
input.attitude.pitch_rad
input.attitude.yaw_rad

input.angular_rate.p
input.angular_rate.q
input.angular_rate.r
```

---

# v4.1.0 の主な新機能・変更点

## 1. Rotor Fault Control example

`examples/rotor-fault-control/` に、単一ローター完全故障時の Control Allocation 差し替え例を追加しました。

サンプルは Control Adapter の正式な拡張境界である `IControlAllocationBackend` を利用し、次の流れを示します。

```text
Normal
  -> 標準 Control Allocation

単一ローター完全故障
  -> TwoRotorEmergency
  -> 故障ローターを停止
  -> 対向ローターを policy 停止
  -> 残る 2 ローターへ collective thrust を等配分

復旧
  -> Normal
```

このサンプルは高度な耐故障制御則そのものを完成実装するものではなく、利用者が論文・研究由来の allocation を実装するためのカスタマイズ境界を提供します。

主なカスタマイズポイントは次です。

```cpp
calculate_active_rotor_speeds_rad_per_sec(
    const ControlAllocationInput& input,
    std::size_t physically_failed_rotor)
```

v4.1.0 では、この引数から現在姿勢と body-frame 角速度も参照できます。

関連:

```text
examples/rotor-fault-control/README.md
examples/build.md
examples/test.md
```

## 2. Control Adapter へ現在状態を伝搬

Controller がその tick で使用した現在状態を Mixer / Control Allocation 境界まで伝搬します。

```text
Controller input
  euler_x/y/z
  p/q/r
      |
      v
Controller output current_state
      |
      v
AdapterAircraftMixer
      |
      v
ControlAllocationInput
  attitude
  angular_rate
```

これにより、故障制御、state-dependent allocation、研究用 control law で機体姿勢・角速度を直接利用できます。

また、Attitude Control Backend 側でも body angular rate と controller `dt_sec` を利用できるように整理されています。

## 3. 可変ローター数と Generic Control Allocation

4 ローター固定の内部実装を整理し、最大 16 ローターまで扱える構造へ拡張しました。

主な変更点:

- rotor geometry 数を機体 config から取得
- Aircraft / Thrust Dynamics のローター保持を可変長化
- hover rotor speed を実ローター数から算出
- Generic Control Allocation Backend を追加
- geometry の妥当性・rank を起動時に検証
- effectiveness matrix 等を事前計算して runtime で再利用
- SITL actuator channel と local rotor index の mapping に対応

4 ローター機は従来どおり利用できます。

## 4. PX4 / ArduPilot SITL 実行基盤の整理

Aircraft Service を actuator-event-driven に整理し、PX4 / ArduPilot の actuator 受信と物理 step の責務を明確化しました。

主な変更点:

- fresh actuator message ごとに 1 physics step を実行
- bootstrap sensor 送信と steady-state 処理を分離
- 箱庭 asset time と aircraft time の双方向 barrier
- multi-aircraft 同期の診断ログ追加
- actuator timeout / recovery の診断改善
- ArduPilot raw PWM channel の取り扱い拡張
- PX4 / ArduPilot 共通 SITL timing utility の追加

ArduPilot については、実機由来 parameter の SITL 反映や Mission Planner を使った確認手順も追加しています。

## 5. PX4 pymavlink 速度指令サンプル

`drone_api/mavsdk/px4-sample2.py` に、PX4 Offboard へ pymavlink から速度指令を送るサンプルを追加・整理しました。

主な内容:

- `SET_POSITION_TARGET_LOCAL_NED` による速度指令
- Offboard へ入る前の setpoint stream の維持
- Local NED を基準にした相対高度での離陸
- 速度指令継続中の `LOCAL_POSITION_NED` 監視
- `triangle` / `step` の 2 種類の水平速度デモ

実行例:

```bash
python3 drone_api/mavsdk/px4-sample2.py \
  --udp udp:127.0.0.1:14540 \
  --demo triangle
```

`triangle` は水平 5 m/s の三角形軌道、`step` は 1 m/s の速度ステップを確認するためのデモです。

詳細は次を参照してください。

```text
drone_api/mavsdk/README.md
```

## 6. MuJoCo / Viewer 改善

MuJoCo 周辺では次の改善を行いました。

- `modelPath` に `.xml` だけでなく `.mjb` を指定可能
- MJB は Drone PRO と同じ MuJoCo version で生成したものを利用
- MuJoCo scene geometry capacity を model size から決定
- fixed camera `fpv` を使った picture-in-picture 表示
- `--mujoco-fpv-pip` オプション追加

MJB は version-bound な実行成果物です。Drone PRO 側の MuJoCo version を更新した場合は、正本 XML から再生成してください。

## 7. tuning / autotune 改善

PID tuning / autotune について、Python 実行環境、timing、profile 生成の一貫性を改善しました。

主な変更点:

- 子 Python process で `sys.executable` を利用
- timing profile を simulation / controller / EKF / PX4 runtime へ一括反映
- canonical manifest の差し替え対応
- PX4 controller / EKF parameter の profile 内コピー
- generated profile metadata の拡張
- RC runtime 生成モードの追加

既存 tuning profile を継続利用する場合でも、v4.1.0 で profile 生成ロジックを変更しているため、再現性を重視する場合は profile を再生成して確認することを推奨します。

## 8. Visual State Publisher / launcher 周辺の安定化

Visual State Publisher について、Hakoniwa asset 登録後の endpoint 初期化順序を整理し、PDU read/write fallback を追加しました。

また、launcher / web bridge 周辺では install prefix を固定 `/usr/local/hakoniwa` に依存しない構成へ整理しています。

## 9. 納品アーカイブの整理

`tools/nohin/nohin.bash` に `full` / `source` の 2 種類の納品アーカイブを追加しました。

完全版 ZIP:

```bash
bash tools/nohin/nohin.bash v4.1.0 full
```

生成物:

```text
hakoniwa-drone-pro-v4.1.0.zip
hakoniwa-drone-pro-v4.1.0.zip.sha256
```

軽量 source 版:

```bash
bash tools/nohin/nohin.bash v4.1.0 source
```

生成物:

```text
hakoniwa-drone-pro-v4.1.0-source.tar.xz
hakoniwa-drone-pro-v4.1.0-source.tar.xz.sha256
```

`source` 版は、メインリポジトリに加えて、ビルド・更新に必要な以下のソース依存を収録します。

- MAVLink C Library v2
- GLM
- Hakoniwa Core PRO とその nested dependency
- Hakoniwa Drone Control Adapter

一方で、画像、PDF、Office 文書、計測データ、ビルド済みバイナリなど、大容量または生成系のファイルは除外します。

多数の類似した生成済み MAVLink / PDU ヘッダを効率よく圧縮するため、`source` 版は ZIP ではなく `tar.xz` 形式です。生成した `source` アーカイブが 3,000,000 bytes を超えた場合はエラーにして納品を停止します。

顧客向けアップデート手順は、前述のとおり箱庭ラボから納品された ZIP を展開する運用を前提とします。`source` tar.xz は、メール添付などの軽量なソース確認・更新用途に利用できます。

各アーカイブ内の `DELIVERY_REVISION.txt` には対象 tag/branch、commit SHA、submodule SHA が記録されます。また、ルートの `THIRD_PARTY_NOTICES.md` に主な third-party component とライセンス情報を整理しています。

---

## アップデート後の確認

### 1. Drone PRO unit / regression test

macOS:

```bash
bash tools/build-mac.bash test
```

今回追加された Control Allocation state propagation を限定して確認する場合:

```bash
GTEST_FILTER='AdapterAircraftMixerStatePropagationTest.*:AircraftControlOutputStateTest.*' \
bash tools/build-mac.bash test
```

### 2. tuning runner

`src/cmake-build` を削除した場合、unit test の build だけでは tuning runner は再生成されません。

```bash
bash tools/build-mac.bash tuning
```

その後、必要に応じて autotune pipeline を実行してください。

### 3. Rotor Fault Control example

Business Pack Foundation を利用する環境では、以下で example の依存関係と build を確認できます。

```bash
python3 examples/rotor-fault-control/operator.py doctor
python3 examples/rotor-fault-control/operator.py build
```

実動作では、離陸後に単一ローター故障と復旧を入力し、`TwoRotorEmergency` / `Normal` の遷移を確認します。

### 4. source 納品 package

```bash
bash tools/nohin/nohin.bash v4.1.0 source
```

生成物:

```text
hakoniwa-drone-pro-v4.1.0-source.tar.xz
hakoniwa-drone-pro-v4.1.0-source.tar.xz.sha256
```

`DELIVERY_REVISION.txt`、`THIRD_PARTY_NOTICES.md`、SHA-256 を併せて確認してください。

---

## まとめ

v4.1.0 は、v4.0.1 で導入した Control Link / Scenario Link を実利用・研究用途へ広げるアップデートです。

特に、

- 故障制御を `IControlAllocationBackend` で差し替える境界
- current attitude / body angular rate の allocation への提供
- 可変ローター数
- PX4 / ArduPilot SITL 時刻同期
- PX4 pymavlink 速度指令サンプル
- tuning / MuJoCo / Viewer の運用改善
- full ZIP / 軽量 source tar.xz の納品アーカイブ
- third-party license notice の整理

を追加・整理しました。

既存の 4 ローター機・標準制御経路は維持しつつ、PRO 側でより多様な機体・制御・検証シナリオを構成できることが v4.1.0 の主な変更点です。
