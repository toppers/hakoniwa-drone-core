# 衝突のAPI

## 概要
ドローン同士の衝突、ドローンと固定壁の衝突、ARにおけるドローンと手の接触、などによって、速度や角速度がどのように変化するのかを計算するためのAPIです。

## 関数

`impulse_by_collision`

衝突による力積(impulse)を計算します。座標系は単一の座標系です。ただし、すべてのベクトルを自分の機体座標系 body_frame を利用した方がよいでしょう。すべてのこの座標系に変換して利用します。この関数によって、速度の変化と角速度の変化を計算することができます。力積は力と時間の積であり、この量 $J$ を時間を分割して、数回にわたって徐々に速度に加算することもできますし、一回の更新で、どん、と速度を更新することもできます。

$$
\int_0^T Fdt = J \quad \text{（$J$は力積 - $T$は接触時間）}
$$

実際には、場合に応じて、以下を呼んで速度と角速度を更新します。

- `delta_velocity_by_collision` ... 前後の速度変化量（ $v' = v + \Delta_v$ 、速度に直接足す）
- `acceleration_by_collision` ... 加速度( $\dot{v} , 時間積分して速度に。)
- `acceleration_by_force` ... 加速度( $\dot{v} , 時間積分して速度に。一般的に collision 以外にも使える)
- `force_by_collision` ... 掛かった力
- `delta_angular_velocity_by_collision` ... 前後の角速度変化
- `angular_acceleration_by_collision` ...　各加速度
- `angular_acceleration_by_torque` ...　各加速度（一般的に、collision 以外にも使える）
- `torque_by_collision` ... 掛かったトルク


## 方針

これまでの `velocity_after_contact_with_wall` と違って、衝突後の速度を与えるのでなく、
力積（力やトルク）を求めることで、衝突による加速度と角加速度を計算します。これによって、
加速度センサーやジャイロとも連携できるようになります。

また、contact_vector == normal_vector の場合、角速度の変化はなく、`velocity_after_contact_with_wall` と同じ結果を得ることができます。

## 使い方

```cpp
ImpulseType impulse = impulse_by_collision(...);

// 速度の変化の扱い
// やり方(1) 現在の衝突ロジックの場所で速度を変える
VelocityType delta_v = delta_velocity_from_impulse(...,impulse,...);
v_after = v_current + delta_v;

// やり方(2) 加速に追加して積分器に入れる
AccelerationType dv = acceleration_in_body_frame(...);
dv += acceleration_from_impulse(impulse,mass, delta_time); // 衝突による加速度(一気に加速)
v += delta_t * dv; // 速度の更新（積分器に入れる）

// 角速度の変化の扱い
// やり方(1) 現在の衝突ロジックの場所で角速度を変える
delta_w = delta_angular_velocity_from_impulse(impulse, r1, {Ix, Iy, Iz});
w_after = w_current + delta_w;

// やり方(2) 加速に追加して積分器に入れる
AngularAccelerationType dw = angular_acceleration_in_body_frame(...);
dw += angular_acceleration_by_impulse(...,impulse,...); // 衝突による角加速度
w += delta_t * dw; // 角速度の更新（積分器に入れる）
```

## 引数
```cpp
ImpulseType impulse_by_collision(/* coordicates are ALL in one (self body) frame */
    const VelocityType& v1, /* self velocity in self body frame */
    const AngularVelocityType& w1, /* self angular velocity in self body frame */
    const VelocityType& v2, /* other velocity in self body frame */
    const AngularVelocityType& w2, /* other angular velocity in self body frame */
    const VectorType& r1, /* self contact vector, from self center to contact = contact_point - center_point in body frame */
    const VectorType& r2, /* vector from other center to contact = contact_point - other_center_point in body frame */
    double m1, /* self mass */
    double m2, /* other mass */
    const InertiaDiagType& I1, /* diagonal elements of the inertia tensor of the self */
    const InertiaDiagType& I2, /* diagonal elements of the inertia tensor of the other */
    const VectorType& normal, /* normal vector of the contact surface (n and -n give the same result, don't care the +/- direction) */
    double e /* restitution_coefficient 0.0-1.0*/) ;
```

#### NOTE
other_mass, other_inertia == Inf 的なバージョンで、引数を減らしたものも作る（相手が不動の場合）。現在（`velocity_after_contact_with_wall`）を再現するには、このバージョンを使い、normal_vector == contact_vector とする。


## 数学

衝突の物理シミュレーションについて、接触時間中の力学を考慮したモデルを立てます。まず、基本となる変数を定義します。図は2剛体の一般的なモデルとよりシンプルに一方が圧倒的に大きな質量と慣性モーメントを持っている場合（衝突に動じない）です。ここでは、一般的に話を進め、シンプルなモデルでの式も最後に示します。

![collision](collision.png)

- $m_1, m_2$ : それぞれの剛体の質量
- $I_1, I_2$ : それぞれの慣性モーメント（衝突位置中心）
- $v_1, v_2$ : 衝突前の並進速度ベクトル
- $\omega_1, \omega_2$ : 衝突前の角速度ベクトル
- $v'_1, v'_2$ : 衝突後の並進速度ベクトル
- $\omega'_1, \omega'_2$ : 衝突後の角速度ベクトル
- $r_1, r_2$ : 重心から接触点までのベクトル
- $F$ : 接触位置での力ベクトル
- $n$ : 接触面の法線ベクトル
- $e$ : 反発係数

