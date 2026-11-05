# GPS の仕様

GPS（GNSS 受信機）に固有のことを書きます。全センサに共通の決まり（座標、取り付け位置姿勢、処理の順番、自動操縦との合わせ方）は
[センサの共通仕様](../README.md) にあります。

## 1. 何を測るか

**アンテナ**の位置と速度を測り、受信機が申告する精度と一緒に出します。

| 出力 | 単位 | 意味 |
|---|---|---|
| 緯度・経度 | 度 | WGS-84 `[SEN-GPS-010]` |
| 高度 | m | 海抜 `[SEN-GPS-020]` |
| 速度 | m/s | 北・東・下（NED）の 3 成分 `[SEN-GPS-030]` |
| 対地速度 | m/s | 水平の速さ `[SEN-GPS-040]` |
| 進行方向（COG） | 度 | 水平の速度の向き。真北から時計回りに 0 以上 360 未満（360 は 0 として出す）。水平の速さが 0.1 m/s 未満のときは、向きが定まらないので「無効」 `[SEN-GPS-050]` |
| 水平・垂直の位置の精度 | m | 受信機が申告する精度（4.2）。実際の誤差ではない `[SEN-GPS-060]` |
| 速度の精度 | m/s | 同上 `[SEN-GPS-070]` |
| 衛星の数 | 個 | 設定した値 `[SEN-GPS-080]` |
| 測位の種類 | — | 3D 測位で固定 `[SEN-GPS-090]`。このモデルは、測位がいつも続いている状態での数値の誤差を作るもので、衛星の数を 0 にしても 3D 測位として出します（衛星の数は申告の値だけ） |

- 無効になるのは進行方向だけです。位置の精度・対地速度・衛星の数などほかの出力は、いつも有効な値を出します。 `[SEN-GPS-095]`

## 2. 真値

### 2.1 アンテナの位置と速度

GPS は**アンテナの位置**を測ります。アンテナの位置と速度は、共通仕様 2.4 の剛体の式で、機体の原点の動きから求めます。 `[SEN-GPS-100]`

```text
p_ant = p + R_nb · r
v_ant = v + R_nb · (ω × r)
```

r はアンテナの取り付け位置（`components.sensors.gps.mount.positionM`）です。機体が回ると、アンテナが原点のまわりを回る分だけ速度が変わります。

### 2.2 緯度・経度・高度への換算

シミュレーションの原点（`simulation.location` の `latitude`・`longitude`・`altitude`）を基準に、
世界（NED）の位置 (x, y, z) を、原点での WGS-84 の曲率半径で換算します。 `[SEN-GPS-110]`

```text
a  = 6,378,137 m、 f = 1 / 298.257223563、 e² = f · (2 − f)
φ₀ = 原点の緯度、 h₀ = 原点の高度
M  = a · (1 − e²) / (1 − e² · sin²φ₀)^(3/2)       （子午線の曲率半径）
N  = a / (1 − e² · sin²φ₀)^(1/2)                   （東西の曲率半径）

緯度 = φ₀ + x / (M + h₀)          （ラジアン）
経度 = λ₀ + y / ((N + h₀) · cos φ₀)
高度 = h₀ − z
```

- 原点のまわりを平らとみなす近似です。換算の誤差は、原点の緯度と進む向きで変わります。例：原点から 3 km 斜めに進んだとき、東京付近（35.7°）で約 0.6 m、緯度 60° で約 1.4 m です。
- 高度は海抜と呼びますが、ジオイドと楕円体の差は扱いません。曲率半径の計算でも、海抜の値を楕円体からの高さの代わりに使います（9 章）。 `[SEN-GPS-120]`

## 3. 取り付け位置姿勢

`components.sensors.gps.mount` に書きます（共通仕様 2.2）。

- **位置を使います。** アンテナの位置と速度を測ります（2.1）。 `[SEN-GPS-130]`
- **姿勢は使いません。** 位置と速度は、アンテナの向きによらないためです。 `[SEN-GPS-140]`

例：アンテナを原点から上に 20 cm（`positionM = [0, 0, -0.2]`）に付けて、機体が 90° 横に傾くと、アンテナの位置は水平に 20 cm 動きます。

## 4. 処理の順番

GPS の値は、次の順番で作ります。 `[SEN-GPS-150]`

```text
p_ant・v_ant（NED） → 遅れ → 測る → ノイズ → ドリフト → 緯度・経度・高度へ換算 → 出力
                                                     （対地速度・進行方向は、ノイズを足したあとの速度から計算）
```

