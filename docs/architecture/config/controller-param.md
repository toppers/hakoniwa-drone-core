
# ドローン制御パラメータ

このドキュメントは、`param-api-mixer.txt` ファイルに記載されている各パラメータの役割について説明します。

## 基本パラメータ

- `SIMULATION_DELTA_TIME`: シミュレーションの1ステップあたりの時間（秒）。
- `MASS`: ドローンの質量（kg）。
- `GRAVITY`: 重力加速度（m/s^2）。

## 高度制御

- `PID_ALT_CONTROL_CYCLE`: 高度制御の実行周期（秒）。0の場合は毎周期実行。
- `PID_ALT_MAX_POWER`: 高度制御における最大出力（スロットル）。
- `PID_ALT_THROTTLE_GAIN`: スロットル入力に対するゲイン。
- `PID_ALT_MAX_SPD`: 目標高度へ移動する際の最大速度（m/s）。

### 高度制御のPIDパラメータ

- `PID_ALT_Kp`: 高度制御の比例ゲイン。
- `PID_ALT_Ki`: 高度制御の積分ゲイン。
- `PID_ALT_Kd`: 高度制御の微分ゲイン。
- `PID_ALT_SPD_Kp`: 高度方向の速度制御の比例ゲイン。
- `PID_ALT_SPD_Ki`: 高度方向の速度制御の積分ゲイン。
- `PID_ALT_SPD_Kd`: 高度方向の速度制御の微分ゲイン。

### スラスト基本値

- `BASE_THRUST_DIVISOR`: ホバリングに必要なスラストを計算する際の除数。 `(mass * gravity) / BASE_THRUST_DIVISOR` のように使われる。1.0以上の値を設定する。0.0を設定すると、この項は無効になる。

## 水平制御

- `POS_CONTROL_CYCLE`: 水平位置制御の実行周期（秒）。0の場合は毎周期実行。
- `SPD_CONTROL_CYCLE`: 水平速度制御の実行周期（秒）。0の場合は毎周期実行。
- `PID_POS_MAX_SPD`: 目標位置へ移動する際の最大速度（m/s）。

### 水平位置制御のPIDパラメータ

- `PID_POS_X_Kp`: 水平位置（X軸）制御の比例ゲイン。
- `PID_POS_X_Ki`: 水平位置（X軸）制御の積分ゲイン。
- `PID_POS_X_Kd`: 水平位置（X軸）制御の微分ゲイン。
- `PID_POS_Y_Kp`: 水平位置（Y軸）制御の比例ゲイン。
- `PID_POS_Y_Ki`: 水平位置（Y軸）制御の積分ゲイン。
- `PID_POS_Y_Kd`: 水平位置（Y軸）制御の微分ゲイン。

### 水平速度制御のPIDパラメータ

- `PID_POS_VX_Kp`: 水平速度（X軸）制御の比例ゲイン。
- `PID_POS_VX_Ki`: 水平速度（X軸）制御の積分ゲイン。
- `PID_POS_VX_Kd`: 水平速度（X軸）制御の微分ゲイン。
- `PID_POS_VY_Kp`: 水平速度（Y軸）制御の比例ゲイン。
- `PID_POS_VY_Ki`: 水平速度（Y軸）制御の積分ゲイン。
- `PID_POS_VY_Kd`: 水平速度（Y軸）制御の微分ゲイン。

## 姿勢角制御

- `HEAD_CONTROL_CYCLE`: 機首方位制御の実行周期（秒）。0の場合は毎周期実行。
- `ANGULAR_CONTROL_CYCLE`: 姿勢角制御の実行周期（秒）。0の場合は毎周期実行。
- `ANGULAR_RATE_CONTROL_CYCLE`: 角速度制御の実行周期（秒）。0の場合は毎周期実行。
- `PID_POS_MAX_ROLL`: 水平位置制御によって生成される最大ロール角（度）。
- `PID_POS_MAX_PITCH`: 水平位置制御によって生成される最大ピッチ角（度）。
- `PID_ROLL_RPM_MAX`: ロール角制御によって生成される最大ロール角速度（RPM）。
- `PID_PITCH_RPM_MAX`: ピッチ角制御によって生成される最大ピッチ角速度（RPM）。
- `PID_ROLL_TORQUE_MAX`: ロール角速度制御によって生成される最大トルク。
- `PID_PITCH_TORQUE_MAX`: ピッチ角速度制御によって生成される最大トルク。
- `PID_YAW_TORQUE_MAX`: ヨー角速度制御によって生成される最大トルク。

### ロール角度とロール角速度制御のPIDパラメータ

- `PID_ROLL_Kp`: ロール角制御の比例ゲイン。
- `PID_ROLL_Ki`: ロール角制御の積分ゲイン。
- `PID_ROLL_Kd`: ロール角制御の微分ゲイン。
- `PID_ROLL_RATE_Kp`: ロール角速度制御の比例ゲイン。
- `PID_ROLL_RATE_Ki`: ロール角速度制御の積分ゲイン。
- `PID_ROLL_RATE_Kd`: ロール角速度制御の微分ゲイン。