摩擦は無視して力を法線方向のみとし、接触位置での力（作用・反作用）から、

$$
F = f(t) n,   \quad \text{ $f(t)$ は時間変化するスカラー関数}
$$

を仮定して、以下の式を立てます。

1. 接触位置の力による並進運動方程式：

$$
\begin{array}{rl}
m_1\dot{v_1} &= F \\
m_2\dot{v_2} &= -F \\
\end{array}
$$

2. 接触位置の力による回転運動方程式：

$$
\begin{array}{ll}
I_1\dot{\omega_1} = r_1 \times F \\
I_2\dot{\omega_2} = r_2 \times (-F)
\end{array}
$$

（参考：この4式は、運動量保存則と角運動量保存則と同値です。上2式を足し合わせて $J$ を消せば運動量保存。下に2式を接触位置における慣性モーメントに変換して足し合わせれば角運動量保存）

3. 接触点での相対速度：

$$
v_{rel} = (v_1 + \omega_1 \times r_1) - (v_2 + \omega_2 \times r_2)
$$

4. 衝突による力積を考慮すると：

$$
\int_0^T Fdt = J \quad \text{（$J$は力積 - $T$は接触時間）}
$$

5. 反発係数の定義より：

$$
v_{rel}' \cdot n = -e(v_{rel} \cdot n)
$$

ここで $v_{rel}$ は相対ベクトル、 $n$ は接触面の法線ベクトル、 $'$ （ダッシュ）は衝突後を表します。

これらの式を連立して解くことで、衝突後の運動を求めることができます。具体的な解き方としては、$T$ 後に完全に衝突が終了するとして、(1),(2) を時間積分します。 左辺は運動量と角運動量（速度と角速度）の前後差になり、右辺は $J$ の式になります。これを使って、反発の式(5)から $J$ について立式すると、 $J$ が解ける形になります。最後に、それを使って、(1),(2) から衝突後の運動量変化と角運動量変化を計算します。やってみましょう。

$$
\begin{array}{ll}
v_1' &= v_1 + J/m_1 \\
v_2' &= v_2 - J/m_2 \\
\omega_1' &= \omega_1 + I_1^{-1}(r_1 \times J) \\
\omega_2' &= \omega_2 - I_2^{-1}(r_2 \times J)
\end{array}
$$

これらの式を式(3)に代入し、

$$
\begin{array}{ll}
v_{rel}' &= (v_1' + \omega_1' \times r_1) - (v_2' + \omega_2' \times r_2) \\
 &= (v_1 + J/m_1 + \omega_1 \times r_1 + I_1^{-1}(r_1 \times J) \times r_1) - (v_2 - J/m_2 + \omega_2 \times r_2 - I_2^{-1}(r_2 \times J) \times r_2) \\
 &= v_{rel} + (1/m_1 + 1/m_2)J + I_1^{-1}(r_1 \times J) \times r_1 + I_2^{-1}(r_2 \times J) \times r_2
\end{array}
$$

これを、反発の式(5)に代入て解くことで、$J$ を求めることができます。
$j_n = J \cdot n$ すなわち $J = j_n n$ ( $J$ は法線方向のみ、摩擦なし)として、

$$
   j_n = -(1+e) (v_{rel} \cdot n)/ \left( \frac{1}{m_1} + \frac{1}{m_2} +
   (r_1 \times n) \cdot I_1^{-1} (r_1 \times n) + (r_2 \times n) \cdot I_2^{-1} (r_2 \times n) \right)
$$

これで、 $J$ が求まりました。これを元に、速度と角速度の変化量を求めることができます。

$m_2, I_2$ が非常に大きい場合、この式は以下に簡略化されます。

$$
   j_n = -(1+e) (v_{rel} \cdot n)/ \left( \frac{1}{m_1} +
   (r_1 \times n) \cdot I_1^{-1} (r_1 \times n) \right)
$$

## 移動体の速度や角速度への反映方法
この計算で求まるのは力積です。ここから、速度変化として $J/m$ を衝突前の速度に加算することで、衝突後の速度が求まります。角速度については、$I^{-1}(r \times J)$ を加算します。

上記は、一瞬で速度・加速度が変化するモデルです。衝突中の運動を追跡したい場合には、 $F(t), (0 \le t \le T)$ をデザインします。この関数は、剛体表面のバネ係数なども関係します。そして、$\int^T_0 F(t) dt = J$ となるように $F(t)$ と接触時間 $T$ を決め、その間、速度・加速度変化を与え続けます。

## まとめ

二つの剛体の衝突による速度・角速度変化について定式化し、解を求めました。

この物理学的考察は、claude と chat GPT o1 mini によってヒントを得て、手計算と整合させました。

- Chat GPT o1 mini による考察
https://chatgpt.com/share/6789c6a0-5d4c-8002-bc1e-e54169e4fdf4