| 段 | 設定（`components.sensors.gps.*`） | 内容 |
|---|---|---|
| 位置 | GPS の取り付け位置姿勢 | アンテナの位置と速度（2.1） |
| 遅れ | `delayMsec` | ハードの遅れ。受信機が位置を解くまでの遅れ（共通仕様 4 章）。目安 100〜200 ms |
| 測る周期 | `updatePeriodMsec` | 新しい値を測る周期（共通仕様 4 章）。`sampleCount`（平均）は 1 だけ書ける（共通仕様 6 章） |
| ノイズ | `positionNoise`、`velocityNoise` | 下の 4.1 |
| ドリフト | `drift` | 位置のゆっくりした変化。下の 4.1 |
| 換算 | — | 2.2 の式 |

- 誤差はすべて、世界（NED）の m・m/s で足してから、緯度・経度に換算します。 `[SEN-GPS-155]`
- 対地速度と進行方向は、ノイズを足したあとの速度から計算します。速度・対地速度・進行方向は、いつも互いに食い違いません。 `[SEN-GPS-160]`
- 値を出す周期（`updatePeriodMsec`）は、受信機が新しい位置を出す周期です（共通仕様 4 章）。目安 100〜200 ms（5〜10 Hz）。間は前の値を出し続けます。 `[SEN-GPS-170]`
- GPS をこの仕様の項目（`mount`、`positionNoise`、`velocityNoise`、`drift`、`accuracy`、`satellitesVisible`、`softDelayMsec`）で書くときは、`updatePeriodMsec` を必ず書きます。書かなければ読み込みをエラーにします。
  周期を書かないと物理の刻みごとに新しい値とノイズが出て、本物の受信機（5〜10 Hz）と条件が変わるうえ、その条件が設定から読み取れないためです。
  これらの項目を書かない既存の設定は、これまでどおり読めます（共通仕様 4.4）。 `[SEN-GPS-175]`

### 4.1 ノイズとドリフト

```json
"positionNoise": { "horizontalM": 0.5, "verticalM": 1.0 },
"velocityNoise": { "horizontalMps": 0.1, "verticalMps": 0.2 },
"drift": { "mode": "gauss-markov", "horizontalM": 1.0, "verticalM": 2.0, "correlationTimeSec": 120 }
```

| 設定 | 意味 |
|---|---|
| `positionNoise.horizontalM` | 北・東の位置に、それぞれ別々に足す正規分布の標準偏差（m） `[SEN-GPS-180]` |
| `positionNoise.verticalM` | 下の位置に足す標準偏差（m） `[SEN-GPS-180]` |
| `velocityNoise.horizontalMps` | 北・東の速度に、それぞれ別々に足す標準偏差（m/s） `[SEN-GPS-190]` |
| `velocityNoise.verticalMps` | 下の速度に足す標準偏差（m/s） `[SEN-GPS-190]` |
| `drift`（`gauss-markov`） | 位置のゆっくりした変化（共通仕様 4.2）。σ は水平（北・東それぞれ）と垂直で別々。`correlationTimeSec` は共通 `[SEN-GPS-200]` |

- ノイズは、省略するか σ が 0 以下なら、その成分のノイズなし。ドリフトは、省略するか σ が 0 なら、その成分のドリフトなし。ドリフトの σ が負、または `correlationTimeSec` が 0 以下なら、設定の誤り（エラー）。 `[SEN-GPS-210]`
- そのほかの省略と誤りの扱いは、共通仕様 4.0 のとおりです。
- 実機の GPS の位置の誤差は、毎回ばらばらのノイズより、数十秒〜数分かけてゆっくり動く誤差（マルチパス、電離層など）が大きい。ドリフトで表します。
- 目安（一例、どれも定常の 1σ）：単独測位で、ドリフトの水平 σ 1〜3 m・垂直 σ 2〜5 m、ノイズの水平 σ 0.1〜0.5 m、速度のノイズ 0.05〜0.2 m/s。
  実際の誤差は受信機と空の見え方で大きく変わるので、使う受信機の記録から合わせます。

### 4.2 精度の申告

受信機が「この位置はこれくらい正しい」と申告する値です。実際の誤差（4.1）とは別に設定します。GPS の劣化を表すときは、両方を設定します。

