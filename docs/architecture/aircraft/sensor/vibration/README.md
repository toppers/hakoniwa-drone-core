# プロペラ由来の IMU 振動（実験的なオプション）

ロータの実際の回転数に同期した周期的な揺れを、IMU（加速度・ジャイロ）が測る値に足す、**実験的なオプション**です。
5 つのセンサ（加速度・ジャイロ・地磁気・気圧・GPS）の仕様は変えません。振動は、センサに入る**外乱**として、センサの手前で足します。

[センサ共通仕様](../README.md) を正本とします。[加速度](../acceleration/README.md)と[ジャイロ](../gyro/README.md)の「真値 → 取り付け位置姿勢 → 遅れ → 測る → ノイズ・ドリフト → 分解能・頭打ち」の流れは変えません。

## 1. 目的と対象

- ロータの実際の回転速度に同期する周期的な揺れを、**IMU の取り付け点での等価な観測外乱**として作り、加速度 [m/s²] とジャイロ [rad/s] に別々に足します。 `[SEN-VIB-010]`
- モデルは `rpm-harmonics` です。各ロータの基本波（1/rev）と、整数倍の高調波（2/rev など）を重ねます。羽根の枚数を B とすると B/rev が羽根の通過周波数です（2/rev を羽根の通過周波数と呼ぶのは 2 枚羽根のときだけ）。 `[SEN-VIB-020]`
- 足すのは IMU が測る値だけです。機体の弾性変形や振動の外力を MuJoCo では解きません。振幅は経験的な値で、実機のログで決めるまでは「実機と一致する」とは言いません。 `[SEN-VIB-030]`

## 2. 部品と責務

```text
ロータ（実際の角速度 rad/s、回転の向き）
    |
    v
振動の生成器（オプション）  物理の刻みごとに 1 回。生の振動だけを作る
    |  1/rev・2/rev … の生の波形（FRD、IMU の取り付け点）
    v
加速度・ジャイロのモデル（v2）
    真値 + 振動 → 向き → 感度 → IMU のフィルタ（オプション、共通仕様 4.5） → 遅れ → 測る → …
```

振動を弱めるフィルタは、生成器ではなく **IMU の側**の部品です（共通仕様 4.5）。生成器は生の振動を作るだけで、フィルタは真値と振動を合わせた値にかかります。

- `components.propellerVibration` を書かないか、`enabled` が false なら、生成器を**作りません**。センサモデル v2 の出力・ログ・乱数の列は、ビット単位で変わりません。 `[SEN-VIB-040]`
- 入力は各ロータの**実際の**角速度 Ω_i [rad/s]、回転の向き、物理の刻み Δt です。出力は FRD の加速度 3 軸と角速度 3 軸です。生成器は、ロータやセンサのクラス、MuJoCo、PX4・ArduPilot を直接参照しません。 `[SEN-VIB-050]`
- 生成器は**1 ステップに 1 回だけ**進め、作った 1 サンプルを加速度とジャイロで共有します。各センサが別々に生成器を呼ぶと位相が 2 回進むので、そうしません。 `[SEN-VIB-060]`
- ロータの更新のあと、IMU の観測の前に呼びます。回転数はロータの実際の角速度を使い、指令の Duty から推測しません。 `[SEN-VIB-070]`
- 推力・トルクを直接入れるモードなど、ロータの実際の回転数がないモードで有効にしたときは、起動時にエラーにします。 `[SEN-VIB-080]`

### 2.1 センサへの足し方

加速度（r は機体の原点から見た IMU の位置、R は取り付け姿勢）：

```text
f_point = f_origin + α_truth × r + ω_truth × (ω_truth × r)
f_input = f_point + δa_vibration_body
f_sensor = Rᵀ f_input → 感度 → 遅れ → 測る → ずれ・ノイズ・ドリフト → 分解能 → 頭打ち
```

ジャイロ：

```text
ω_input = ω_truth_body + δω_vibration_body
ω_sensor = Rᵀ ω_input → 感度 → 遅れ → 測る → ずれ・ノイズ・ドリフト → 分解能 → 頭打ち
```

