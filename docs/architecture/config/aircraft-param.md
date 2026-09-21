# 機体のパラメータ説明

箱庭ドローンシミュレータには機体の外部設定ファイルがあります。

各項目の設定内容は以下のとおりです。

## シミュレーション設定
- **name**: 機体名
- **lockstep**: シミュレーションのロックステップモード。`true` で同期モードに設定されます。
- **timeStep**: シミュレーションのタイムステップ間隔。単位は秒(`s`)。例: `0.003`。
- **sitl**: (オプション) PX4 / ArduPilot などの SITL 連携時の診断設定。
  - **actuator_timeout_msec**: SITL からの actuator 入力を最後に受信してから timeout と判定するまでの時間。単位はミリ秒(`ms`)。未指定時は `300`。
- **logging**: ログ採取方式の設定。
  - **mode**: ログ採取方式。
    - `csv`: 現行の CSV ログ出力を行います。
    - `none`: ログを採取しません。CSV ファイルやログディレクトリも生成しません。
    - `memory`: 将来拡張用の予約値です。現時点では仕様上の予約とします。
- **logOutputDirectory**: ログファイルの出力ディレクトリへのパス。例: `"./"`。
- **logOutput**: 各種センサーとMAVLinkのログ出力の有効/無効。
  - **sensors**: 各センサーのログ出力設定。`true` または `false`。
  - **mavlink**: MAVLinkメッセージのログ出力設定。`true` または `false`。
- **mavlink_tx_period_msec**: MAVLinkメッセージの送信周期。単位はミリ秒(`ms`)。
- **location**: シミュレーションの地理的位置。
  - **latitude**: 緯度。単位は度(`deg`)。
  - **longitude**: 経度。単位は度(`deg`)。
  - **altitude**: 高度。単位はメートル(`m`)。
  - **magneticField**: 地磁気の強度と方向。
    - **intensity_nT**: 地磁気の強度。単位はナノテスラ(`nT`)。
    - **declination_deg**: 地磁気の偏角。単位は度(`deg`)。
    - **inclination_deg**: 地磁気の傾斜角。単位は度(`deg`)。

### logging と logOutput の関係

- `simulation.logging.mode = "none"` の場合:
  - ログ採取自体を行いません
  - `logOutputDirectory` は実質未使用です
  - `logOutput.sensors` / `logOutput.mavlink` は無視されます
- `simulation.logging.mode = "csv"` の場合:
  - 従来どおり CSV 出力を行います
  - `logOutputDirectory` と `logOutput.*` が有効です
- `simulation.logging.mode` が未指定の場合:
  - 後方互換のため、`csv` と同等に扱う想定です

### SITL actuator timeout 監視

PX4 / ArduPilot などの外部 SITL と接続する場合、通常は actuator 入力を受信したタイミングで機体の物理更新を行い、Hakoniwa simulation tick 側で sensor データを送信します。

```text
actuator受信イベント:
  -> actuator入力を反映
  -> aircraft->run()

Hakoniwa simulation tick:
  -> send_sensor_data()
  -> write_back_pdu()
```

この構造では、SITL 側から actuator 入力が一定時間届かなくなると、`aircraft->run()` が呼ばれず、機体内部の simulation time が進まなくなります。その結果、`send_sensor_data()` の周期判定に使う時刻も進まず、Hakoniwa 全体の simulation tick は進んでいても sensor 送信が止まる場合があります。

`simulation.sitl.actuator_timeout_msec` は、この状態を検出してログへ出すための閾値です。timeout 検出時に、最後に受信した actuator timestamp、最後に送信した sensor timestamp、外部シミュレーション時刻、機体内部の simulation time を出力します。

設定例:

```json
{
  "simulation": {
    "lockstep": true,
    "timeStep": 0.003,
    "sitl": {
      "actuator_timeout_msec": 300
    }
  }
}
```

未設定時は、次と同等に扱います。

```text
actuator_timeout_msec = 300
```

この監視ログは、SITL 側が actuator 出力を止める根本原因を解決するものではありません。長時間 timeout が継続する場合は、SITL 側の状態、MAVLink/TCP 通信、GCS/mission 操作の影響を確認してください。

### SITL actuator timeout ログ

actuator timeout を検出すると、次のような warning が出力されます。

```text
WARN: [sitl-lockstep] actuator receive timeout aircraft_index=0 timeout_active=1 actuator_age_sec=2 hako_time_usec=2929014000 last_actuator_sim_usec=1783566165101128 sensor_age_sec=0 last_sensor_sim_usec=1783566165104128 current_sim_usec=823308000
```

各項目の意味は次のとおりです。