```json
"accuracy": { "horizontalM": 1.5, "verticalM": 3.0, "speedMps": 0.3 },
"satellitesVisible": 12
```

| 設定 | 意味 |
|---|---|
| `accuracy.horizontalM`・`verticalM` | 申告する水平・垂直の位置の精度（m）。省略したときは 0.5 m・0.75 m `[SEN-GPS-220]` |
| `accuracy.speedMps` | 申告する速度の精度（m/s）。省略したときは 0.5 m/s `[SEN-GPS-230]` |
| `satellitesVisible` | 申告する衛星の数（0〜254）。省略したときは 10。範囲の外は設定の誤り（エラー） `[SEN-GPS-240]` |

自動操縦は、この申告を見て GPS を使うかどうかを決めます（PX4 の `EKF2_REQ_EPH` など）。実際の誤差に見合う値にすると、推定が実際に合います。

## 5. 自動操縦への渡し方

| 動かし方 | 渡し方 |
|---|---|
| Control Link（PX4） | アダプターが EKF へ渡す（位置は m、速度は m/s、位置の精度は m、速度の精度は m/s） `[SEN-GPS-250]` |
| Control Link（ArduPilot） | アダプターが EKF3 へ渡す（PX4 と同じ。位置は m、速度は m/s、位置の精度は m、速度の精度は m/s） `[SEN-GPS-250]`。値は、ArduPilot SITL の u-blox 受信機の単位（緯度・経度は 1e-7 度、高度は mm、速度は mm/s、精度は mm）で 0 の方へ切り捨て、ArduPilot の受信機の処理と同じく高度は cm にしたもの。速度の精度も mm/s で渡す（ArduPilot SITL はこの欄に cm/s の値を書くため 1/10 の値が届くが、これは ArduPilot SITL の不具合なので再現しない。版は共通仕様 5.4） `[SEN-GPS-380]` |
| PX4 SITL | HIL_GPS。緯度・経度は 1e7 倍の整数、高度は mm、速度は cm/s、位置の精度は cm、進行方向は 0.01 度。整数にするときは 0 の方へ切り捨てる（丸めない。PX4 SITL との照合はこの切り捨てを前提にする）。進行方向が無効のときは 65535（位置の精度・対地速度・衛星の数は無効にしないので、65535・255 は出さない）。**速度の精度は HIL_GPS に欄がないので、PX4 SITL には渡らない** `[SEN-GPS-260]` |
| ArduPilot SITL | 箱庭からは送らない。ArduPilot SITL が自分で GPS を作る（6 章の置き換え）。ArduPilot SITL がそのもとにする機体の位置と速度には、機体の原点の真の値を送る（アンテナの位置・ノイズ・遅れを入れない。入れると、ArduPilot SITL が足す分と二重になる） `[SEN-GPS-270]` |
| 箱庭アダプター | 1 章と同じ出力（緯度・経度・高度と NED の速度）を使う。取り付け位置姿勢は使わない `[SEN-GPS-280]` |

## 6. PX4・ArduPilot のパラメータとの対応

関係の 4 種類（合わせる・見込み・置き換え・較正）は、ジャイロの仕様 5 章と同じ意味です。