- 振動は真値ではなく、IMU の取り付け点の観測外乱です。δω_vibration を剛体の α×r・ω×(ω×r) に入れません。MuJoCo の機体の状態にも戻しません。 `[SEN-VIB-090]`
- 足すのは IMU の向きの変換・感度の**前**です。遅れ、測る周期、分解能、測定範囲は、振動を含めた入力全体にかかります。生成器の側で、向きの変換や頭打ちを二重にかけません。 `[SEN-VIB-100]`
- この振動は、白色ノイズや Gauss-Markov のドリフトで代わりにしません。

## 3. 回転数に同期する高調波

ロータ i の回転速度の大きさ Ω_i ≥ 0 と回転の向き s_i ∈ {−1, +1} を使います。位相は物理の刻みごとに積み上げます。

```text
θ_i[k+1] = wrap(θ_i[k] + s_i Ω_i[k+1] Δt)
q_i[k+1] = (Ω_i[k+1] / Ω_ref)²
v_i,h     = q_i[k+1] sin(h θ_i[k+1] + φ_h)

δa_raw[k+1] = Σ_i Σ_h A_acc[h]  ⊙ v_i,h
δω_raw[k+1] = Σ_i Σ_h A_gyro[h] ⊙ v_i,h
```

A_acc[h] は FRD の 3 軸の振幅 [m/s²]、A_gyro[h] は FRD の 3 軸の振幅 [rad/s] で、基準の回転数（`referenceRpm`）で IMU に現れる振幅です。⊙ は軸ごとの掛け算です。符号付きの振幅で、軸ごとの 180° の位相の反転を表せます。

- θ_i はロータごとの位相です。回転の向きが −1 のロータは、位相が逆に進みます。sin(Ω(t)·t) の形は、回転数が変わると不連続になるので使いません。Ω_i = 0 のとき寄与は 0 で、位相はそのまま保ちます。 `[SEN-VIB-110]`
- Ω² は、回転体の不釣り合いの力 F ≈ m_e r Ω² から来る、経験的な最初の近似です。構造の伝わり方 H_i(f) で実際の IMU の振幅は変わるので、共振を含めた定量的な一致は保証しません。 `[SEN-VIB-120]`
- 揺れは確定的な周期の信号です。初めの位相は、`simulation.randomSeed`、機体の名前・番号、ロータの番号から、ほかのセンサのノイズとは別の乱数の列で決めます。リセットすると同じ波形に戻ります。`randomSeed` がないときは、生成器を作るときに決め、リセットでその値に戻ります。 `[SEN-VIB-130]`
- ロータの回転数に上限は設けません。飛行中の回転数で止めることはしません。 `[SEN-VIB-135]`
- 作る時点での折り返しを防ぐため、機体の最大の回転速度 Ω_max と高調波の次数 h から、いちばん高い成分 h·Ω_max/(2π) が、作る周期のナイキスト周波数（物理 1 ms なら 500 Hz）より下であることを、起動時に確かめます。超える次数があれば、起動時のエラーにします。Ω_max は、ロータの `max_rad_per_sec`（書いていなければ、Drone PRO の既定と同じくホバーの回転速度の 2 倍）です。x500（1032 rad/s、1/rev は 164 Hz）では、1/rev・2/rev を使います（3/rev 以上は、要るときに考えます）。 `[SEN-VIB-137]`

## 4. 設定

```json
{
  "components": {
    "propellerVibration": {
      "enabled": true,
      "model": "rpm-harmonics",
      "referenceRpm": 5590,
      "harmonics": [
        {
          "order": 1,
          "accelAmplitudeMps2": [1.0, 1.0, 1.5],
          "gyroAmplitudeRadps": [0.05, 0.05, 0.05]
        },
        {
          "order": 2,
          "accelAmplitudeMps2": [0.4, 0.4, 0.6],
          "gyroAmplitudeRadps": [0.02, 0.02, 0.02]
        }
      ],
      "aliasAttenuationDb": 40
    },
    "sensors": {
      "acc":  { "updatePeriodMsec": 4, "filter": { "type": "chebyshev2", "order": 6, "stopbandHz": 125, "stopbandAttenuationDb": 40 } },
      "gyro": { "updatePeriodMsec": 4, "filter": { "type": "chebyshev2", "order": 6, "stopbandHz": 125, "stopbandAttenuationDb": 40 } }
    }
  }
}
```