| 項目 | 時刻の種類 | 意味 |
|---|---|---|
| `aircraft_index` | index | 対象機体の index |
| `timeout_active` | 状態 | `1` の場合、actuator timeout を検出中 |
| `actuator_age_sec` | 実時間 | 最後に actuator 入力を受信してからの経過秒 |
| `external_time_usec` | 外部 simulation time | 接続先のシミュレーション時刻。箱庭連携時はasset時刻 |
| `last_actuator_sim_usec` | SITL message timestamp | 最後に受信した actuator message の timestamp |
| `sensor_age_sec` | 実時間 | 最後に sensor 送信に成功してからの経過秒 |
| `last_sensor_sim_usec` | MAVLink sensor timestamp | 最後に送信した sensor message の timestamp |
| `current_sim_usec` | aircraft simulation time | 機体内部の simulation time。`aircraft->run()` で進む |

ログの見方:

- `external_time_usec` が進み、`current_sim_usec` が止まる場合:
  - 外部シミュレーション時刻は進んでいるが、機体内部の物理更新が止まっています。
- `actuator_age_sec` が増え続ける場合:
  - SITL 側から actuator 入力が届いていません。
- `sensor_age_sec` も増え続ける場合:
  - sensor 送信も止まっています。`current_sim_usec` が止まっている場合は、sensor 周期判定に使う機体内部時刻が進んでいない可能性があります。
- `external_time_usec` が進み、`actuator_age_sec` が増え続ける場合:
  - 外部シミュレーション時刻は進んでいますが、SITL 側から actuator 入力が戻っていません。

timeout 検出後に actuator 入力を再受信すると、次のような復帰ログが出ます。

```text
INFO: [sitl-lockstep] actuator receive recovered aircraft_index=0 aircraft_sim_usec=824000000 actuator_sim_usec=1783566165401128
```

### 実験的な外部時刻/SITL時刻バリア

時刻ドメイン、bootstrap、通常時の双方向barrier、マルチ機の動作契約は
[SITL and Hakoniwa asset time synchronization](../aircraft/sitl-time-sync.md)
を正本とする。

`hakoniwa-build.yaml`の`features.sitl_asset_time_sync`を`true`にしてビルドすると、従来のtimeout監視に加えて、
外部シミュレーション時刻と機体内部時刻を相互に待ち合わせる方式が有効になります。
この機能はデフォルトで`ON`です。従来の非同期方式を明示的に確認する場合だけ`false`を指定してください。

Aircraft Serviceは`IServicePduSyncher`の任意の時刻同期機能だけを使用します。
通常の`ServicePduSyncher`はNOPなので箱庭なしでは既存経路のままです。箱庭連携時だけ
`HakoniwaSimulator`が外部時刻の提供・待機・停止通知を実装します。

```yaml
features:
  sitl_asset_time_sync: true
```

この方式では、処理の所有者を次のように分離します。

```text
SITL actuator受信スレッド:
  -> 外部シミュレーション時刻が追いつくまで待つ
  -> actuator入力を反映
  -> aircraft->run()
  -> sensor送信

外部シミュレーションstep callback:
  -> aircraft timeが次の外部tickへ到達するまで待つ
  -> PDUを書き戻す
  -> 外部シミュレーション時刻を1 tick進める
```

待機が診断間隔を超えると、次のいずれかを出力します。

- `event=external_time_waiting_for_sitl`: 外部シミュレーション側はstep callbackへ到達しているが、
  SITLから次のactuatorが届かず、機体物理時刻が進んでいない。
- `event=sitl_waiting_for_external_time`: SITLのactuatorは届いているが、
  外部シミュレーション時刻が進んでいない。
- `event=external_time_wait_for_sitl_recovered` / `event=sitl_wait_for_external_time_recovered`:
  対応する待機状態から復帰した。

各ログには`external_time_usec`、`aircraft_time_usec`、`skew_usec`、
`actuator_count`、`physics_step_count`、`sensor_send_count`を含めます。
カウンタが止まった位置と待機方向を併せて確認することで、SITL/MAVLink側と
外部シミュレーションcallback側のどちらから調査すべきかを切り分けられます。

PX4とArduPilotは共通のAircraft Service同期クラスを使用しますが、現時点の
実SITL確認範囲はPX4です。

### パス解決の基準

path 項目は、次の順で解決する方針とする。

1. 絶対パスならそのまま使う
2. 相対パスなら config ファイル基準で解決を試みる
3. それで見つからない場合のみ、プロセスのカレントディレクトリ基準でも解決を試みる

この fallback は後方互換のために残す。
将来的な正規仕様は、config ファイル基準の相対パスとする。

対象例:

- `simulation.logOutputDirectory`
- `components.battery.BatteryModelCsvFilePath`
- `controller.moduleDirectory`
- `controller.paramFilePath`
- `components.sensors.*.vendor`

