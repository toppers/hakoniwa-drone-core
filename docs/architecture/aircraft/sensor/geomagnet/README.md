# 地磁気センサの仕様

地磁気センサに固有のことを書きます。全センサに共通の決まり（座標、取り付け位置姿勢、回転の式、処理の順番、
自動操縦との合わせ方）は [センサの共通仕様](../README.md) にあります。

## 1. 何を測るか

センサの位置での磁場を、**センサの軸**で測ります。単位は nT（ナノテスラ）です。 `[SEN-MAG-010]`

| 単位 | 換算 |
|---|---|
| 1 G（ガウス） | 100,000 nT |
| 1 mG（ミリガウス） | 100 nT |

### 1.1 地磁気（真値）

地磁気は、場所の設定 `simulation.location.magneticField` の 3 つの値で決まり、飛行中は変わりません。 `[SEN-MAG-020]`

| 設定 | 意味 | 単位 |
|---|---|---|
| `intensity_nT` | 地磁気の強さ F | nT `[SEN-MAG-030]` |
| `declination_deg` | 偏角 D（真北から東へ測った、磁北の向き） | 度 `[SEN-MAG-030]` |
| `inclination_deg` | 伏角 I（水平から下へ測った、磁力線の傾き） | 度 `[SEN-MAG-030]` |

3 つの値はどれも必ず書きます。1 つでも書かなければ、設定の誤りとしてエラーにします。 `[SEN-MAG-035]`

世界（NED）での地磁気のベクトルは、次のとおりです。 `[SEN-MAG-040]`

```text
m_ned = F · ( cos I · cos D,  cos I · sin D,  sin I )
```

- 例：東京付近では F ≒ 46,000 nT、D ≒ −7.5°（西偏）、I ≒ 49° です。
- 機体の軸での値は、機体の姿勢 R_nb（機体 → 世界）を使って m_body = R_nbᵀ · m_ned です。 `[SEN-MAG-050]`
- 地磁気は機体の大きさの範囲では変わらないので、センサの位置では変わりません。 `[SEN-MAG-060]`

## 2. 取り付け位置姿勢

地磁気センサは、IMU と同じ基板に載っている**内蔵**の地磁気センサとします。取り付け位置姿勢は、IMU のもの `[SEN-MAG-070]`
（`components.sensors.imu.mount`）を使います（共通仕様 2.2）。自動操縦の側でも、内蔵の地磁気センサとして扱います（5 章）。

- **姿勢だけを使います。** m_sensor = Rᵀ · m_body（R は共通仕様 2.3 の回転行列）。 `[SEN-MAG-080]`
- **位置は使いません。** 地磁気は機体の大きさの範囲では変わらないためです。 `[SEN-MAG-060]`

例：IMU を `yaw = 90` で付けると、機首を磁北に向けた機体では、地磁気の水平の成分がセンサの −y 軸に出ます。

## 3. 処理の順番

共通仕様 4 章の順番に、地磁気センサに固有の段を入れると次のとおりです。 `[SEN-MAG-090]`

```text
m_body → 姿勢（Rᵀ） → 軟鉄（S） → 硬鉄（b） → 遅れ → 測る → ノイズ → ドリフト → 分解能 → 頭打ち → m_sensor
```