| 箱庭の設定 | 関係 | PX4 | ArduPilot |
|---|---|---|---|
| アンテナの位置 | 合わせる（重心から見た値に直して渡す。共通仕様 5.1） | `SENS_GPS0_OFFX`・`OFFY`・`OFFZ` | `GPS1_POS_X`・`Y`・`Z` |
| アンテナの位置 | 置き換え（ArduPilot SITL） | — | `SIM_GPS_POS_X`・`Y`・`Z`（機体の原点からの位置、FRD。`positionM` をそのまま） `[SEN-GPS-290]` |
| `delayMsec` | 見込み | `SENS_GPS0_DELAY`（ms）= `delayMsec`（測定を遅らせる値ではなく、遅れを EKF に知らせる値。気圧の仕様 6 章と同じ。設定を作る道具は、気圧の `EKF2_BARO_DELAY` と同じく推奨として表示する） | `GPS1_DELAY_MS`（ms）= `delayMsec` `[SEN-GPS-300]`。ArduPilot では `GPS1_DELAY_MS` = 0 は「受信機の既定の遅れを使う」の意味。Control Link も同じく、0 のときは自動操縦の設定 `runtime.gps_receiver_default_lag_ms`（必須）を使う。ArduPilot SITL の u-blox は世代を名乗らないので、ArduPilot は 220 ms を使う。設定はこの値にそろえる `[SEN-GPS-385]` |
| `delayMsec` | 置き換え（ArduPilot SITL） | — | `SIM_GPS_LAG_MS`（ms）= `delayMsec` `[SEN-GPS-310]` |
| `positionNoise` | 見込み | `EKF2_GPS_P_NOISE`（m） | `EK3_POSNE_M_NSE`（m） |
| `velocityNoise` | 見込み | `EKF2_GPS_V_NOISE`（m/s） | `EK3_VELNE_M_NSE`（水平）・`EK3_VELD_M_NSE`（垂直）（m/s） |
| `velocityNoise` | 置き換え（ArduPilot SITL） | — | `SIM_GPS_VERR_X`・`Y`・`Z`（m/s）= 北・東・下の σ × √3（一様分布 ±値 なので、標準偏差をそろえる）。ArduPilot SITL は、速度の精度の申告もこの値から決める（水平の 2 つの長さ）ので、`accuracy.speedMps` を別に置き換えられない `[SEN-GPS-320]` |
| `positionNoise`、`drift` | 対応なし（ArduPilot SITL） | — | ArduPilot SITL には、水平の位置に乱数の誤差を足す設定がない。`SIM_GPS_NOISE` と `SIM_GPS_DRIFTALT` は高度だけをゆっくり正弦波で動かすもので、別物。使わない（0） `[SEN-GPS-330]` |
| `accuracy` | 置き換え（ArduPilot SITL） | — | `SIM_GPS_ACC`（m）= `accuracy.horizontalM`。ArduPilot SITL は水平・垂直の申告に同じ値を使うので、`verticalM` は別に置き換えられない（違いは記録に残す。共通仕様 4.0） `[SEN-GPS-340]` |
| `satellitesVisible` | 置き換え（ArduPilot SITL） | — | `SIM_GPS_NUMSATS` `[SEN-GPS-350]` |
| `updatePeriodMsec` | 置き換え（ArduPilot SITL） | — | `SIM_GPS_HZ` = 1000 / `updatePeriodMsec`（最も近い整数） `[SEN-GPS-360]` |

- ArduPilot SITL では、位置のノイズとドリフトを再現できません。GPS の位置の誤差を見る実験は、Control Link か PX4 SITL で行います。 `[SEN-GPS-370]`

## 7. SDFormat との対応

| 箱庭 | SDFormat（`<navsat>`） | 関係 |
|---|---|---|
| `positionNoise.horizontalM`・`verticalM` | `position_sensing/horizontal/noise`・`vertical/noise` | 名前と意味（m）は同じ。ただし gz-sensors（8・10）は水平のノイズを緯度・経度の**度**に足していて、仕様の m と食い違う。箱庭は m で足す |
| `velocityNoise.horizontalMps`・`verticalMps` | `velocity_sensing/horizontal/noise`・`vertical/noise` | 同じ（m/s） |
| `drift`（`gauss-markov`） | `noise` の `dynamic_bias_*` | 考え方だけ対応（共通仕様 7 章） |
| アンテナの位置 | `<sensor><pose>` | 同じ考え方。箱庭はアンテナの速度にも回転の分を入れる |
| 精度の申告・衛星の数 | なし | SDFormat の標準の要素にはない |
| 遅れ | なし | 同上 |

## 8. 受け入れの確かめ方

1. **既定値の互換**：取り付け位置姿勢とこの仕様で足した設定を書かないとき、出力が、それらの段がない場合と一致する（ログが一致）。
2. **換算**：原点から北へ 1,000 m、東へ 1,000 m の位置の緯度・経度が、2.2 の式と一致する（いくつかの原点の緯度で）。
3. **アンテナの位置**：アンテナを上に 20 cm 付けて機体を 90° 傾けると、位置が水平に 20 cm 動く。機体が回ると、速度が ω × r だけ変わる。
4. **ノイズの単位**：`positionNoise.horizontalM` = 1 のとき、北・東の位置の誤差の標準偏差がそれぞれ 1 m（緯度・経度を m に戻して測る）。
5. **進行方向**：止まっているとき（水平の速さ 0.1 m/s 未満）は無効、東へ進むと 90 度。
6. **飛行**：ノイズ・ドリフト・遅れを入れ、自動操縦の見込みと精度の申告（6 章、4.2。PX4 SITL では位置の精度まで）を合わせると、位置の推定が安定する。Control Link と PX4 SITL で、繰り返して判定する。