### ピッチ角度とピッチ角速度制御のPIDパラメータ

- `PID_PITCH_Kp`: ピッチ角制御の比例ゲイン。
- `PID_PITCH_Ki`: ピッチ角制御の積分ゲイン。
- `PID_PITCH_Kd`: ピッチ角制御の微分ゲイン。
- `PID_PITCH_RATE_Kp`: ピッチ角速度制御の比例ゲイン。
- `PID_PITCH_RATE_Ki`: ピッチ角速度制御の積分ゲイン。
- `PID_PITCH_RATE_Kd`: ピッチ角速度制御の微分ゲイン。

### ヨー角度とヨー角速度制御のPIDパラメータ

- `PID_YAW_RPM_MAX`: ヨー角制御によって生成される最大ヨー角速度（RPM）。
- `PID_YAW_Kp`: ヨー角制御の比例ゲイン。
- `PID_YAW_Ki`: ヨー角制御の積分ゲイン。
- `PID_YAW_Kd`: ヨー角制御の微分ゲイン。
- `PID_YAW_RATE_Kp`: ヨー角速度制御の比例ゲイン。
- `PID_YAW_RATE_Ki`: ヨー角速度制御の積分ゲイン。
- `PID_YAW_RATE_Kd`: ヨー角速度制御の微分ゲイン。

## ラジオコントロール

- `YAW_DELTA_VALUE_DEG`: ラジコンのヨー操作1単位あたりの目標ヨー角の変化量（度）。
- `ALT_DELTA_VALUE_M`: ラジコンの高度操作1単位あたりの目標高度の変化量（m）。
- `ANGLE_CONTROL_ENABLE`: 角度制御を有効にするかどうかのフラグ（1:有効, 0:無効）。
- `ALT_SPD_CONTROL_ENABLE`: 高度速度制御を有効にするかどうかのフラグ（1:有効, 0:無効）。
- `ANGLE_RATE_CONTROL_ENABLE`: 角速度制御を有効にするかどうかのフラグ（1:有効, 0:無効）。

## フリップコントロール

- `FLIP_CONTROL_ENABLE`: フリップ（宙返り）制御を有効にするかどうかのフラグ（1:有効, 0:無効）。
- `FLIP_STICK_CHECK_TIME_SEC`: フリップ操作を検出するためのスティック入力のチェック間隔（秒）。
- `FLIP_STICK_VALUE`: フリップ操作とみなされるスティック入力の閾値。
- `FLIP_TARGET_TIME_SEC`: フリップ動作全体の目標時間（秒）。
- `FLIP_CONSTANT_TIME_SEC`: フリップ中に一定の角速度を維持する時間（秒）。

## 離陸制御モード

- `CTRLMODE_TAKEOFF_IDLE_THROTTLE_RATE`: 離陸待機中のスロットルレート。
- `CTRLMODE_TAKEOFF_TRIGGER_THROTTLE_VALUE`: 離陸を開始するスロットルの閾値。
- `CTRLMODE_TAKEOFF_TRIGGER_HOLD_SEC`: 離陸開始のスロットル閾値を維持する時間（秒）。
- `CTRLMODE_TAKEOFF_ACTION_TARGET_ALTITUDE_M`: 離陸後の目標高度（m）。
- `CTRLMODE_TAKEOFF_ACTION_MAX_SPEED_M_S`: 離陸時の最大上昇速度（m/s）。
- `CTRLMODE_TAKEOFF_COMPLETION_ALTITUDE_ERROR_M`: 離陸完了とみなす高度誤差（m）。
- `CTRLMODE_TAKEOFF_COMPLETION_STABLE_DURATION_SEC`: 離陸完了とみなすための安定維持時間（秒）。
- `CTRLMODE_TAKEOFF_COMPLETION_STABLE_ANGLE_DEG`: 離陸完了とみなすための機体傾斜角度の閾値（度）。

## 着陸制御モード

- `CTRLMODE_LANDING_TRIGGER_ALTITUDE_M`: 着陸モードを開始する高度（m）。
- `CTRLMODE_LANDING_TRIGGER_THROTTLE_VALUE`: 着陸モードを開始するスロットルの閾値。
- `CTRLMODE_LANDING_TRIGGER_HOLD_SEC`: 着陸開始のスロットル閾値を維持する時間（秒）。
- `CTRLMODE_LANDING_ACTION_TARGET_SPEED_M_S`: 着陸時の目標降下速度（m/s）。
- `CTRLMODE_LANDING_COMPLETION_ALTITUDE_M`: 着陸完了とみなす高度（m）。
- `CTRLMODE_LANDING_COMPLETION_STABLE_ANGLE_DEG`: 着陸完了とみなすための機体傾斜角度の閾値（度）。
- `CTRLMODE_LANDING_COMPLETION_STABLE_DURATION_SEC`: 着陸完了とみなすための安定維持時間（秒）。
