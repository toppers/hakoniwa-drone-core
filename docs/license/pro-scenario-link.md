# 箱庭ドローン・シナリオLink

箱庭ドローン・シナリオLinkは、故障、外乱、センサノイズなどの検証条件を、箱庭ドローンPROに接続・反映するためのオプションです。

具体的には、
- 箱庭ドローンPROのコンポーネントである、`aircraft` の外乱入力を、
- `Disturbance` PDU および関連APIを通して、
- 外部環境モデル、故障シナリオ、風条件、センサ条件などを含む検証シナリオに接続する
ためのオプションです。

これにより、機体挙動、制御応答、安全余裕、破綻条件などを事前に確認し、実機試験で重点的に確認すべき条件を絞り込むことができます。

シナリオLinkで扱う主な入力は以下の通りです。

- 風外乱
- 温度
- 気圧
- 周辺障害物情報
- センサノイズ
- 故障注入

これらの外乱系入力は、`Disturbance` PDU に集約され、箱庭ドローンPRO本体へ入力されます。

`Disturbance` PDU の値を、センサ、アクチュエータ、物理モデル、MuJoCo連携などへどのように反映するかは、契約範囲内で利用者がカスタマイズできます。

`Disturbance` PDU のメンバとの対応関係は以下の通りです。

| シナリオ入力 | `Disturbance` PDU メンバ | 意味 |
| --- | --- | --- |
| 風外乱 | `d_wind.value.x`, `d_wind.value.y`, `d_wind.value.z` | 風速ベクトル |
| 周辺障害物情報 | `d_boundary.boundary_point`, `d_boundary.boundary_normal` | 機体に最も近い地面、壁、天井などの代表点と法線方向 |
| 温度 | `d_temp.value` | 環境温度 |
| 気圧 | `d_atm.sea_level_atm` | 海面気圧 |
| センサノイズおよび故障注入 | `d_user_custom` の拡張領域 | センサノイズ、故障注入、検証シナリオ固有の拡張入力 |

デフォルト実装の代表例は以下の通りです。

- ローター故障注入
  - `Disturbance` PDU の拡張領域からデコードされ、各ローターの制御入力に対する倍率として適用されます。倍率 `1.0` は正常状態、`0.0` は完全故障、`0.0` から `1.0` の間は出力低下を表します。
- 風外乱
  - 機体の運動計算に反映されます。風シミュレータやシナリオ側が時刻に応じて `d_wind` の風ベクトルを更新することで、変動風や乱流相当の条件を表現できます。MuJoCoを利用する構成では、受信した風外乱から相対風速を計算し、抗力としてMuJoCo側へ外力を適用します。
- 周辺障害物情報
  - 機体に最も近い地面、壁、天井などの環境面を表します。箱庭ドローンPROは、この代表点と法線方向から、ローターまわりの境界面近接外乱を計算します。
- 温度
  - バッテリーモデルの入力として利用されます。
- 気圧
  - センサおよび機体運動に関係する環境条件として利用されます。

## 補足

箱庭ドローン・シナリオLinkを含まない利用形態では、故障注入、外乱入力、環境条件を含むシナリオ連携機能は未サポートです。

## コード上の境界

箱庭ドローン・シナリオLinkの境界は、ビルドマクロでは分離しません。

シナリオLinkは、ライセンス契約者が利用できる機能として提供します。無償版では、`Disturbance` PDU を利用した故障注入、外乱入力、環境条件連携は未サポートの扱いとします。

主なコード上の対象は以下です。

| 対象 | 内容 |
| --- | --- |
| `include/aircraft/interfaces/idisturbance.hpp` | 外乱入力およびローター故障注入の内部型定義 |
| `include/aircraft/interfaces/iaircraft_input.hpp` | 機体入力としての disturbance 集約 |
| `src/service/impl/service_pdu_syncher.hpp` | `Disturbance` PDU から内部 disturbance へのコピーおよびローター故障注入デコード |
| `src/service/drone/impl/drone_service.cpp` | サービス層での `Disturbance` PDU 受信、座標変換、機体入力への反映 |
| `src/aircraft/impl/aircraft.hpp` | バッテリー、ローター、機体ダイナミクス、センサへの disturbance 適用 |
| `src/aircraft/impl/fault_injection/fault_rotor.hpp` | ローター故障注入の適用 |
| `src/aircraft/impl/body/drone_dynamics_mujoco.hpp` | MuJoCo構成での風外乱の外力適用 |
| `src/aircraft/impl/body/drone_dynamics_body_frame.hpp` | BodyFrame構成での風外乱および境界面近接外乱の運動計算への反映 |
| `src/aircraft/impl/battery/battery_dynamics.hpp` | 温度を利用したバッテリーモデル |
| `src/aircraft/impl/sensors/sensor_gps.hpp` | GPSセンサの出力生成およびセンサ条件の拡張対象 |

## ビルド方法

箱庭ドローン・シナリオLinkは、専用のCMakeビルドオプションでは有効化しません。

通常のビルド手順は以下です。

```sh
tools/build-mac.bash build
tools/build-ubuntu.bash build
```

```powershell
.\tools\build-win.ps1
```

シナリオLinkの利用可否は、ビルド成果物ではなく、ライセンス契約および提供されるシナリオ連携機能の利用条件によって扱います。