| 段 | 設定（`components.sensors.mag.*`） | 内容 |
|---|---|---|
| 姿勢 | IMU の取り付け位置姿勢 | センサの軸へ回す |
| 軟鉄 | `softIron` | 機体の鉄などで磁場がゆがむ。下の 3.1 |
| 硬鉄 | `hardIronNT` | 機体の磁石などで、いつも同じ磁場が足される。下の 3.1 |
| 遅れ | `delayMsec` | ハードの遅れ（共通仕様 4 章） |
| 測る周期 | `updatePeriodMsec` | 新しい値を測る周期（共通仕様 4 章）。`sampleCount`（平均）は 1 だけ書ける（共通仕様 6 章） |
| ノイズ | `noise` | 正規分布の標準偏差（nT）。1 つの値（3 軸共通）か、軸ごとの [x, y, z]。0 以下の軸はノイズなし `[SEN-MAG-100]` |
| ノイズの密度 | `noiseDensity` | `noise` の代わりに書ける白色ノイズの密度（nT/√Hz）。σ に直す式と決まりは共通仕様 4.3。`noise` と両方は書けない `[SEN-COM-185]` |
| ドリフト | `drift` | ゼロ点のゆっくりした変化。`mode` は `gauss-markov`（共通仕様 4.2）。`stddevNT`（nT）、`correlationTimeSec`（秒）。ほかの `mode` はエラー（共通仕様 4.0） `[SEN-MAG-110]` |
| 分解能 | `resolutionNT` | 値の刻み。下の 3.2 |
| 頭打ち | `range.fullScaleGauss` | 測れる範囲（±G）。軸ごとに範囲で切る。下の 3.3 |

自動操縦が受け取ってから使うまでの遅れ（`softDelayMsec`）と、値を出す周期（`updatePeriodMsec`）は、
センサの値そのものではなく渡し方の設定です（共通仕様 4 章）。

### 3.1 硬鉄と軟鉄

地磁気センサの誤差の大部分は、センサそのものではなく、機体に載っている物から来ます。

- **硬鉄**（hard iron）：機体の磁石や磁化した部品が作る磁場。機体と一緒に回るので、センサの軸でいつも同じ量が足されます。
- **軟鉄**（soft iron）：機体の鉄などが地磁気をゆがめる効果。向きによって大きさが変わります。対称な 3×3 の行列 S で表します。 `[SEN-MAG-120]`

```text
m' = S · m + b      （m は姿勢で回したあとの値、軸はセンサの軸）
```

```json
"softIron": { "diagonal": [1.02, 0.98, 1.01], "offDiagonal": [0.01, -0.02, 0.005] },
"hardIronNT": [3000.0, -1500.0, 800.0]
```

- `softIron.diagonal`：S の対角 [S₀₀, S₁₁, S₂₂]。省略すれば [1, 1, 1]。 `[SEN-MAG-130]`
- `softIron.offDiagonal`：S の対角でない成分 [S₀₁, S₀₂, S₁₂]。S は対称（S₁₀ = S₀₁ など）。省略すれば [0, 0, 0]。 `[SEN-MAG-140]`
- `hardIronNT`：b（nT）。省略すれば [0, 0, 0]。目安は機体によって数百〜数千 nT。 `[SEN-MAG-150]`
- S は逆行列を持つこと（行列式が 0 でないこと）。 `[SEN-MAG-160]`
- 行列式の大きさが 1e-9 より小さいとき、または S・b に有限でない値があるときは、設定の誤りとしてエラーにします。 `[SEN-MAG-165]`

### 3.2 分解能

値の刻みです。各軸の値を、`resolutionNT` の整数倍のうち最も近いものに丸めます（頭打ちの前）。 `[SEN-MAG-170]`
ちょうど中間のときは、0 から遠い方にします。刻みは 3 軸共通です。 `[SEN-MAG-180]`

- 例：±8 G を 16 ビットで測るチップなら、16 × 100,000 / 65536 ≒ 24 nT。
- 省略すれば丸めない。 `[SEN-MAG-190]`

### 3.3 頭打ち（測れる範囲）

- 各軸の値を ±`fullScaleGauss` × 100,000 nT で切ります（処理の最後）。 `[SEN-MAG-200]`
- **センサの軸ごとに**切ります。 `[SEN-MAG-210]`
- 目安は ±4〜±16 G。地磁気は 1 G より十分小さいので、振り切れるのは、強い磁石が近くにあるときです。
- 頭打ちになったことは上に伝えません。 `[SEN-MAG-220]`
- `range` を省略すれば切らない。`fullScaleGauss` の省略と誤りの扱いは、共通仕様 4.0 のとおり。 `[SEN-MAG-230]`