## コンポーネント設定
- **droneDynamics**: ドローンの動力学モデル。
  - **physicsEquation**: 運動方程式のタイプを指定します。
    - `BodyFrame`: 箱庭のデフォルト物理モデル。
    - `BodyFrameMatlab`: MATLABで生成した物理モデル。
    - `Mujoco`: MuJoCoシミュレータ連携モデル。
  - **useQuaternion**: 姿勢計算にクォータニオンを使用する場合は`true`。
  - **collision_detection**: 障害物との衝突を検出して物理式にフィードバックする場合は`true`。
  - **enable_disturbance**: 風や温度などの外乱を物理/センサモデルにフィードバックする場合は`true`。
  - **manual_control**: センサキャリブレーション等で機体を手動操作する場合に`true`。
  - **airFrictionCoefficient**: 空気抵抗係数。1次項と2次項を配列で指定します。
  - **inertia**: 慣性モーメント [Ixx, Iyy, Izz]。単位は `kg*m^2`。
  - **mass_kg**: ドローンの質量。単位は `kg`。
  - **body_size**: 機体のサイズ [x, y, z]。単位は `m`。
  - **position_meter**: 機体の初期位置 [x, y, z]。単位は `m`。
  - **angle_degree**: 機体の初期角度 [roll, pitch, yaw]。単位は `deg`。
  - **out_of_bounds_reset**: (オプション) 機体がシミュレーション範囲外に出た際の自動リセット設定。
    - **position**: 位置 [x, y, z] のリセットを有効にするか。
    - **velocity**: 速度 [x, y, z] のリセットを有効にするか。
    - **angular_velocity**: 角速度 [x, y, z] のリセットを有効にするか。
  - **body_boundary_disturbance_power**: (オプション) 地面効果の強さ。デフォルトは `1.0`。
  - **mujoco**: (オプション) MuJoCo連携用の設定。
    - **modelPath**: MuJoCoモデルファイルのパス。`.xml`は`mj_loadXML()`でコンパイルして読み込み、`.mjb`は`mj_loadModel()`でコンパイル済みモデルを直接読み込む。拡張子の大文字・小文字は区別しない。それ以外の拡張子は設定誤りとして拒否する。
    - **modelName**: モデル名。
    - **propNames**: プロペラ名（複数指定可）。

### MuJoCo XMLとMJB

`.xml`は可搬性と編集性を持つ正本として使用する。大規模なmeshを含むworldでは、起動ごとにXMLをコンパイルすると時間がかかるため、同じMuJoCo versionで事前生成した`.mjb`を`modelPath`へ指定できる。

MJBはMuJoCo version-boundな実行成果物であり、異なるMuJoCo versionで生成したファイルの互換性は保証しない。Drone PRO側のMuJoCoを更新した場合は、正本XMLからMJBを再生成すること。MJBの配布・生成工程では、正本XMLのhash、MJBのhash、生成に使用したMuJoCo versionを併せて記録することを推奨する。
- **rotor**: ローターの設定。
  - **vendor**: ベンダ名。現状は`None`。
  - **rpmMax**: ローターの最大回転数 (rpm)。
  - **max_rad_per_sec**: (オプション) ローターの有効最大角速度。単位は `rad/s`。未指定時は後方互換のため、ホバリング角速度 `omega_hover = sqrt(mass_kg * g / (Ct * ROTOR_NUM))` の 2 倍を使用します。指定時はその値を有効最大角速度として使用します。v4.0.0 では一次遅れモデルの duty-to-speed scale も、この有効最大角速度と同じ値として扱います。
  - **radius**: ローターの半径 (m)。
  - **dynamics_constants**: ローターの動力学定数。
    - **R**: 電気抵抗 (Ω)。
    - **Cq**: トルク係数 (Nms^2/rad^2)。
    - **Ct**: 推力係数 (Ns^2/rad^2)。
    - **D**: 動粘性摩擦係数 (Nms/rad)。
    - **K**: 逆起電力定数 (Nm/A)。
    - **J**: モーターイナーシャ (kg*m^2)。
- **battery**: (オプション) バッテリーモデルの設定。
  - **vendor**: ベンダ名。
  - **model**: モデルタイプ (`"constant"`など)。
  - **BatteryModelCsvFilePath**: バッテリーモデルのCSVファイルパス。
  - **NominalVoltage**: 公称電圧 (V)。
  - **NominalCapacity**: 公称容量 (Ah)。内部実装でも容量は hour 系で扱われるため、current config の `4.0` は 4Ah を意味する。
  - **EODVoltage**: 放電終止電圧 (V)。
  - **VoltageLevelGreen**: 電圧レベル（緑）の閾値 (V)。
  - **VoltageLevelYellow**: 電圧レベル（黄）の閾値 (V)。
  - **CapacityLevelYellow**: 容量レベル（黄）の閾値 (Ah)。
