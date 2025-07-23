# 機体のパラメータ説明

箱庭ドローンシミュレータには機体の外部設定ファイルがあります。

各項目の設定内容は以下のとおりです。

## シミュレーション設定
- **name**: 機体名
- **lockstep**: シミュレーションのロックステップモード。`true` で同期モードに設定されます。
- **timeStep**: シミュレーションのタイムステップ間隔。単位は秒(`s`)。例: `0.003`。
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
    - **modelPath**: MuJoCoモデルファイルのパス。
    - **modelName**: モデル名。
    - **propNames**: プロペラ名（複数指定可）。
- **rotor**: ローターの設定。
  - **vendor**: ベンダ名。現状は`None`。
  - **rpmMax**: ローターの最大回転数 (rpm)。
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
  - **NominalCapacity**: 公称容量 (mAh)。
  - **EODVoltage**: 放電終止電圧 (V)。
  - **VoltageLevelGreen**: 電圧レベル（緑）の閾値 (V)。
  - **VoltageLevelYellow**: 電圧レベル（黄）の閾値 (V)。
  - **CapacityLevelYellow**: 容量レベル（黄）の閾値 (%)。
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
- **direct_rotor_control**: ローターの直接制御を有効にする場合は`true`。
- **mixer**: (オプション) ドローンのミキサー設定。未設定の場合は、推力とトルクが直接物理モデルに入力されます。
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


## 機体パラメータの設定例

- [PX4連携](https://github.com/toppers/hakoniwa-drone-core/blob/main/config/drone/px4/drone_config_0.json)
- [Ardupilot連携](https://github.com/toppers/hakoniwa-drone-core/blob/main/config/drone/ardupilot/drone_config_0.json)
- [ゲームパッドによるドローン操作](https://github.com/toppers/hakoniwa-drone-core/blob/main/config/drone/rc/drone_config_0.json)
- [Python APIによるドローン操作](https://github.com/toppers/hakoniwa-drone-core/blob/main/config/drone/api/drone_config_0.json)
