[English](README.md) | 日本語

# MuJoCo / Hakoniwa / PX4 座標系統合メモ

## 目的

このドキュメントは、MuJoCo モデル、箱庭ドローン内部設定、PX4 ローター設定の間で、
座標系とローター配置をどのように対応付けるかを整理するための内部技術メモである。

特に、以下のような混乱を防ぐことを目的とする。

- `drone.xml` のローター位置と `drone_config_0.json` の `rotorPositions` の対応
- NED / FRD / FLU 系の座標系の混同
- PX4 `CA_ROTOR` 系パラメータとの対応
- 機体モデル切替時の符号ミス、並び順ミス

---

## 関係する座標系

この文書では、まず以下を前提として扱う。

- **PX4 側**
  - 地上座標系: **NED**
  - 機体座標系: **FRD**
- **箱庭ドローン内部**
  - 地上座標系: **NED**
  - 機体座標系: **FRD**
- **MuJoCo 側**
  - この実装では **FLU (Forward-Left-Up)** として扱う
  - `drone.xml` の `body pos` は MuJoCo/FLU のモデルローカル座標
  - これを箱庭/PX4 のローター設定へ写像して使う

重要なのは、MuJoCo の `drone.xml` 上の位置を、そのまま PX4/箱庭のローター設定値と同一視しないことである。
本ドキュメントでは、`mujoco-px4-1` の実績構成を基準に、MuJoCo ローカル配置から箱庭/PX4 のローター配置へ写像する規則を整理する。

### 1. Ground Coordinate System (NED)

箱庭ドローンシミュレータの位置・速度の基本座標系は NED を前提とする。

- X: North
- Y: East
- Z: Down

関連ドキュメント:
- [fundamental/README.md](/docs/fundamental/README.md)

### 2. Body Coordinate System (FRD)

機体固定座標系は FRD を前提とする。

- X: Forward
- Y: Right
- Z: Down

関連ドキュメント:
- [fundamental/README.md](/docs/fundamental/README.md)

### 3. FLU 系座標

外部ツールや既存資料では FLU

- X: Forward
- Y: Left
- Z: Up

を前提とする場合がある。

PX4 の実運用側は本リポジトリでは NED/FRD を前提とする。
一方で、MuJoCo モデルや外部資料では FLU 的な説明が使われることがあるため、
FRD/NED と直接混同しないよう注意が必要である。

### 4. MuJoCo モデル座標

`src/aircraft/impl/body/drone_dynamics_mujoco.hpp` では、MuJoCo 側の座標系を **FLU** として明示的に扱っている。

- `ned_to_mujoco()`
- `mujoco_to_ned()`

の変換関数があり、

- NED → MuJoCo(FLU)
- MuJoCo(FLU) → NED

の対応をコード上で持っている。

したがって、`drone.xml` に定義される `body pos` は、本実装上は **MuJoCo/FLU のモデルローカル配置** とみなしてよい。
ただし、ここで定義された値を、そのまま `rotorPositions` にコピペしてよいとは限らない。

### MuJoCo でのトルク/推力の適用

MuJoCo 実装では `drone_dynamics_mujoco` 内で、`rotor_thrust` / `rotor_anti_torque` による力を body frame へ変換して MuJoCo に適用する。

- `prop_thrust[i]` は body -Z 方向（NED/FRD）で計算され、MuJoCo へ `Fflu` として与えられる。
- roll/pitch トルクは `position × thrust_vector` で計算されるため、`rotorPositions.z` が共通であれば結果に差は出ない。
- yaw 反トルクは `rotationDirection` が `ccw` 符号として引き継がれ、`rotor_anti_torque` で合算される。

したがって、MuJoCo 側でも `rotorPositions` / `rotationDirection` の意味は BodyFrame 実装と一致し、torque/thrust 式は同じである。

---

## 座標系の対応関係

この節では、どの設定・実装がどの座標系を前提にしているかを整理する。