- **thruster**: スラスターの設定。
  - **vendor**: ベンダ名。現状は`None`。
  - **rotorPositions**: ローターの位置と回転方向。
    - **position**: 位置 [x, y, z] (m)。
    - **rotationDirection**: 回転方向 (CW: -1.0, CCW: 1.0)。
  - **Ct**: 推力係数 (Ns^2/rad^2)。
- **sensors**: 各種センサーの設定。
  - **sampleCount**: サンプル数。
  - **noise**: ノイズレベル（標準偏差）。ノイズがない場合は `0`。
  - **vendor**: (オプション) センサモジュールのパス。
  - **context**: (オプション) センサモジュールに渡す追加情報。
    - **moduleName**: モジュール名。

## コントローラ設定

**controller**セクションでは、ドローンのフライトコントローラーモジュールに関連する設定を行います。

- **moduleDirectory**: (オプション) フライトコントローラーモジュールのディレクトリパス。
- **moduleName**: (オプション) 使用するフライトコントローラーモジュール名。
- **paramFilePath**: (オプション) コントローラのパラメータファイルへのパス。
- **paramText**: (オプション) コントローラのパラメータをテキスト形式で直接記述。
- **serviceMode**: (オプション) 制御サービスの動作モード。
  - `rc`: RC/ゲームパッド入力で機体を操作する。
  - `api`: 外部 API から機体を操作する。
  - `legacy`: 明示指定されない legacy 挙動。controller 種別に応じて `rc` または `api` として解決される。
  - 後方互換のため、既存の `rpc` 指定は `api` として扱われる。
- **apiServiceMode**: (オプション) `serviceMode = api` のときの API 公開方式。
  - `rpc`: 新しい箱庭 RPC service を使う。
  - `legacy-api`: 従来の箱庭 PDU ベース API を使う。
  - 未指定時は `legacy-api` として扱われる。
- **direct_rotor_control**: ローターの直接制御を有効にする場合は`true`。
- **mixer**: (オプション) ドローンのミキサー設定。未設定の場合は、推力とトルクが直接物理モデルに入力されます。
  - **enable**: ミキサーを有効にするかどうか。未指定時は `true` として扱われる。
  - **vendor**: ミキサーのベンダ名 (`"None"`, `"linear"`など)。
  - **enableDebugLog**: デバッグログを有効にする場合は`true`。
  - **enableErrorLog**: エラーログを有効にする場合は`true`。
- **pid**: (オプション) PIDコントローラのゲイン設定。
  - **angle_velocity_pid**: 角速度制御PID。
    - **kp**: 比例ゲイン [roll, pitch, yaw]。
    - **ki**: 積分ゲイン [roll, pitch, yaw]。
    - **kd**: 微分ゲイン [roll, pitch, yaw]。
  - **angle_pid**: 角度制御PID。
    - **kp**: 比例ゲin [roll, pitch, yaw]。
    - **ki**: 積分ゲイン [roll, pitch, yaw]。
    - **kd**: 微分ゲイン [roll, pitch, yaw]。
  - **pos_pid**: 高度制御PID。
    - **kp**: 比例ゲイン [z]。
    - **ki**: 積分ゲイン [z]。
    - **kd**: 微分ゲイン [z]。

### controller パスの仕様

- `moduleDirectory` は config ファイル基準の相対パスを正規仕様とする
- `paramFilePath` も config ファイル基準の相対パスを正規仕様とする
- 後方互換のため、config ファイル基準で見つからない場合のみ、カレントディレクトリ基準でも解決を試みる

### controller service mode の仕様

- `serviceMode = rc`
  - RC/ゲームパッド入力を使う
  - 箱庭 RPC service は作成しない
- `serviceMode = api` かつ `apiServiceMode = rpc`
  - 新しい箱庭 RPC service を使う
- `serviceMode = api` かつ `apiServiceMode = legacy-api`
  - 従来の PDU ベース API を使う

後方互換:

- `serviceMode = rpc`
  - `serviceMode = api`
  - `apiServiceMode = rpc`
  と同義として扱う
- `serviceMode` 未指定時は内部的に `legacy` として扱う
  - radio control controller の場合は `rc`
  - それ以外は `api + legacy-api`


## 機体パラメータの設定例

- [PX4連携](https://github.com/toppers/hakoniwa-drone-core/blob/main/config/drone/px4/drone_config_0.json)
- [Ardupilot連携](https://github.com/toppers/hakoniwa-drone-core/blob/main/config/drone/ardupilot/drone_config_0.json)
- [ゲームパッドによるドローン操作](https://github.com/toppers/hakoniwa-drone-core/blob/main/config/drone/rc/drone_config_0.json)
- [Python APIによるドローン操作](https://github.com/toppers/hakoniwa-drone-core/blob/main/config/drone/api/drone_config_0.json)