## 4. 自動操縦への渡し方

| 動かし方 | 渡し方 | 機体の軸に直すところ |
|---|---|---|
| Control Link（PX4） | アダプターが EKF へ渡す | アダプターが `SENS_BOARD_ROT` で戻す `[SEN-MAG-240]` |
| Control Link（ArduPilot） | アダプターが EKF3 へ渡す | アダプターが `AHRS_ORIENTATION` で戻す `[SEN-MAG-240]` |
| PX4 SITL | HIL_SENSOR（ガウスに換算） | PX4 が `SENS_BOARD_ROT` で戻す `[SEN-MAG-250]` |
| ArduPilot SITL | 箱庭からは送らない。ArduPilot SITL が自分で地磁気を作る | ArduPilot が `AHRS_ORIENTATION` で戻す `[SEN-MAG-260]` |
| 箱庭アダプター | — | サポートしない |

ArduPilot SITL では、硬鉄・軟鉄・ノイズ・遅れの設定を ArduPilot SITL のパラメータに置き換えます（5 章の表と 5.2）。 `[SEN-MAG-270]`
`drift`、`resolutionNT`、`range` は ArduPilot SITL に置き換えられないので、反映しません。設定を作る道具が記録に残します（共通仕様 4.0）。 `[SEN-MAG-275]`
地磁気の真値（強さ・偏角・伏角）は置き換えません。ArduPilot SITL は、飛ぶ場所の緯度・経度から自分の世界地磁気モデルで真値を決めます。 `[SEN-MAG-280]`
箱庭の `simulation.location.magneticField` は、ユーザが同じ場所の世界地磁気モデルの値にそろえて書きます。 `[SEN-MAG-290]`
設定を作る道具は、書かれた値を、その場所の世界地磁気モデルの値と比べます。強さが 1%、偏角・伏角が 0.5° を超えて違えば、警告を記録に残します。設定の値は書き換えません。 `[SEN-MAG-295]`
PX4 SITL も偏角を自分の表で決めるので、この比べ方で PX4 SITL との違いも確かめられます。

## 5. PX4・ArduPilot のパラメータとの対応

関係の 4 種類（合わせる・見込み・置き換え・較正）は、ジャイロの仕様 5 章と同じ意味です。

| 箱庭の設定 | 関係 | PX4 | ArduPilot |
|---|---|---|---|
| IMU の姿勢 | 合わせる | `SENS_BOARD_ROT`、`SENS_BOARD_X_OFF`・`Y_OFF`・`Z_OFF`（作り方は共通仕様 5.2） | `AHRS_ORIENTATION`、`CUST_ROT_ENABLE`、`CUST_ROT1_ROLL`・`PITCH`・`YAW`（同） |
| 内蔵であること | 合わせる | `CAL_MAG0_ROT = -1`（内蔵。ボード全体の回転を使う） | `COMPASS_EXTERNAL = 0`、`COMPASS_ORIENT = 0`（Control Link と実機。ArduPilot SITL は 5.3） `[SEN-MAG-300]` |
| 内蔵であること | 置き換え（ArduPilot SITL） | — | `SIM_MAG1_ORIENT = 0`、`COMPASS_ORIENT` = IMU の取り付けの回転の逆（5.3） `[SEN-MAG-310]` |
| `hardIronNT`、`softIron` | 較正 | `CAL_MAG0_XOFF`・`YOFF`・`ZOFF`、`CAL_MAG0_XSCALE`・`YSCALE`・`ZSCALE`、`CAL_MAG0_XODIAG`・`YODIAG`・`ZODIAG`。作り方は 5.1 | `COMPASS_OFS_X`・`Y`・`Z`、`COMPASS_DIA_X`・`Y`・`Z`、`COMPASS_ODI_X`・`Y`・`Z`。作り方は 5.1 |
| `hardIronNT`、`softIron` | 置き換え（ArduPilot SITL） | — | `SIM_MAG1_OFS_X`・`Y`・`Z`、`SIM_MAG1_DIA_X`・`Y`・`Z`、`SIM_MAG1_ODI_X`・`Y`・`Z`。作り方は 5.2 |
| `noise` | 見込み | `EKF2_MAG_NOISE`（G） | `EK3_MAG_M_NSE`（G） |
| `noise` | 置き換え（ArduPilot SITL） | — | `SIM_MAG_RND` = `noise` / 100（mG） `[SEN-MAG-320]` |
| `drift` | 見込み | `EKF2_MAG_B_NOISE`（G/s）（推定器のずれの変化の見込み。単位が違い、`drift` の設定から直接は換算しない） | `EK3_MAGB_P_NSE`（G/s）（同） |
| `delayMsec` | 置き換え（ArduPilot SITL） | — | `SIM_MAG_DELAY` = `delayMsec`（ms） `[SEN-MAG-330]` |
| `simulation.location.magneticField` の偏角 | 見込み | — | `COMPASS_DEC`（rad。`COMPASS_AUTODEC = 0` のときに使う） |
| `range`、`resolutionNT` | — | 対応なし | 対応なし |