フィルタ（`components.sensors.acc.filter`・`gyro.filter`）は、IMU の設定です（共通仕様 4.5）。上は、振動の実験のための例です。

**振幅は試験のための仮の値です。実機の x500 の特性を表すものではありません。** `[SEN-VIB-200]`

| 設定 | 決まり |
|---|---|
| `components.propellerVibration` | `components.sensors` とは別の設定。書かないか `enabled` が false なら OFF |
| `enabled` | true・false だけ |
| `model` | 有効なときは必須。`rpm-harmonics` だけ |
| `referenceRpm` | 有効なときは必須。有限で正の数 |
| `harmonics[]` | 有効なときは空でない配列。`order` は正の整数で、同じ `order` を重ねない |
| `accelAmplitudeMps2` | 有限の数 3 つ（FRD、m/s²） |
| `gyroAmplitudeRadps` | 有限の数 3 つ（FRD、rad/s） |
| `phaseDeg` | 高調波ごとの位相（度）。省略したときは 0 |
| `aliasAttenuationDb` | 有効なときは必須。読む周期のナイキスト周波数より上の振動を、IMU のフィルタがどれだけ弱めなければならないか（dB、正の数。5 章） |

有効なときに、足りない・誤った値、未知の設定やモデルがあれば、起動時のエラーにします。センサモデル v2 を使わないビルドで有効にしたときも、エラーにします。 `[SEN-VIB-140]`
振動を有効にしても、`components.sensors.imu.mount` や `acc`・`gyro` の設定の意味は変わりません。

## 5. 読む周期と折り返し

- 波形を作る周期（物理の刻み、1 ms なら 500 Hz まで）、IMU を読む周期（`updatePeriodMsec`）、SITL へ送る周期、EKF・制御が使う周期を区別します。たとえば IMU を 4 ms で読むと、表せるのは 125 Hz までです。約 5,600 rpm の 2/rev（約 187 Hz）を、ならさずに 4 ms で取ると、約 63 Hz に折り返します。 `[SEN-VIB-150]`
- 生成器は生の振動を作るだけで、フィルタを持ちません。読む前の折り返しは、**IMU のフィルタ**（共通仕様 4.5）で防ぎます。フィルタは、真値と振動を合わせた値に、物理の刻みごとにかかり、測る（4 ms）より前に働きます。 `[SEN-VIB-160]`
- 振動を有効にしたときは、加速度・ジャイロのどちらにも IMU のフィルタが要ります。さらに、各フィルタの利得が、読むいちばん長い周期（`updatePeriodMsec`、SITL の送る周期）のナイキスト周波数から、振動のいちばん高い成分（h·Ω_max/(2π)）までのすべての周波数で、−`aliasAttenuationDb` 以下でなければなりません。満たさないときは、起動時のエラーにします。回転数にかかわらず、ナイキストより上の振動は、決めた量以上に弱まってから読まれます。 `[SEN-VIB-165]`
- 例（物理 1 ms、Chebyshev II・6 次・阻止域の端 125 Hz・40 dB）の利得は、次のとおりです。

| 周波数 | 50 Hz | 93 Hz | 110 Hz | 125 Hz 以上 |
|---|---|---|---|---|
| 利得 | 0.0 dB | −4.3 dB | −17.8 dB | −40 dB 以下 |

- IMU のフィルタは、真値にもかかるので、制御が受け取る値も遅れます（例の設定で、遅い動きに対して約 4.7 ms）。これは、シミュレーションすべき IMU の特性として扱います（共通仕様 4.5）。
- 対象の経路は、PX4 Control Link・PX4 SITL・ArduPilot Control Link です。PX4 SITL へ IMU を送る周期（4 ms）は変えません。 `[SEN-VIB-170]`
- ArduPilot SITL は、ArduPilot の中で IMU と振動（`SIM_VIB_*`）を作ります。箱庭の振動は ArduPilot SITL には送りません。`SIM_VIB_*` を使う実験は別に扱い、二重に入れません。係数や位相の一致は言いません。
- 4 ms で読む経路では、約 186 Hz の 2/rev を自動操縦のノッチフィルタで消す評価はしません（IMU のフィルタで弱まってから読まれるため）。この評価には、高い速さで IMU を渡す入力を別に設計します。 `[SEN-VIB-175]`
- 振動を有効にした閉ループの試験（飛行）は、IMU のフィルタの受け入れ試験（テスト設計 4 章）と、合わせたセンサ値の試験に合格した構成で行います。 `[SEN-VIB-178]`

