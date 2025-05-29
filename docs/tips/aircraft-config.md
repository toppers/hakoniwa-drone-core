# TIPS

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
    - BodyFrame: 箱庭のデフォルト物理モデルを利用する場合は、この値を設定してください。
    - BodyFrameMatlab: MATLABで生成した物理モデルのコードを利用する場合は、この値を設定してください。
  - **collision_detection**: 障害物との衝突を検出して物理式にフィードバックする場合は`true`。非検出とする場合は、`false`。
  - **enable_disturbance**: 風や温度などの外乱を物理/センサモデルにフィードバックする場合は`true`。非検出とする場合は、`false`。
  - **manual_control**:　センサキャリブレーションで機体を手動で操作した場合に利用します。`true`にすると、外部操作が可能になります。通常は`false`として下さい。
  - **airFrictionCoefficient**: 空気抵抗係数。空気抵抗の１次項と２次項を配列で指定します。
  - **inertia**: 慣性モーメントのリスト。単位はキログラム・メートル二乗(`kg*m^2`)。
  - **mass_kg**: ドローンの質量。単位はキログラム(`kg`)。
  - **body_size**: 機体のサイズ（x, y, z）を配列で指定します。単位はメートル(`m`)。
  - **position_meter**: 機体の初期位置。単位はメートル(`m`)。
  - **angle_degree**: 機体の初期角度。単位は度(`deg`)。
- **rotor**: ローターの設定。
  - **vendor**: ベンダ名を指定します。現状は`None`を設定して下さい。
  - **dynamics_constants**: ローターの動力学定数。
    - **R**: 電気抵抗。単位はオーム(`Ω`)。
    - **Cq**: トルク係数。単位は(`Nms^2/rad^2`)。
    - **D**: 動粘性摩擦係数。単位は(`Nms/rad`)。
    - **K**: 逆起電力定数。単位はラジアン/秒・ボルト(`Nm/A`)。
    - **J**: モーターイナーシャ。単位はキログラム・メートル二乗(`kg*m^2`)。
- **thruster**: スラスターの設定。
  - **vendor**: ベンダ名を指定します。現状は`None`を設定して下さい。
  - **rotorPositions**: ローターの位置と回転方向。単位はメートル(`m`)。rotationDirectionはローターの回転方向(CW:-1.0, CCW: 1.0)
  - **Ct**: 推力係数。単位は(`Ns^2/rad^2`)。
- **sensors**: 各種センサーの設定。
  - **sampleCount**: サンプル数
  - **noise**:ノイズレベル(標準偏差)。ノイズ未設定の場合は0。


## コントローラ設定

**controller**セクションでは、ドローンのフライトコントローラーモジュールに関連する設定を行います。以下のパラメータが設定可能です。

- **moduleDirectory**: フライトコントローラーモジュールが格納されているディレクトリパスを指定します。例えば、`"../src/drone_control/cmake-build/workspace/FlightController"` のようにモジュールのパスを指定します。
  
- **moduleName**: 使用するフライトコントローラーモジュールの名前を指定します。これにより、シミュレーション内でどのフライトコントローラーモジュールが使用されるかを決定します。例: `"FlightController"`。

- **direct_rotor_control**: ローターの直接制御を有効にするかどうかを指定します。`true`に設定すると、ローターを直接操作する制御が有効になります。通常は`false`に設定します。

- **mixer**: ドローンのミキサー設定を指定します。本セクション未設定の場合は、直接、推力とトルクが物理モデルに入力されます。
  - **vendor**: ミキサーのベンダ名を指定します。現状では`"None"`と`"linear"`を指定できます。
  - **enableDebugLog**: デバッグログの出力を有効にするかどうかを指定します。`true`でデバッグログが有効になります。
  - **enableErrorLog**: エラーログの出力を有効にするかどうかを指定します。`true`でエラーログが有効になります。


## 機体パラメータの設定例

- [PX4連携](https://github.com/toppers/hakoniwa-drone-core/blob/main/config/drone/px4/drone_config_0.json)
- [Ardupilot連携](https://github.com/toppers/hakoniwa-drone-core/blob/main/config/drone/ardupilot/drone_config_0.json)
- [ゲームパッドによるドローン操作](https://github.com/toppers/hakoniwa-drone-core/blob/main/config/drone/rc/drone_config_0.json)
- [Python APIによるドローン操作](https://github.com/toppers/hakoniwa-drone-core/blob/main/config/drone/api/drone_config_0.json)