| 対象 | 主な役割 | 前提座標系 | 備考 |
|------|----------|------------|------|
| 箱庭の位置/速度 | 機体状態の外部表現 | NED | 基本の地上座標系 |
| 箱庭の機体固定軸 | 姿勢・機体運動 | FRD | 制御・機体系で利用 |
| MuJoCo `drone.xml` | モデル配置 | MuJoCo FLU local | 直接 `rotorPositions` と一致しない場合がある |
| `drone_config_0.json` `rotorPositions` | ロータ力学入力 | 箱庭/PX4 側の機体配置表現 | 本文書の主対象 |
| PX4 `CA_ROTOR` | ミキサ/配置パラメータ | PX4 body frame (FRD 前提) | ローター番号・符号対応を明示する |

---

## 関係する設定ファイル

### 箱庭ドローン内部設定

- `config/drone/<model>/drone_config_0.json`

主に確認する項目:

- `thruster.rotorPositions`
- `rotationDirection`

注意:

- `rotorPositions` は **地上座標系 NED ではなく、機体座標系 FRD でのローター位置** として扱う
- したがって、`x=Forward`, `y=Right`, `z=Down` の向きで読む
- MuJoCo `drone.xml` の FLU 配置値を使う場合は、FRD への写像を意識する必要がある

### MuJoCo モデル

- `config/drone/<model>/drone.xml`

主に確認する項目:

- `prop*` / `rotor*` 相当 body の `pos`

### PX4 側設定

対象:

- `CA_ROTOR*` 系パラメータ

ここでは、PX4 側のローター番号と、
箱庭側 `rotorPositions` / `rotationDirection` の対応を整理する。

### PX4 `CA_ROTOR` の意味

PX4 の control allocation 実装では、マルチコプタ用ローターの有効性を
body frame 上の位置・推力軸・係数から構成する。

参照:

- `work/PX4-Autopilot/src/modules/control_allocator/VehicleActuatorEffectiveness/ActuatorEffectivenessRotors.cpp`
- `work/PX4-Autopilot/src/modules/control_allocator/module.yaml`

PX4 側の主要パラメータは以下である。

- `CA_ROTOR{i}_PX`, `CA_ROTOR{i}_PY`, `CA_ROTOR{i}_PZ`
  - 重心基準の body frame 上のローター位置
- `CA_ROTOR{i}_CT`
  - 推力係数
- `CA_ROTOR{i}_KM`
  - モーメント係数
  - PX4 の定義は `Torque = KM * Thrust`
  - PX4 は明示的に
    - `KM > 0`: CCW
    - `KM < 0`: CW
    としている

マルチコプタ標準設定では、PX4 はローター推力軸を `axis = (0, 0, -1)` として扱う。
これは FRD body frame において「上向き推力」を意味する。

PX4 実装上の基本式は以下である。

```text
thrust = CT * axis
moment = CT * position × axis - CT * KM * axis
```

ここで、

- `position × axis`
  - ローター位置による roll/pitch モーメント
- `-CT * KM * axis`
  - プロペラ回転による yaw モーメント

を表す。

したがって、箱庭側との対応は次のように読める。

| 概念 | 箱庭 | PX4 |
|------|------|-----|
| ローター位置 | `thruster.rotorPositions` (FRD) | `CA_ROTOR*_PX/PY/PZ` |
| 推力方向 | body -Z 方向 | `axis = (0,0,-1)` |
| 回転方向 | `rotationDirection` | `CA_ROTOR*_KM` の符号 |
| 上から見た CCW | `rotationDirection = +1` | `KM > 0` |
| 上から見た CW | `rotationDirection = -1` | `KM < 0` |

実務上は、quad-X のような通常配置であれば以下の対応として整理してよい。

- 箱庭 `rotationDirection = +1`
  - PX4 `CA_ROTOR*_KM > 0`
  - 機体を上から見て CCW