## 6. 互換、記録、評価

- OFF のときは、計算・乱数の消費・ログの形を増やしません。ON のときも、同じ回転数の列・条件・種なら、同じ波形になります。 `[SEN-VIB-180]`
- 振動を有効にした実験では、次を区別して記録できるようにします。各ロータの実際の速さ（`log_rotor_N.csv`）、生成器の生の波形（1 ms、加速度 3 軸・角速度 3 軸、ロータごとの寄与）、センサの最終の値（`log_acc.csv`・`log_gyro.csv`）。生の波形は FFT で確かめられるよう、物理の刻みごとに書き出します。 `[SEN-VIB-190]`
- 振動の大きさは、ロータごとの寄与と、合わせた IMU の振動の RMS を分けて評価します。同じ回転数のロータどうしは位相で強め合ったり弱め合ったりするので、合わせた RMS はロータごとの RMS の二乗和の平方根にはなりません。 `[SEN-VIB-195]`
- OFF なら、機体の物理の状態もセンサの値も変わりません。ON でも生成器は MuJoCo に外力を加えませんが、制御の入力が変われば、閉ループで機体の軌道は変わってかまいません。
- このモデルで確かめられるのは「決めた周期的な外乱が、推定・フィルタ・制御にどう効くか」です。実機の構造の共振、振動の整流、温度、弾性のモードは扱いません。実機と同じことを示すには、高い速さの IMU と回転数のログで係数を決め、別の飛行の区間で PSD・RMS・ピークの位置を確かめます。

## 7. 文献と参照した実装

### 文献