- `noise` を軸ごとに書いたときは、`SIM_MAG_RND` に 3 つの σ のうち最も大きいものを使います。違いは、設定を作る道具が記録に残します（共通仕様 4.0）。 `[SEN-MAG-335]`

### 5.1 較正値の作り方

PX4 と ArduPilot は、硬鉄と軟鉄を次の式で取り除きます（センサの軸）。

| | 直し方 | 単位 |
|---|---|---|
| PX4 | m_corrected = S_c · (m − o) | G |
| ArduPilot | m_corrected = S_c · (m + o) | mG |

S_c は対称な 3×3 の行列で、対角が `*SCALE`・`COMPASS_DIA_*`、対角でない成分 [S₀₁, S₀₂, S₁₂] が `*ODIAG`・`COMPASS_ODI_*` です。 `[SEN-MAG-340]`
箱庭の設定から、次の式で較正値を作ります。 `[SEN-MAG-350]`

```text
S_c = S⁻¹
PX4       の o = b / 100,000   （G）
ArduPilot の o = −b / 100      （mG。ArduPilot はオフセットを足すので符号が逆）
```

- この較正値を設定すると、自動操縦が硬鉄と軟鉄を取り除きます。設定しなければ、誤差はそのまま推定に入ります。 `[SEN-MAG-360]`

### 5.2 ArduPilot SITL での置き換え

ArduPilot SITL は、自分で作った地磁気に、`SIM_MAG1_DIA`・`ODI` で作った行列の**逆行列**を掛け、`SIM_MAG1_OFS` を引きます。
箱庭と同じ m' = S · m + b を作るには、次の値にします。 `[SEN-MAG-370]`

```text
SIM_MAG1_DIA・ODI で作る行列 = S⁻¹   （逆行列を掛けるので、S を作るには S⁻¹ を渡す）
SIM_MAG1_OFS = −b / 100               （mG）
```

ArduPilot SITL は、起動したときに `COMPASS_OFS` が 0 なら、`SIM_MAG1_OFS` を `COMPASS_OFS` にそのまま写します。
そのため、何もしないと硬鉄は起動時に自動で較正され、打ち消されます。

- 較正したときの飛行を見るとき：そのままでよい（硬鉄は自動で較正される）。軟鉄の較正は 5.1 の `COMPASS_DIA`・`ODI` を設定する。 `[SEN-MAG-380]`
- 較正しないときの飛行を見るとき：起動する前に `COMPASS_OFS_X` を、0 ではない無視できる小さな値（0.001 mG）にしておく。0 でないので起動時の写しが起きず、硬鉄は較正されないまま残る。 `[SEN-MAG-390]`

### 5.3 ArduPilot SITL での姿勢