## 9. サポートしない特性

| 特性 | 意味 | 備考 |
|---|---|---|
| 衛星の配置と遮へい | ビルや地形で衛星が見えなくなる。精度が場所で変わる | 衛星の軌道と 3D の街のモデルが要る |
| マルチパスの細かい再現 | 反射した電波で位置がずれる | ドリフトでおおまかに表す |
| 測位の種類の変化 | 2D 測位、RTK、測位を失う、など | 測位は 3D で固定 |
| 測位までの時間 | 電源を入れてから測位できるまでの時間 | 始めから測位している |
| ジオイド | 楕円体の高さと海抜の差 | 高度は海抜として扱う |
| 原点から遠い場所の換算 | 原点から数 km 以上離れたときの、地球の丸みによる換算の誤差 | 2.2 は原点のまわりの近似 |
| GPS による機首の向き（2 アンテナ） | 2 つのアンテナで向きを測る | — |
| 妨害・なりすまし | ジャミング、スプーフィング | — |
| 複数の GPS | 2 つ以上を載せる | GPS は 1 つ |

### このモデルで判断してよいこと

このモデルは、自動操縦の推定と制御にセンサの誤差がどう効くかを確かめるためのものです。実物のセンサの値を、細部まで同じに作るものではありません。そこで、このモデルの結果で判断してよいことと、判断してはいけないことを分けておきます。

| 判断してよいこと | 判断してはいけないこと |
|---|---|
| アンテナの位置と、自動操縦への合わせ方が正しいか | 測位を失う・2D 測位になる・精度が落ちる場面の振る舞い（測位はいつも 3D 測位として扱う） |
| 位置・速度のノイズ、遅れ、ドリフトが、位置の推定と制御に与える影響（測位が続いている状態で） | 建物や地形による遮へい・反射（マルチパス）、衛星の配置の影響 |
| 申告した精度に、自動操縦がどう応じるか | 時間とともに変わる申告精度（申告精度は設定した一定の値） |

## 10. 要求の一覧

番号の決まりは、共通仕様 8 章のとおりです。