- Ghalamchi, B. and Mueller, M. W., *Vibration-Based Propeller Fault Diagnosis for Multicopters* (2018), [著者公開 PDF](https://hiperlab.berkeley.edu/wp-content/uploads/2018/05/2018_Vibration-basedPropellerFault.pdf)。回転数と振動のスペクトルの関係を使った故障診断。
- Baldini, A. et al., *Real-time propeller fault detection for multirotor drones based on vibration data analysis*, Engineering Applications of Artificial Intelligence 123 (2023), 106343, [DOI](https://doi.org/10.1016/j.engappai.2023.106343)。実機の IMU の振動からの故障診断。
- Balandi, L., Robuffo Giordano, P. and Tognon, M., *Enhancing IMU Accuracy in MRAVs: A Theoretical and Experimental Approach to Vibration Damping*, ICUAS (2025), [DOI](https://doi.org/10.1109/ICUAS65942.2025.11007828)。機械的な振動と防振の実験。
- Baldini, A. et al., *Modeling the Effects of Blade Damage in Multirotors Dynamics*, Journal of the Franklin Institute (2026), 109032, [DOI](https://doi.org/10.1016/j.jfranklin.2026.109032)。損傷時の高調波の励振と構造の減衰。
- Baldini, A. et al., *Active Propeller Fault Detection and Isolation in Multirotors Via Vibration Model* (2026, プレプリント), [arXiv](https://arxiv.org/abs/2604.07281)。振動のモデルを使った故障の分離。

### 参照した実装（比べる対象。ソースは写さない）

- [ArduPilot `AP_InertialSensor_SITL.cpp`](https://github.com/ArduPilot/ardupilot/blob/master/libraries/AP_InertialSensor/AP_InertialSensor_SITL.cpp)：回転数に同期する振動・高調波（`SIM_VIB_*`）。ArduPilot は GPL-3.0-or-later なので、コードは写さず、一般的な高調波の式から独立に作ります。
- [PX4 `sih.cpp`](https://github.com/PX4/PX4-Autopilot/blob/main/src/modules/simulation/simulator_sih/sih.cpp)：IMU のノイズの作り方（振動とは別）。
- [PX4 `VehicleIMU.cpp`](https://github.com/PX4/PX4-Autopilot/blob/main/src/modules/sensors/vehicle_imu/VehicleIMU.cpp)：振動の指標、IMU の積算。
- [Gazebo `ImuSensor.cc`](https://github.com/gazebosim/gz-sensors/blob/main/src/ImuSensor.cc)、[Project AirSim `imu.cpp`](https://github.com/iamaisim/ProjectAirSim/blob/main/core_sim/src/sensors/imu.cpp)、[Pegasus `imu.py`](https://github.com/PegasusSimulator/PegasusSimulator/blob/main/extensions/pegasus.simulator/pegasus/simulator/logic/sensors/imu.py)：ふつうのノイズ・バイアスのモデル（比べる対象）。

## 8. 要求の一覧

| 番号 | 要求 | 章 |
|---|---|---|
| SEN-VIB-010 | IMU の取り付け点での、加速度・角速度の周期的な観測外乱 | 1 |
| SEN-VIB-020 | ロータの実際の回転数の基本波・高調波を使う | 1 |
| SEN-VIB-030 | 実機と同じとは、ログで確かめる前に言わない。MuJoCo には振動を加えない | 1 |
| SEN-VIB-040 | OFF は生成器を作らず、v2 の出力はビット単位で同じ | 2 |
| SEN-VIB-050 | 具体的なクラスに頼らず、実際の回転数から FRD の 2 つの 3 軸の信号を出す | 2 |
| SEN-VIB-060 | 物理の刻みに 1 回だけ進め、サンプルを共有する | 2 |
| SEN-VIB-070 | ロータの実際の角速度を使い、物理の更新のあと・IMU の更新の前に足す | 2 |
| SEN-VIB-080 | 回転数のないモードで有効ならエラー | 2 |
| SEN-VIB-090 | 振動の角速度を剛体の加速度の補正に使わない。真値・物理を変えない | 2.1 |
| SEN-VIB-100 | センサの向きの変換と誤差・測る・頭打ちの前で足す | 2.1 |
| SEN-VIB-110 | 回転数を積み上げた位相。逆向きのロータは逆に進む。止まると寄与 0・位相は保つ | 3 |
| SEN-VIB-120 | Ω² の比例は経験的な近似として扱う | 3 |
| SEN-VIB-130 | 種・機体・ロータごとの初めの位相と、リセットでの再現 | 3 |
| SEN-VIB-135 | ロータの回転数に上限を設けない | 3 |
| SEN-VIB-137 | 最大の回転速度 × 高調波の次数が、作る周期のナイキスト周波数を超えたら起動時のエラー | 3 |
| SEN-VIB-140 | 設定の決まりと、誤った値・v2 なしのビルドでの拒否 | 4 |
| SEN-VIB-150 | 物理・IMU・SITL・EKF の周期を区別する | 5 |
| SEN-VIB-160 | 生成器は生の振動だけを作る。折り返しは IMU のフィルタ（共通仕様 4.5）で、測る前に防ぐ | 5 |
| SEN-VIB-165 | 振動が有効なら、加速度・ジャイロの IMU のフィルタが、ナイキストから振動のいちばん高い成分まで −`aliasAttenuationDb` 以下。満たさなければ起動時のエラー | 5 |
| SEN-VIB-170 | 対象の経路と、PX4 SITL の送る周期（4 ms）は変えないこと。ArduPilot SITL には送らない | 5 |
| SEN-VIB-175 | 4 ms の経路では 2/rev のノッチの評価をしない | 5 |
| SEN-VIB-178 | 振動を有効にした閉ループの試験は、IMU のフィルタの受け入れ試験と合わせたセンサ値の試験に合格した構成で行う | 5 |
| SEN-VIB-180 | OFF で何も増やさない。ON で再現できる | 6 |
| SEN-VIB-190 | 回転数・生の波形・フィルタのあと・センサの最終の値を分けて記録する。生の波形は物理の刻みごと | 6 |
| SEN-VIB-195 | ロータごとの寄与と、合わせた IMU の振動の RMS を分けて評価する | 6 |
| SEN-VIB-200 | 振幅は試験のための仮の値で、実機の特性とは言わない | 4 |