ArduPilot SITL は、1 つ目の地磁気センサを外付けとして扱います（`COMPASS_EXTERNAL` を 0 にしても 1 に変わります）。
ArduPilot SITL は、`AHRS_ORIENTATION` があると、自分で作る地磁気を、その回転と逆向きに回った値で出します。
一方、ArduPilot は外付けの地磁気を `AHRS_ORIENTATION` では戻さず、`COMPASS_ORIENT` だけで戻します。
そこで、`SIM_IMU_ORIENT = 0`、`SIM_MAG1_ORIENT = 0` とし、`COMPASS_ORIENT` を IMU の取り付けの回転の逆にします。
逆の回転が番号の表にあればその番号（例：`yaw = 90` なら 6、ヨー 270°）、なければ Custom 2（102）にして、角度を `CUST_ROT2_ROLL`・`PITCH`・`YAW` に書きます（Custom 1 は IMU の取り付けが使う）。
地磁気センサは IMU と同じ取り付けなので、これで内蔵と同じく機体の軸に戻ります。
`COMPASS_ORIENT` を 0 や `AHRS_ORIENTATION` と同じ値にすると、地上で推定の機首の向きが取り付けの角度（またはその 2 倍）だけずれて始まり、離陸したあとで一気に直すときに機体が大きく揺れます。 `[SEN-MAG-310]`

## 6. 受け入れの確かめ方

1. **既定値の互換**：取り付け位置姿勢とこの仕様で足した設定を書かないとき、出力が、それらの段がない場合と一致する（ログが一致）。
2. **真値**：水平で機首を真北に向けた機体で、機体の軸の値が m_ned と一致する（ノイズなし）。
3. **姿勢**：IMU を 90° 回して付け、自動操縦にも同じ姿勢を設定すると、機首の向きの推定が回さないときと同じになる。設定しなければずれる。
   Control Link と SITL、PX4 と ArduPilot の両方で、繰り返して判定する。
4. **較正**：硬鉄・軟鉄を入れ、5.1 の較正値を設定すると、機首の向きの推定が誤差なしのときと同じになる。設定しなければずれる。
   ArduPilot SITL で較正しないときは、5.2 のとおり起動のあとで `COMPASS_OFS` を 0 に設定し直してから判定する。
   PX4・ArduPilot の EKF は、飛行中に地磁気のずれを学習する。そのため「ずれる」は、離陸の直後に判定する。

## 7. サポートしない特性

| 特性 | 意味 | 目安 | 備考 |
|---|---|---|---|
| モーターの電流による乱れ | モーターや電線の電流が作る磁場。スロットルで変わる | 数百〜数千 nT | 電流のモデルが要る。自動操縦の補正は `CAL_MAG0_XCOMP`・`COMPASS_MOT_*` |
| 場所による地磁気の変化 | 飛ぶ場所で地磁気が変わる | 1 km で数 nT | 地磁気は場所の設定で 1 つに決める |
| 地上の鉄による乱れ | 建物・地面の鉄が地磁気をゆがめる | 場所による | — |
| 温度の影響 | 温度でゼロ点と目盛りが変わる | — | — |
| 目盛りの誤差と軸の干渉 | センサそのものの誤差 | ±1% 程度 | 軟鉄の行列で近似できる |
| 帯域とエイリアシング | 内部のサンプリングと、出す周期の違いで起きる折り返し | — | — |
| 外付けの地磁気センサ | GPS と一体のモジュールなど、IMU と別の場所・姿勢に付けるもの。実機のドローンでは、電流の乱れを避けるためによく使う | — | 複数のセンサのどれを使うかと合わせて扱う |
| 複数の地磁気センサ | 2 つ以上を載せる | — | 地磁気センサは 1 つ |

### このモデルで判断してよいこと

このモデルは、自動操縦の推定と制御にセンサの誤差がどう効くかを確かめるためのものです。実物のセンサの値を、細部まで同じに作るものではありません。そこで、このモデルの結果で判断してよいことと、判断してはいけないことを分けておきます。