- 箱庭 `rotationDirection = -1`
  - PX4 `CA_ROTOR*_KM < 0`
  - 機体を上から見て CW

### PX4 `none_iris` の具体例

本リポジトリで日常的に参照する PX4 SITL 構成は `SYS_AUTOSTART=10016` であり、
対応する airframe は以下である。

- `work/PX4-Autopilot/ROMFS/px4fmu_common/init.d-posix/airframes/10016_none_iris`

この構成における `CA_ROTOR` の主要設定は以下である。

| Rotor | PX4 position `(PX, PY)` | PX4 `KM` | 上から見た回転 |
|------|--------------------------|----------|----------------|
| 0 | `( 0.1515,  0.2450 )` | `+0.05` | CCW |
| 1 | `(-0.1515, -0.1875 )` | `+0.05` | CCW |
| 2 | `( 0.1515, -0.2450 )` | `-0.05` | CW |
| 3 | `(-0.1515,  0.1875 )` | `-0.05` | CW |

したがって、`none_iris` を箱庭側設定へ対応付けるときの回転方向規則は次のように読める。

- Rotor 0, 1
  - `KM > 0`
  - 箱庭 `rotationDirection = +1`
- Rotor 2, 3
  - `KM < 0`
  - 箱庭 `rotationDirection = -1`

位置ベクトルそのものは、PX4 と箱庭のどちらも FRD/body frame 前提で読んでよい。

---

## 実例

### 1. `mujoco-px4-1`

この構成は既存実績があるため、座標系・ローター並びの基準として扱う。

確認対象:

- `config/drone/mujoco-px4-1/drone.xml`
- `config/drone/mujoco-px4-1/drone_config_0.json`

この構成では、MuJoCo 側の `propNames` は以下の順で定義されている。

- `d1_prop1`
- `d1_prop2`
- `d1_prop3`
- `d1_prop4`

MuJoCo `drone.xml` 上の位置は FLU として解釈する。

| Prop | MuJoCo `drone.xml` position (FLU) | `rotorPositions` (FRD) |
|------|-----------------------------------|------------------------|
| `d1_prop1` | `( 0.05, -0.05, 0.0 )` | `( 0.05,  0.05, 0.0 )` |
| `d1_prop2` | `(-0.05,  0.05, 0.0 )` | `(-0.05, -0.05, 0.0 )` |
| `d1_prop3` | `( 0.05,  0.05, 0.0 )` | `( 0.05, -0.05, 0.0 )` |
| `d1_prop4` | `(-0.05, -0.05, 0.0 )` | `(-0.05,  0.05, 0.0 )` |

ここから分かることは、

- `x` はそのまま使っている
- `y` は FLU → FRD 変換により符号反転している
- `z` はこの実績構成では `0.0` を使っている

したがって、`mujoco-px4-1` を基準にした最小写像規則は以下である。

```text
FRD.x = FLU.x
FRD.y = -FLU.y
FRD.z = 0.0   // 現行実績構成では z を使わない
```

`rotationDirection` は、上記の位置写像とは独立に、
既存実績構成の並び順を維持したまま使う。

### `rotationDirection` の意味

`rotationDirection` は、**機体を上から人間が見たときのプロペラ回転方向**を表す。

- `rotationDirection = +1`
  - **CCW (Counter Clockwise, 反時計回り)**
- `rotationDirection = -1`
  - **CW (Clockwise, 時計回り)**

実装上は、この値は `ccw` 符号として扱われ、
反トルク計算の符号にもそのまま使われる。

根拠:

- [rotor_physics.hpp](/src/physics/rotor_physics.hpp)
- [rotor_physics.cpp](/src/physics/rotor_physics.cpp)

### 2. `tuning/x500/config/drone/mujoco-x500-mixer-on`

`x500` は `mujoco-px4-1` を基準に、ローター配置のスケールやモデル差分を反映する対象として扱う。

確認対象:

- `tuning/x500/config/drone/mujoco-x500-mixer-on/drone.xml`
- `tuning/x500/config/drone/mujoco-x500-mixer-on/drone_config_0.json`

`x500` では、MuJoCo モデル上のプロペラ位置が `mujoco-px4-1` より大きい。

| Prop | MuJoCo `drone.xml` position (FLU) | `rotorPositions` (FRD) |
|------|-----------------------------------|------------------------|
| `prop1` | `( 0.18, -0.18, 0.02 )` | `( 0.18,  0.18, 0.0 )` |
| `prop2` | `(-0.18,  0.18, 0.02 )` | `(-0.18, -0.18, 0.0 )` |
| `prop3` | `( 0.18,  0.18, 0.02 )` | `( 0.18, -0.18, 0.0 )` |
| `prop4` | `(-0.18, -0.18, 0.02 )` | `(-0.18,  0.18, 0.0 )` |

この構成では、`mujoco-px4-1` と同じ写像規則を維持し、
XY のスケールだけを `0.05 -> 0.18` に変更している。

現時点では、

- `x` はそのまま使う
- `y` は符号反転する
- `z` は `0.0` を使う

という実績構成を採用している。

したがって、`x500` への反映規則は以下である。

```text
FRD.x = FLU.x
FRD.y = -FLU.y
FRD.z = 0.0
```

加えて、

- `rotationDirection` の並び順は `mujoco-px4-1` と同じ規則を維持する
- まずは座標系と符号を優先して整合させ、`z` 反映の是非は別論点として扱う

### `mujoco-px4-1` と `tuning/x500/config/drone/mujoco-x500-mixer-on` の差分

両者の差分は、主に「モデル寸法・慣性・ローター位置スケール」であり、
座標系の写像規則そのものは維持している。

| 項目 | `mujoco-px4-1` | `tuning/x500/config/drone/mujoco-x500-mixer-on` | 備考 |
|------|----------------|---------------------|------|
| MuJoCo body 名 | `d1_drone_base` | `drone_base` | モデル名差分 |
| prop 名 | `d1_prop1..4` | `prop1..4` | 名前差分 |
| MuJoCo prop 位置 | `±0.05` | `±0.18` | `x500` の方が大型 |
| MuJoCo prop z | `0.0` | `0.02` | `x500` はモデル上の高さあり |
| `rotorPositions` XY | `±0.05` | `±0.18` | XY スケールのみ更新 |
| `rotorPositions` z | `0.0` | `0.0` | 現行実績では維持 |
| `rotationDirection` 並び | `+1,+1,-1,-1` | `+1,+1,-1,-1` | 規則は維持 |
| mass_kg | `0.71` | `0.730482` | `x500` の方がやや重い |
| inertia | `0.0061, 0.00653, 0.0116` | `0.000813645, 0.000813645, 0.00155585` | モデル依存で差分あり |
| rotor `Ct` | `8.3E-07` | `1.12E-05` | rotor モデル差分 |
| rotor `Cq` | `3.0E-08` | `1.55E-07` | rotor モデル差分 |
| rotor `K` | `3.28E-03` | `1.03796702E-02` | rotor モデル差分 |
| rotor `J` | `8.12E-06` | `4.00E-05` | rotor モデル差分 |

重要なのは、`x500` では以下を **変えていない** 点である。

- FLU → FRD の写像規則
- `rotationDirection` の並び順
- `rotorPositions.z = 0.0` という運用上の判断

したがって、`x500` 対応の本質は

- モデル寸法とローター位置スケールを更新する
- ただし写像規則と回転方向規則は `mujoco-px4-1` を維持する

という点にある。

---

## MuJoCo モデル時の設定反映ルール

`physicsEquation = MuJoCo` の場合、`drone_config_0.json` に項目が存在していても、
本体物理へは反映されないものがある。

### 有効な設定