| 番号 | 要求 | 章 |
|---|---|---|
| SEN-GPS-010 | 緯度・経度は WGS-84 の度で出す | 1 |
| SEN-GPS-020 | 高度は海抜の m で出す | 1 |
| SEN-GPS-030 | 速度は北・東・下（NED）の 3 成分の m/s で出す | 1 |
| SEN-GPS-040 | 対地速度は水平の速さ（m/s） | 1 |
| SEN-GPS-050 | 進行方向は水平の速度の向きで、真北から時計回りに 0 以上 360 未満の度（360 は 0）。水平の速さが 0.1 m/s 未満のときは無効 | 1 |
| SEN-GPS-060 | 水平・垂直の位置の精度（m）は受信機が申告する値で、実際の誤差ではない | 1 |
| SEN-GPS-070 | 速度の精度（m/s）は受信機が申告する値で、実際の誤差ではない | 1 |
| SEN-GPS-080 | 衛星の数は設定した値を出す | 1 |
| SEN-GPS-090 | 測位の種類は 3D 測位で固定 | 1 |
| SEN-GPS-095 | 無効になるのは進行方向だけ。ほかの出力はいつも有効な値 | 1 |
| SEN-GPS-100 | アンテナの位置と速度は、共通仕様 2.4 の剛体の式で機体の原点の動きから求める（p + R_nb·r、v + R_nb·(ω × r)） | 2.1 |
| SEN-GPS-110 | 緯度・経度・高度は、`simulation.location` を原点に、原点での WGS-84 の曲率半径で 2.2 の式のとおり換算する | 2.2 |
| SEN-GPS-120 | ジオイドは扱わず、曲率半径の計算でも海抜を楕円体からの高さの代わりに使う | 2.2 |
| SEN-GPS-130 | 取り付けの位置を使う | 3 |
| SEN-GPS-140 | 取り付けの姿勢は使わない | 3 |
| SEN-GPS-150 | 処理の順番は、アンテナの位置・速度 → 遅れ → 測る → ノイズ → ドリフト → 換算 | 4 |
| SEN-GPS-155 | 誤差はすべて NED の m・m/s で足してから、緯度・経度に換算する | 4 |
| SEN-GPS-160 | 対地速度と進行方向は、ノイズを足したあとの速度から計算し、速度と食い違わない | 4 |
| SEN-GPS-170 | `updatePeriodMsec` ごとに新しい値を出し、間は前の値を出し続ける | 4 |
| SEN-GPS-175 | この仕様の GPS の項目を書くときは `updatePeriodMsec` が必須（なければエラー）。書かない既存の設定はそのまま読める | 4 |
| SEN-GPS-180 | 位置のノイズは、北・東にそれぞれ別々に水平の σ、下に垂直の σ（m）の正規分布を足す | 4.1 |
| SEN-GPS-190 | 速度のノイズは、北・東にそれぞれ別々に水平の σ、下に垂直の σ（m/s）の正規分布を足す | 4.1 |
| SEN-GPS-200 | ドリフト `gauss-markov` は共通仕様 4.2 で、σ は水平（北・東それぞれ）と垂直で別々、`correlationTimeSec` は共通 | 4.1 |
| SEN-GPS-210 | ノイズは省略か σ ≤ 0 でその成分のノイズなし。ドリフトは省略か σ = 0 でその成分のドリフトなし、σ が負か `correlationTimeSec` ≤ 0 はエラー | 4.1 |
| SEN-GPS-220 | `accuracy.horizontalM`・`verticalM` は申告する位置の精度。省略したときは 0.5 m・0.75 m | 4.2 |
| SEN-GPS-230 | `accuracy.speedMps` は申告する速度の精度。省略したときは 0.5 m/s | 4.2 |
| SEN-GPS-240 | `satellitesVisible` は 0〜254。省略したときは 10。範囲の外はエラー | 4.2 |
| SEN-GPS-250 | Control Link では、アダプターが EKF（PX4）・EKF3（ArduPilot）へ、位置は m、速度は m/s、位置の精度は m、速度の精度は m/s で渡す | 5 |
| SEN-GPS-260 | PX4 SITL へは HIL_GPS で、5 章の単位で渡す。進行方向の無効は 65535。速度の精度は渡らない | 5 |
| SEN-GPS-270 | ArduPilot SITL へは箱庭から GPS を送らない。機体の位置・速度としては、機体の原点の真の値を送る | 5 |
| SEN-GPS-280 | 箱庭アダプターは 1 章と同じ出力（緯度・経度・高度と NED の速度）を使い、取り付け位置姿勢は使わない | 5 |
| SEN-GPS-290 | ArduPilot SITL では `SIM_GPS_POS_X`・`Y`・`Z` = `positionM`（機体の原点から、FRD） | 6 |
| SEN-GPS-300 | `SENS_GPS0_DELAY`・`GPS1_DELAY_MS` = `delayMsec`（ms） | 6 |
| SEN-GPS-310 | ArduPilot SITL では `SIM_GPS_LAG_MS` = `delayMsec`（ms） | 6 |
| SEN-GPS-320 | ArduPilot SITL では `SIM_GPS_VERR_X`・`Y`・`Z` = 北・東・下の速度のノイズの σ × √3 | 6 |
| SEN-GPS-330 | ArduPilot SITL では `SIM_GPS_NOISE` = 0、`SIM_GPS_DRIFTALT` = 0 | 6 |
| SEN-GPS-340 | ArduPilot SITL では `SIM_GPS_ACC` = `accuracy.horizontalM`（m）。`verticalM` は置き換えられない | 6 |
| SEN-GPS-350 | ArduPilot SITL では `satellitesVisible` を `SIM_GPS_NUMSATS` に置き換える | 6 |
| SEN-GPS-360 | ArduPilot SITL では `SIM_GPS_HZ` = 1000 / `updatePeriodMsec` の最も近い整数 | 6 |
| SEN-GPS-370 | ArduPilot SITL では位置のノイズとドリフトを再現しない。GPS の位置の誤差を見る実験は Control Link か PX4 SITL で行う | 6 |
| SEN-GPS-380 | Control Link（ArduPilot）では、GPS の値を ArduPilot SITL の u-blox 受信機の単位で 0 の方へ切り捨て、ArduPilot の受信機の処理と同じ形で EKF3 へ渡す。速度の精度は正しい単位（mm/s）で渡し、ArduPilot SITL の 1/10 になる不具合は再現しない | 5 |
| SEN-GPS-385 | Control Link（ArduPilot）では、`GPS1_DELAY_MS` = 0 のとき、ArduPilot と同じく受信機の既定の遅れ（`runtime.gps_receiver_default_lag_ms`、必須）を使う | 6 |