| 判断してよいこと | 判断してはいけないこと |
|---|---|
| 取り付けの向きと、自動操縦への合わせ方が正しいか | 場所によって変わる地磁気の影響（地磁気は設定した一定の値） |
| 硬鉄・軟鉄の誤差と、その較正が機首の向きの推定に与える影響 | モーターの電流による地磁気の乱れ |
| ノイズ・ドリフト・頭打ちが、機首の向きの推定に与える影響 | 外付けの地磁気センサや、複数の地磁気センサの選び方 |

## 8. 要求の一覧

番号の決まりは、共通仕様 8 章のとおりです。

| 番号 | 要求 | 章 |
|---|---|---|
| SEN-MAG-010 | 出力はセンサの位置の磁場で、センサの軸、単位は nT | 1 |
| SEN-MAG-020 | 地磁気は `simulation.location.magneticField` の 3 つの値で決まり、飛行中は変わらない | 1.1 |
| SEN-MAG-030 | `intensity_nT` は強さ F（nT）、`declination_deg` は偏角 D（真北から東へ、度）、`inclination_deg` は伏角 I（水平から下へ、度） | 1.1 |
| SEN-MAG-035 | `magneticField` の 3 つの値は必須で、1 つでも書かなければエラー | 1.1 |
| SEN-MAG-040 | m_ned = F·(cos I·cos D, cos I·sin D, sin I) | 1.1 |
| SEN-MAG-050 | 機体の軸の値は m_body = R_nbᵀ·m_ned | 1.1 |
| SEN-MAG-060 | 地磁気はセンサの位置では変わらず、取り付けの位置は使わない | 1.1、2 |
| SEN-MAG-070 | 地磁気センサは内蔵とし、IMU の取り付け位置姿勢を使う | 2 |
| SEN-MAG-080 | 姿勢だけを使い、m_sensor = Rᵀ·m_body | 2 |
| SEN-MAG-090 | 処理の順番は、姿勢 → 軟鉄 → 硬鉄 → 遅れ → 測る → ノイズ → ドリフト → 分解能 → 頭打ち | 3 |
| SEN-MAG-100 | ノイズは σ（nT）を 1 つの値か [x, y, z] で書き、0 以下の軸はノイズなし | 3 |
| SEN-MAG-110 | ドリフトは `gauss-markov`（共通仕様 4.2）だけで、σ は `stddevNT`。ほかの `mode` はエラー | 3 |
| SEN-MAG-120 | 硬鉄と軟鉄は m' = S·m + b（姿勢で回したあと、センサの軸）。S は対称な 3×3 の行列 | 3.1 |
| SEN-MAG-130 | `softIron.diagonal` は S の対角。省略すれば [1, 1, 1] | 3.1 |
| SEN-MAG-140 | `softIron.offDiagonal` は [S₀₁, S₀₂, S₁₂] で、S は対称。省略すれば [0, 0, 0] | 3.1 |
| SEN-MAG-150 | `hardIronNT` は b（nT）。省略すれば [0, 0, 0] | 3.1 |
| SEN-MAG-160 | S は逆行列を持つ（行列式が 0 でない） | 3.1 |
| SEN-MAG-165 | 行列式の大きさが 1e-9 より小さい S、有限でない S・b はエラー | 3.1 |
| SEN-MAG-170 | 分解能は `resolutionNT` の最も近い整数倍に丸め、頭打ちの前に当てる | 3.2 |
| SEN-MAG-180 | 分解能の丸めは、中間は 0 から遠い方。刻みは 3 軸共通 | 3.2 |
| SEN-MAG-190 | `resolutionNT` を省略すると丸めない | 3.2 |
| SEN-MAG-200 | 頭打ちは ±`fullScaleGauss` × 100,000 nT で、処理の最後に当てる | 3.3 |
| SEN-MAG-210 | 頭打ちはセンサの軸ごとに当てる | 3.3 |
| SEN-MAG-220 | 頭打ちになったことは上に伝えない | 3.3 |
| SEN-MAG-230 | `range` を省略すると切らない。`fullScaleGauss` は共通仕様 4.0 のとおり | 3.3 |
| SEN-MAG-240 | Control Link では、アダプターがセンサの軸の値を受け取り、`SENS_BOARD_ROT`・`AHRS_ORIENTATION` で機体の軸に直して EKF へ渡す | 4 |
| SEN-MAG-250 | PX4 SITL では、HIL_SENSOR でガウスに換算して渡し、PX4 が `SENS_BOARD_ROT` で戻す | 4 |
| SEN-MAG-260 | ArduPilot SITL へは箱庭から地磁気を送らず、ArduPilot SITL が自分で作る | 4 |
| SEN-MAG-270 | ArduPilot SITL では、硬鉄・軟鉄・ノイズ・遅れを ArduPilot SITL のパラメータに置き換える | 4 |
| SEN-MAG-275 | ArduPilot SITL では、`drift`・`resolutionNT`・`range` を反映せず、設定を作る道具が記録に残す | 4 |
| SEN-MAG-280 | ArduPilot SITL では、地磁気の真値は置き換えず、ArduPilot SITL が緯度・経度から決める | 4 |
| SEN-MAG-290 | `simulation.location.magneticField` は、ユーザが同じ場所の世界地磁気モデルの値にそろえて書く | 4 |
| SEN-MAG-295 | 設定を作る道具は、`magneticField` を世界地磁気モデルと比べ、強さ 1%・偏角と伏角 0.5° を超えて違えば警告を記録に残す。値は書き換えない | 4 |
| SEN-MAG-300 | 内蔵として、PX4 は `CAL_MAG0_ROT = -1`、ArduPilot（Control Link と実機）は `COMPASS_EXTERNAL = 0`・`COMPASS_ORIENT = 0` | 5 |
| SEN-MAG-310 | ArduPilot SITL では `SIM_IMU_ORIENT = 0`・`SIM_MAG1_ORIENT = 0`・`COMPASS_ORIENT` = IMU の取り付けの回転の逆（表になければ Custom 2） | 5、5.3 |
| SEN-MAG-320 | ArduPilot SITL では `SIM_MAG_RND` = `noise` / 100（mG） | 5 |
| SEN-MAG-330 | ArduPilot SITL では `SIM_MAG_DELAY` = `delayMsec`（ms） | 5 |
| SEN-MAG-335 | `noise` を軸ごとに書いたときは、`SIM_MAG_RND` に 3 つの σ の最大を使い、違いを記録に残す | 5 |
| SEN-MAG-340 | 較正の行列 S_c の対角は `*SCALE`・`COMPASS_DIA_*`、対角でない成分 [S₀₁, S₀₂, S₁₂] は `*ODIAG`・`COMPASS_ODI_*` | 5.1 |
| SEN-MAG-350 | 較正値は S_c = S⁻¹、PX4 の o = b / 100,000（G）、ArduPilot の o = −b / 100（mG） | 5.1 |
| SEN-MAG-360 | 較正値を設定すれば硬鉄と軟鉄が取り除かれ、設定しなければ誤差が推定に入る | 5.1 |
| SEN-MAG-370 | ArduPilot SITL では、`SIM_MAG1_DIA`・`ODI` の行列 = S⁻¹、`SIM_MAG1_OFS` = −b / 100（mG） | 5.2 |
| SEN-MAG-380 | ArduPilot SITL で較正したときは、硬鉄は起動時の自動の較正に任せ、軟鉄は 5.1 の `COMPASS_DIA`・`ODI` を設定する | 5.2 |
| SEN-MAG-390 | ArduPilot SITL で較正しないときは、起動する前に `COMPASS_OFS_X` を 0.001 mG にして、起動時の写しを止める | 5.2 |