| 項目 | 役割 | 備考 |
|------|------|------|
| `droneDynamics.mujoco.modelName` | MuJoCo body 名 | 使用される |
| `droneDynamics.mujoco.propNames` | prop body 名 | 使用される |
| `droneDynamics.mujoco.modelPath` | MuJoCo XML パス | 使用される |
| `rotor.dynamics_constants.R` | モータ抵抗 | 使用される |
| `rotor.dynamics_constants.Ct` | 推力係数 | 使用される |
| `rotor.dynamics_constants.Cq` | 反トルク係数 | 使用される |
| `rotor.dynamics_constants.K` | モータ定数 | 使用される |
| `rotor.dynamics_constants.D` | ロータ回転抵抗 | 使用される |
| `rotor.dynamics_constants.J` | ロータ慣性 | 使用される |
| `thruster.rotorPositions` | ローター位置 (FRD) | 使用される |
| `thruster.Ct` | 合推力計算用係数 | 使用される |
| `position_meter` | 初期位置 | 使用される |
| `angle_degree` | 初期姿勢 | 使用される |

### 本体物理には反映されない設定

以下は `aircraft_factory` から setter は呼ばれるが、
MuJoCo 実装側では現状無視される。

| 項目 | 現状 | 根拠 |
|------|------|------|
| `droneDynamics.mass_kg` | 無視 | `set_mass()` は no-op |
| `droneDynamics.inertia` | 無視 | `set_torque_constants()` は no-op |
| `droneDynamics.body_size` | 無視 | `set_body_size()` は no-op |

### 実際に参照される mass / inertia

MuJoCo 機体の本体質量・慣性は、`drone_config_0.json` ではなく、
**MuJoCo モデル (`drone.xml`) から取得される。**

実装上は以下を参照している。

- `mujoco_model->body_subtreemass[body_id]`
- `mujoco_model->body_inertia[...]`

したがって、MuJoCo 機体の本体質量・慣性を調整したい場合は、
`drone_config_0.json` ではなく `drone.xml` 側を修正する必要がある。

### 空気抵抗の扱い

空気抵抗は 2 層に分かれる。

1. **ローター軸まわりの抵抗**
   - `rotor.dynamics_constants.D`
   - ロータ回転数のダイナミクスに使う
   - 機体全体の空力抵抗ではない

2. **機体全体の空力抵抗**
   - `droneDynamics.airFrictionCoefficient`
   - BodyFrame 実装では本体並進運動の drag として使う
   - MuJoCo 実装でも同じ drag モデルを使う
   - ただし MuJoCo では、計算した抗力を **重心への外力** として与える

したがって、`physicsEquation = MuJoCo` の場合でも、
`airFrictionCoefficient` の物理的な意味は BodyFrame と同じとみなしてよい。
違うのは、力の適用先が

- BodyFrame: 自前の運動方程式
- MuJoCo: MuJoCo への外力適用

である点である。

---

## 今回の符号問題

この節では、今回発見した以下の問題を正式に整理する。

- MuJoCo モデル配置と `rotorPositions` の対応が暗黙的だった
- `mujoco-px4-1` と同じ並び順を維持すべき箇所が明文化されていなかった
- NED / FRD / MuJoCo ローカル座標の混同により、符号の誤解が生じやすかった

今回まず固定すべき事実は以下である。

- 箱庭/PX4 側のローター配置は **FRD**
- MuJoCo 側のモデル配置は **FLU**
- したがって、`rotorPositions` を考える時に NED を直接持ち込まない
- world frame の NED と、body frame の FRD を混同しない

TODO:

- 何が誤っていたか
- 正しい写像規則
- `x500` への反映方法

---

## 関連ドキュメント

- [fundamental/README.md](/docs/fundamental/README.md)
- [aircraft/README.md](/docs/architecture/aircraft/README.md)
- [thruster/README.md](/docs/architecture/aircraft/thruster/README.md)
- [rotor/README.md](/docs/architecture/aircraft/rotor/README.md)
