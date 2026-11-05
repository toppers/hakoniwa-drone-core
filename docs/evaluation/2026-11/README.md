# 箱庭ドローン PRO

**技術仕様・定量評価・競合技術比較｜改訂第4版**  
**評価日：2026年11月1日（第4版の追加分は2026年11月5日）｜合同会社箱庭ラボ｜技術評価資料（製品保証書ではない）**

> **第4版（v5.0.0、2026-11-05）での注記**：v5.0.0で、センサーモデルv2（本資料の「標準センサー」の行）を
> 無償版（hakoniwa-drone-core）にも含め、**PIL（PX4の実ファームをエミュレータAthrillの上で動かす構成）**を公開した
> （1章、2.3節、3章）。Control Link（CL）、外部センサー（Sensors PRO）、Camera PROは、引き続き別製品・別契約です。
> 参考文献のうち、Drone PRO・Camera PROのリポジトリへのリンクは非公開で、契約者のみ開けます。Athrill関連は公開です。

> **結論**：箱庭ドローン PRO の中心用途は、**機体・センサー・制御・故障条件を指定し、制御／推定が成立する範囲を定量的に検証すること**である。センサー群の追加は、その「検証できる条件」を拡張する技術投資であり、カメラ／LiDARの機能数でGazeboやProject AirSimと競う戦略への転換を意味しない。比較は第Ⅰ部でRflySim・ArduPilot SITL・PX4 SIH・MATLAB/Simulinkとの**制御検証**、第Ⅱ部でGazebo・Project AirSimとの**センサーおよびシミュレーション機能**を扱う。性能値は同一条件の比較だけを横並びにし、実機妥当性とは区別する。[H1][H2][H3][C1][C2]

## 0. 比較の基準・凡例

本書は公開された公式資料、関連リポジトリの実装・試験記録、および2026年10月31日版の製品スペックシートを照合した。**複数のシミュレータ全体を同一機体・同一PC・同一ワールドで実行した総合ベンチマークではない。** 競合の全機能を網羅したものでもない。

| 表記 | 意味 |
|---|---|
| **○** | 指定した製品／構成で公式資料またはソースに実装・提供を確認した機能 |
| **△** | 追加プラグイン、別製品、条件付き実装、利用可能だが今回の連携で未検証 |
| **—** | 指定した範囲の標準機能としては今回確認できない。**技術的な不可能・非対応の断定ではない** |
| **本体** | 箱庭ドローン PRO本体の実装・対応機能。正式リリースとmain実装は区別する |
| **CL / SL** | 別契約のControl Link／Scenario Link。基本ライセンスの標準機能には算入しない |
| **Sensors / Camera** | 別リポジトリのMuJoCo Sensors PRO／Camera PRO。実装とDrone PROへの統合状態を区別する |

**対象バージョン**：Drone PROの正式公開版は**v5.0.0（2026-11-05）**。第3版までの評価はv4.2.0（2026-10-18）と、本資料で参照した開発版mainは`3fc3c958`（2026-11-01）、MuJoCo Sensors PROは`450c2b9`（同日）、Camera PROは`3b1788dc`。競合はGazebo Jetty（gz-sensors 10系）、Project AirSim v1.0.1の公式資料、RflySimの公開マニュアル、PX4・ArduPilot・MathWorksの公式資料を用いる。第3版では、カメラのDrone PRO統合（PR #335）と手順書・PDU定義v2（PR #336）の取り込みを反映した。第4版のPILは、Athrill STM32（`athrill-target-stm32`）v0.2.0候補、Athrill RISC-V（`athrill-target-riscv`）v0.1.0候補、`athrill-device`、比較対象のRenodeはArduPilotの性能改善ブランチ（`fbea4f40`）を用いる。[H1][H4][H5][H9][H10][C1][C2][C3]

---

# 第Ⅰ部　箱庭ドローン PROの技術仕様と「制御検証」の比較

## 1. 位置づけと提供範囲

箱庭の技術的な中心は、①同じ機体・センサー・制御条件で繰り返す、②制御アルゴリズムや外乱を差し替える、③速い代役実行（CL）と対応SITLの出力を比較し、④採否を判断するための**根拠と適用限界**を残すことである。[H2][H3]

| 分類 | 技術仕様 | 提供範囲・注意点 |
|---|---|---|
| 物理 | **MuJoCo 3.16.0**、MJCF/XML、質量・重心・慣性・剛体接触 | 本体。実機物理との一致を証明するものではない |
| 機体・推進 | ローター**1～16基**、位置・回転方向・推力・反トルク係数・ローター慣性 | 幾何・制御配分条件によって安定飛行可否が異なる |
| 時刻 | 固定物理刻み。代表的な実証は**1ms** | 制御周期、センサー周期、通信遅延は別に設定・評価 |
| 標準センサー | 加速度、ジャイロ、地磁気、気圧、GPS | 本体センサーv2。取り付け・遅延・ノイズ・ずれなどを設定 |
| 外部センサー | 距離計、2D／3D LiDAR、深度カメラ、RGBカメラ（Sensors PROのプラグイン） | main実装、ビルドスイッチ`HAKO_ENABLE_EXTERNAL_SENSORS`（既定OFF）。確認はmacOS。無償版v5.0.0には含まれない |
| PX4／ArduPilot | 両方のSITL実行とMAVLink連携 | 本体と構成依存。外部センサーのFC入力まで一律に保証しない |
| PIL（実ファーム） | PX4のボード用ファーム（Pixhawk 4の`px4_fmu-v5_default`、AIFoundry Erbium）をエミュレータAthrillで実行し、共有メモリのPDUでデータの往復ごとに同期 | **v5.0.0で公開**（無償版も）。STM32はボードのチップ（IMU・地磁気・気圧・GPS）を模擬しPX4のドライバがそのまま読む。ArduPilotは起動・チップ検出まで、箱庭での飛行は未確認。実ハードウェアのHILではない |
| 制御差し替え | PX4／ArduPilot系アダプタと独自制御 | **CL：別オプション** |
| PID探索 | hover → angle → altitude → horizontalの4段階 | **CL等**、半自動。完全無人処理・全機体の成功は意味しない |
| 外乱・故障注入 | ローター故障・風等の条件注入 | **SL：別オプション**。最適な復旧制御を自動で保証しない |
| RPM振動 | 実ローター回転数・連続位相・高調波を用いたIMU観測外乱 | **2026-10-31 main実装、実験的**。飛行・実機振幅の全面検証は未完了 |
| IMUフィルタ | Chebyshev II／ButterworthのLPF | main実装・既定OFF、加速度・ジャイロ別設定 |
| 複数機体 | fleet構成・共有時刻・複数機体 | 大規模台数実測は軽量条件で、全機能有効時の上限ではない |
| 外部接続 | C/C++、Python、MAVLink、PDU、RPC | ROS 2は接続形態依存。標準的なROS 2全インタフェースの保証ではない |
| 記録 | CSV、制御・センサー状態ログ。HKBLOG関連はmain実装 | バージョン・ビルド構成によって利用範囲が異なる |
| 対象環境 | macOS Arm、Ubuntu 22.04／24.04、Windows 11等 | 用途によりWSL2／Docker。GPU不要は**ヘッドレス制御計算**の条件 |

製品群の境界を特に強調する。高品質RGB、Optical Flow画像、Scene Flow、SegmentationはCamera PRO側、距離計・LiDAR・深度・RGBの新しいプラグインはSensors PRO側の実装であり、**Drone PRO v4.2.0にすべて標準搭載されたという意味ではない**。[H1][H5][H6]

## 2. 定量実績――制御検証

### 2.1 Control LinkとSITLの閉ループ応答照合

| 指標 | PX4 | ArduPilot |
|---|---:|---:|
| 事前定義した判定項目 | **68** | **72** |
| OK | **63** | **66** |
| 要確認 | **5** | **6** |
| NG | **0** | **0** |
| 反復数 | CL 10回／SITL 10回 | CL 10回／SITL 10回 |
| 物理刻み | **1 ms** | **1 ms** |
| 主制御周期 | **4 ms**（角速度） | **3 ms**（333Hz） |
| 比較機体 | X500相当の試験モデル | X500相当の試験モデル |

PX4の「要確認」は、例えばコマンド応答のばらつきや着陸時間の統計範囲が重ならない等が理由で、**5件とも定義した許容差内**。ArduPilotの6件も同様に許容差内である。NG 0は**対象項目・閾値の範囲内でNGがなかった**という意味で、軌跡の完全一致、実機への妥当性保証、安全認証を示さない。X500やEAMSのモデルは公開資料から推定した試験モデルであり、メーカー公認の実機同定モデルではない。[H2][H3]

### 2.2 時間・再現性の代表例

| 測定項目 | 数値 | 測定条件と解釈 |
|---|---:|---|
| PX4 Control Link飛行 | **126秒相当 → 5.0秒（約25.2倍）** | Apple M2 Pro、macOS、MuJoCo物理1ms、角速度制御4ms、viewerなし、X500シナリオ |
| ArduPilot Control Link飛行 | **183秒相当 → 約7.1秒（約25.8倍）** | 2026-10-31スペックシート記載の代表例。PX4とは別条件 |
| PX4：10シード・5並列 | **約49秒** | 並列試験一式の所要例。単体速度の単純積ではない |
| Control Link記録の再実行 | **13ログファイルのバイト一致** | 特定シナリオ・環境・出力ログに限る。全OS・全機能の決定論保証ではない |
| EAMS：機体値修正〜4段PID調整 | **約30分** | 開発作業例。一般的な平均作業時間ではない。EAMSの機体は、[EAMS E6106FLMPの公開情報](https://www.eams-robo.co.jp/products/e6106flmp/)をもとに箱庭ラボが独自に作ったシミュレーションの機体で、実物と同じであることは保証しない |

競合製品との**飛行全体の速度倍率差は測っていない**。本表の「約25倍」は**実時間との比率**であり、Gazebo・RflySim・ArduPilot SITL・PX4 SIH・MATLABに対する25倍の優位を意味しない。[H2][H3][H7]

### 2.3 PIL――ボード用ファームのままの実行（第4版で追加）

| 測定項目 | 数値 | 測定条件と解釈 |
|---|---:|---|
| PX4（Pixhawk 4用）×箱庭x500の離陸・ホバリング | **3/3回**、2.5m目標に対し**2.48–2.50m** | Apple M2 Pro、macOS、MuJoCo viewerあり・実時間。パラメータ初期化から1回目を含む。v5.0.0と同じコードのPRO版で確認（公開版zipは未確認） |
| PX4（Erbium、RISC-V）×箱庭x500 | **3/3回**、**2.50–2.51m** | 同上 |
| PIL全体の速さ（STM32、ホバリング中） | **RTF 1.48** | 2026-11-04、viewerなし。Athrillは1コアの91%、箱庭は111%。PX4 SIH単体（外部物理なし）は1.94 |
| PX4 SIHの再現性（Athrill単体） | **macOSとLinux x86_64でビット一致**（2,903,884,344命令） | 公開ELFと台本どおりの飛行。SDカード像・ULog・F-RAM・コンソールの全一致。QGroundControl等の実時間入力を含む再現は対象外 |
| ArduPilot（ArduCopter、Pixhawk 4用）の速さ：Renodeとの比較 | Renode **0.30**、Athrill **0.62**（アイドルもそのまま実行）／**1.58**（`b .`をWFI扱い） | 同一ELF・同一Mac。ArduCopterのアイドルは`b .`で、WFIがない。0.62が「ハードウェアの模擬だけ」の比較（約2倍）、1.58はファームを知らない汎用の設定で、そのアイドルの間の時間を飛ばした値（約5倍）。周辺の模擬は両者で違い、作業量を正規化した比較ではない |
| ArduPilotの命令の一致（Renodeとの比較） | Renodeの411,873命令のうち**411,627命令が同期して一致** | 不一致91か所はすべてハードウェアの待ち時間（タイマー割り込みの入りなど） |

PILの位置づけは、**SITL（ホスト向けビルド）とHIL（実ボード）の間**である。ボード用のビルドをそのまま動かし、ドライバ・割り込み・DMAを通る経路を、実ハードウェアなしで繰り返せる。一方で、命令サイクル精度・電気的特性・実ボードの代替は主張しない。[H9][H10][H11]

## 3. 最も近い競合との機能比較――制御検証

比較対象は、**RflySim**、**ArduPilot SITL単体**、**PX4 SIH**、**MATLAB/Simulink＋UAV Toolboxおよび必要なサポートパッケージ**。いずれも「制御系の検証」と直接関係があるが、飛行力学の配置やライセンス・追加製品は異なる。機能の存在と、箱庭と同一形式の定量評価資料の存在は別に判定する。[C1][C2][C3][C4]

| 制御・検証機能 | 箱庭Drone PRO | RflySim | ArduPilot SITL | PX4 SIH | MATLAB＋UAV Toolbox系 |
|---|---|---|---|---|---|
| PX4を含む閉ループ試験 | **○** | **○** | — | **○**（PX4内蔵） | **○**（PX4支援パッケージ） |
| ArduPilotを含む閉ループ試験 | **○** | — 公式の対応の記述なし（SDKにAPM通信の記述あり） | **○** | — | **○**（ArduPilot支援パッケージ） |
| 別の機体物理モデルを指定 | **○** MuJoCo | **○** CopterSim/Simulink | **○** SITLモデル | **△** SIH内部モデルの修正 | **○** Simulink plant |
| 制御ロジックの差し替え | **○ CL** | **○** MBD/PX4 | **△** ArduPilotの変更 | **△** PX4モジュール変更 | **○** Simulink/コード生成 |
| 物理へのモーター故障・風の注入 | **○ SL** | **○** 故障注入系 | **○** SIM_系等 | **△** 追加・モデル変更 | **△** モデル実装／試験設計による |
| センサー異常・GPS喪失試験 | **○** 条件次第 | **○** | **○** | **△** モデル範囲内 | **△** モデル・試験設計による |
| RPM連動のIMU振動モデル | **○ 実験的** | — 方式未確認 | **○** RPM・位相・高調波 | — 今回未確認 | **△** モデル実装に依存 |
| 高速な非実時間実験 | **○ 約25倍の実測例** | **○** 速度の同条件実測なし | **○** `SIM_SPEEDUP` | **○** 軽量・lockstep | **○** 構成依存 |
| 自動／反復試験 | **○** | **○** 自動試験例 | **○** AutoTest等 | **△** PX4のテスト構成依存 | **○** Simulink Test等の構成次第 |
| PIL（エミュレータ上のボード用ファーム） | **○** PX4（Pixhawk 4・Erbium）、ArduPilotは起動まで | — 今回未確認 | — （ホスト向けビルド） | — （SIH-on-hardwareは実ボード） | **△** 実ボード上のPIL（Embedded Coder・対応ハード） |
| HIL・実ハードウェア試験 | — 標準では提供しない（PILは上の行） | **○** Pixhawk HIL | **△** 別のHIL構成 | **○** SIH-on-hardware（HILとは別方式） | **○** 対応パッケージ・ハード必要 |
| 同一シナリオで軽量代役 vs 本物のSITLを定量照合 | **○ CL：68/72項目の記録** | — 同形の標準資料は未確認 | — 別の比較対象を要する | — 別の比較対象を要する | **△** ユーザー構築可能、同形の標準資料未確認 |
| 動かせるOS | **○** macOS（Apple Silicon）・Ubuntu・Windows | Windows（LinuxはWSLの中） | 今回未確認 | 今回未確認 | 今回未確認 |

**選ぶ理由**：機能の有無ではRflySimとの差は小さい。箱庭を選ぶ理由は、①**PX4とArduPilotの両方**を同じ機体・同じ条件で回せること（RflySimの公式の飛行制御はPX4系、ArduPilot SITLとPX4 SIHはそれぞれ自分のFCだけ）、②**macOS・Ubuntu・Windows**で動くこと（RflySimの導入手順はWindows）、③軽量代役と本物のSITLを照合した結果（68／72項目）を**記録として持つ**こと、の3点である。第4版から、④**ボード用ファームのままのPIL**を、実ボードなしに同じ機体・同じ条件で回せること（2.3節）が加わる。[C1][C10][H9]

**読み方**：表中の「○」は機能提供を示すだけで、品質・精度・速度の優劣を示さない。ArduPilot SITLにはSIM_パラメータによる風・GPS異常・振動や`SIM_SPEEDUP`があり、RflySimには故障注入・自動テスト・HILの公式ワークフローがある。PX4 SIHは外部の高品質物理エンジンを使わない軽量設計。MathWorksのSITL／HILは、UAV Toolbox単独で完結せず**Simulink、Embedded Coder、サポートパッケージ等の必要製品が条件によって異なる**。[C1][C2][C3][C4]

### 3.1 Gazebo／Project AirSimも「制御検証の土俵」から見る

| 観点 | Gazebo Jetty | Project AirSim |
|---|---|---|
| PX4 | **○** PX4公式のGazebo連携 | **○** PX4 SITL/HITL、機体に条件あり |
| ArduPilot | **△** ArduPilot公式保守の`ardupilot_gazebo`プラグイン経由 | **△** Project AirSim公式Quad／Hexa SITL例あり、**最新版との動作検証は古い** |
| 故障注入 | **△** 物理プラグイン／PX4側機構等の組合せ | **△** 個別カスタム実装・制御系の機構による |
| 同一機体の軽量代役とSITLの68／72項目形式の照合 | — 本調査で標準成果物は未確認 | — 本調査で標準成果物は未確認 |
| 主な強み | ROS 2・センサー・ロボット資産と豊富な物理／描画プラグイン | Unrealのシーン・カメラ・LiDAR・GIS／機体構成 |

Gazebo ArduPilotの「△」は**ArduPilot側の公式プラグインを追加して使う**という本資料の凡例に合わせたもので、公式性が低いという意味ではない。Project AirSimのArduPilotも**公式実装／手順が存在する**。ただし公式文書自身が「最近のArduPilot最新版との検証はされていない」と断っているため、実運用上の確実性を区別した。[C5][C6][C7]

## 4. RPM連動振動――差別化するなら「モデル境界と検証性」

| 観点 | 箱庭Drone PRO（実験的） | ArduPilot SITL（既存機能） | 解釈 |
|---|---|---|---|
| 回転数の入力 | ローターダイナミクスの**実モデル回転数** | `sitl->state.rpm[motor]` | **両方とも**モーターごとのRPMを用いる。独占的特徴ではない |
| 位相と高調波 | ローターごとの連続位相、1/rev・高調波 | `accel_motor_phase`／`gyro_motor_phase`、選択した高調波 | **両方とも**位相連続と高調波あり |
| 加振先 | FCとは独立した**IMU観測外乱** | ArduPilot SITL内の加速度／ジャイロ観測 | 箱庭は同じ入力条件を異なるFCへ適用する構成を狙える |
| 振幅モデル | RPM依存の経験モデル、パラメータ設定 | 速度・ノイズ・高調波のモデル、`SIM_VIB_*`設定 | **どちらも実機振幅の自動保証ではない** |
| フィルタ・計測連鎖 | 真値＋振動 → IMU LPF → 遅延／標本化／誤差 | ArduPilotのSITLセンサー処理へ内包 | 異なる位置の機構。効果比較には同一条件実験が必要 |
| 実証段階 | 単体・数値試験、飛行レベルは一部保留 | SITLに実装・テスト設定あり | 箱庭の製品差別化としては**未検証事項を明示**する |

**重要な訂正**：ArduPilotを「推力からRPMを推定するだけ」「位相が連続しない」と説明するのは不正確。`AP_InertialSensor_SITL.cpp`の実装はRPM配列・位相積算・高調波を使用している。箱庭の候補優位は「**FCから分離された、交換可能で再現可能な観測外乱源**」にあり、実用上の優位はPX4／ArduPilot両方への同条件注入と受け入れ試験で確認する必要がある。[H8][C8]

---

# 第Ⅱ部　センサーが広げる検証範囲とGazebo／Project AirSimとの比較

## 5. ドローン向けセンサーの実装・統合ステータス

| 機能 | 箱庭側の実装 | Drone PROでの使用状況（2026-11-01） |
|---|---|---|
| IMU（加速度・ジャイロ）／地磁気／気圧／GPS | 本体センサーv2 | **本体実装済み**、MAVLink `HIL_SENSOR`／`HIL_GPS`連携 |
| Rangefinder | Sensors PRO：1本／円錐、ノイズ、分解能 | **PR #334 E1でDrone PRO実飛行結合試験あり**（下向き距離計） |
| 2D／3D LiDAR | Sensors PRO：回転／一括、点時刻、移動歪み | **PR #334 E1で3D LiDAR実飛行結合試験あり**。2DはSensorsの結合試験のみ（Drone PROでの飛行試験は未実施） |
| 深度カメラ | Sensors PRO：ray／render、16bit PNG | **PR #335でDrone PROに統合**。描画の深度を実飛行で確認（中央値0.989 m＝距離計と一致） |
| RGBカメラ | Sensors PRO：MuJoCo描画、JPEG | **PR #335でDrone PROに統合**。表示なし・表示あり（`--mujoco-viewer`）とも実飛行で確認 |
| Optical Flow画像／Scene Flow／Segmentation／BBox等 | **Camera PRO側** | Drone PRO標準機能には算入しない。PX4向けFlow積分・品質・MAVLink連携は別工程 |
| Rangefinder→PX4 | 測距モデルあり | PX4の`DISTANCE_SENSOR`送信経路は未確認 |
| Optical Flow→PX4 | Camera PROに画素の正解値あり | `HIL_OPTICAL_FLOW`送信・EKF2飛行統合は未確認 |

**最新の進捗**：Sensors PROのPR #16は、実FoundationとPythonクライアントを使う統合テスト**35チェック×3回成功**を報告。PR #17はホストViewerとのGLFW共存を修正し**97/97テスト成功**を報告。Drone PROのPR #334は、`HAKO_ENABLE_EXTERNAL_SENSORS`（既定OFF）でRangefinder＋3D LiDARを組み込み、**1mまでの飛行試験を3/3回PASS**、距離計0.97–0.99m、10Hz、1ms刻みの時刻、LiDARScanサービス応答を報告。PR #335はRGB・深度カメラをメインスレッド描画で組み込み、4センサー同時の実飛行を**表示なし8/8・表示あり3/3回PASS**、撮影サービスの応答を報告。表示ありでは進みが約6%遅い。PR #336はPDU定義v2・見本機体・手順書（macOS）を追加し、手順書の命令を順に実行して通ることを確認。いずれもmacOS上の特定条件の報告であり、Windows／Linuxのエンドツーエンド保証ではない。[H4][H5]

## 6. センサー・視覚系の機能比較

凡例：箱庭列の**本体**はDrone PRO、**S**はSensors PRO、**C**はCamera PRO。**S／Cを一括してDrone PRO正式製品の機能とみなさない**。Project AirSimは後継製品（従来Microsoft AirSimは比較列から除外）。Gazeboは**Jetty／gz-sensors系**で、Classicとは区別する。[H5][H6][C5][C6]

### 6.1 計測センサー

| センサー | 箱庭製品群 | Gazebo Jetty | Project AirSim |
|---|---|---|---|
| 加速度・ジャイロ（IMU） | **○ 本体** | **○** | **○** |
| 地磁気 | **○ 本体** | **○** | **○** |
| 気圧 | **○ 本体** | **○** | **○** |
| GPS／GNSS | **○ 本体** | **○ NavSat** | **○** |
| 専用Altimeter | **△** 気圧高度で代用 | **○** | — 確認できず |
| Rangefinder | **○ S／E1飛行試験あり** | **△** レイセンサー／構成で実現 | **○** 構成によりDistance Sensor |
| 2D LiDAR | **○ S** | **○** | **○** |
| 3D多層LiDAR | **○ S／E1飛行試験あり** | **○** | **○** |
| GPU加速LiDAR | — CPU ray中心 | **○** | **○** Unreal側構成 |
| Rosette／Livoxなど特殊走査 | — 未対応 | **△** 拡張・設定次第 | **○** 走査パターン選択 |
| Radar | — 未対応 | — 標準型未確認 | **○** |
| **Airspeed（対気速度）** | — 標準モデル未確認 | **○ `AirSpeedSensor`** | **○** |
| Force/Torque／Contact | **△** MuJoCo状態を利用可 | **○** | **△** 追加構成次第 |

**訂正**：GazeboのAirspeedは`gz-sensors`に標準の`AirSpeedSensor`クラスが存在するため、前版の「△ 外部追加」は誤り。[C9]

### 6.2 画像・認識センサー

| 機能 | 箱庭製品群 | Gazebo Jetty | Project AirSim |
|---|---|---|---|
| RGBカメラ | **○ S／C**（SはDrone PRO mainに統合、macOSで確認） | **○** | **○** |
| Depthカメラ | **○ S／C** ray/render | **○** | **○** |
| RGB-D | **△** 組合せ構成 | **○** | **○** |
| Semantic Segmentation | **○ C**（別製品） | **○** | **△** segmentation画像／ID系 |
| Instance／Panoptic | **△ C** シーン制約あり | **○** | **△** object ID等の構成 |
| Surface Normals | **○ C** | — 標準確認できず | **○** |
| Optical Flow画像 | **○ C**（PX4送信は未統合） | — 標準確認できず | — 標準capture未確認 |
| Scene Flow（画素ごとの3D速度） | **○ C** | — 標準確認できず | — 標準確認できず |
| 2D／3D Bounding Box | **○ C** | **○** | **○** |
| Thermal Camera | — | **○** | — 標準確認できず |
| 魚眼・レンズ歪み | **○ C** | **○** | **△** 対応方式別確認が必要 |
| 露出・逆光・雨滴等 | **○ C** 項目ごとに検証段階あり | **△** 描画構成依存 | **○** Unreal後処理構成 |

箱庭Camera PROにはOptical Flow、Scene Flow、Surface Normals、Semantic Segmentation、BBox等の独立検証記録がある。一方で、Windows GPU環境での実時間性能など一部項目は未達または未検証である。**研究実装・受け入れ試験・標準統合・実機妥当性を混同しない。**[H6]

## 7. センサーv2の独立ベンチマーク――意味のある数値を優先

2026-11-01の評価では、**箱庭センサーv2、Gazebo `gz-sensors 10.2.0`、Project AirSimオリジナル`core_sim`**に同じ真値を流し、macOS arm64で比較した。物理刻み1ms、5センサー（加速度・ジャイロ・地磁気・気圧・GPS）の合計計算時間。これらは**S／CのLiDAR・画像性能ではなく、Drone PRO標準センサーv2の測定**。[H7]

| 1物理ステップあたり：誤差あり | 箱庭 | Gazebo | Project AirSim core_sim |
|---|---:|---:|---:|
| **中央値** | **0.125 µs** | **0.125 µs** | **0.083 µs** |
| **p99** | **0.75 µs** | **9.4 µs** | **12.7 µs** |
| **平均** | **0.183 µs** | **0.774 µs** | **0.787 µs** |
| 物理刻み1msに対する平均時間 | 0.0183% | 0.0774% | 0.0787% |

中央値は箱庭とGazeboが同じで、3者とも計算時間の絶対値は1ms刻みの0.1%未満。平均の「4.23倍／4.30倍」は**実用的な飛行性能の優劣として強調しない**。**p99の観測差**（0.75µs対9.4／12.7µs）は更新刻み付近の処理時間の尾を示すが、**OS／ホスト／センサー構成全体のジッタ保証ではない**。センサーの計算はプロセス／アダプターの測定形態にも依存する。条件を揃えたエンドツーエンド性能検証は別途必要。[H7]

| 同じ真値を与える独立評価 | 実測・観察 | 注意 |
|---|---|---|
| ノイズなし・ジャイロ | 箱庭 vs Gazebo **差0** | 代表20秒・250Hzの条件 |
| ノイズなし・加速度 | 最大差 **3.6×10⁻¹⁵m/s²** | 丸め差相当 |
| 大気圧（0–3000m） | 箱庭・GazeboともUS 1976式と**差0Pa** | 参照式への整合であり実測大気の一致ではない |
| GPS：10km | 箱庭とGazeboで水平**9.6m**差 | 地球曲率への写像方式が違うため、直ちにバグではない |
| 誤差統計 | 箱庭 **21特性試験すべて設定内** | 事前設定の観測量と許容域での判定 |
| 再現性（同じ条件の5場面） | 箱庭 **5/5**、AirSim **5/5** | Gazeboは共有乱数系列の消費順・リセット挙動に依存。設計特性であり製品全体の欠陥とは断定しない |
| センサーv2のテスト設計証跡 | **216／239（約90%）** | 主にSITL・飛行系の残り23行は証跡未登録、即座に「NG」ではない |

### 7.1 再現性に関する中立的な表現

Gazeboでは本比較アダプターが`gz::math::Rand`の**プロセス共有乱数系列**を利用するため、他センサーの呼び出し順・スレッド並行実行・reset条件によってサンプル列が変わった。一方、箱庭はセンサーごと・特性ごとに系列を分け、Project AirSimのcore_simはインスタンスごとに固定種を使う。**比較したのは指定したアダプター・5場面であり、Gazeboの全利用形態が非決定的であるという主張ではない。**[H7]

---

# 第Ⅲ部　評価の限界・導入判断・付録

## 8. 評価の限界を分ける

| 観点 | 証明できること | 証明しないこと |
|---|---|---|
| Verification（仕様準拠） | 独立した式・期待値・テストへの一致 | 実世界の挙動そのもの |
| Integration（統合） | 特定OS・機体・FC・PDUでの結合動作 | 全OS・全センサー・全FC組合せ |
| Validation（現実妥当性） | 実測のある条件でのモデル誤差・妥当域 | データ未取得の故障・天候・機体一般への外挿 |
| Performance（性能） | 試験環境での平均・p99・RTF・処理時間 | 別マシン・別センサー構成の性能保証 |
| Competitive Evidence（競合） | 公式提供の有無、同じ条件の比較結果 | 同一条件で測っていない製品間の性能・精度順位 |

**適用上の注意**：本資料は安全認証、耐故障性の製品保証、実機一致の証明ではない。箱庭の独自性を主張する際には「その結果をどの条件で再現できるか」を示す。[H2][H3][H7]

## 9. 今後の検証・製品化の優先順位

| 優先 | 検証課題 | 受け入れ証拠の例 |
|---|---|---|
| A | 外部センサーのmacOS以外での結合とSITL併用 | Ubuntu／WSL2（ray系センサー）・Windowsの実飛行、PX4／ArduPilot SITLと同時の時刻・停止 |
| A | PX4光学フロー位置保持 | `DISTANCE_SENSOR`＋`HIL_OPTICAL_FLOW`、ジャイロ積分・品質・時刻、GPSなしEKF2実飛行 |
| A | RPM振動のFC独立性を証明 | 同一RPM・振動シード・モデルをPX4／ArduPilotへ適用、観測スペクトル・EKF・制御差を記録 |
| A | ArduPilotのPIL飛行 | Athrill STM32上のArduCopterで箱庭x500の離陸・ホバリング、繰り返し3回以上 |
| A | 多センサー飛行の1msリアルタイム性 | Rangefinder／3D LiDAR／RGB／Depth同時、平均・p99・最大・RTF・取りこぼし、機体数別 |
| B | 競合との同条件ベンチマーク | 同一機体・同一物理相当・シナリオ・CPU・測定対象・ウォームアップ時間を固定した比較 |
| B | 外部センサーのOS・配布評価 | Windows／Linux/macOS、DLL/so/dylib ABI、サービス再起動、異常時復旧 |
| B | センサーv2未登録23試験 | SITL／飛行条件のテスト結果・ログ・判定閾値・未実施理由を追跡 |
| C | 追加センサーの機会評価 | Airspeed・Radar・特殊走査LiDAR等をユースケースと実機要求に基づき選別 |

## 付録A　「18特性」の全内訳――比較軸が恣意的に見えないよう公開

この18項目は**箱庭がセンサー誤差・設定表現力を調べるために定義した軸**であり、競合のセンサー種類・総合性能スコアではない。「条件付」は実現できる範囲に条件があるという意味で、単純に×と同じに扱わない。詳細な判定条件は元資料を参照。[H7]

| # | センサー特性 | 箱庭 | Gazebo | Project AirSim core_sim |
|---:|---|:---:|:---:|:---:|
| 1 | 5センサーのノイズ | ○ | ○ | △ |
| 2 | 固定のずれ（バイアス） | ○ | △ | △ |
| 3 | 起動時に抽選するずれ | ○ | ○ | △ |
| 4 | IMUの時間変動バイアス | ○ | ○ | △ |
| 5 | 地磁気・気圧・GPSの時間変動バイアス | ○ | × | △ |
| 6 | 分解能 | ○ | △ | × |
| 7 | センサー別の更新周期 | ○ | ○ | ○ |
| 8 | ジャイロと加速度で別周期 | ○ | × | × |
| 9 | センサー値の遅延 | ○ | × | × |
| 10 | 測定範囲の飽和 | ○ | × | × |
| 11 | 感度誤差・軸干渉 | ○ | × | △ |
| 12 | IMUのフィルタ | ○ | × | × |
| 13 | 地磁気の硬鉄・軟鉄効果 | ○ | × | × |
| 14 | 気象条件（海面気圧・気温） | ○ | × | × |
| 15 | 気温・気圧高度出力 | ○ | × | △ |
| 16 | GPS受信機報告値（精度／衛星数／進行方向） | ○ | × | △ |
| 17 | GPS水平位置ノイズをmで指定 | ○ | × | × |
| 18 | 加速度の自動操縦較正値 | ○ | × | × |

**集計**：箱庭○18／18、Gazebo○4＋△2＋×12、Project AirSim○1＋△8＋×9。**元の概要ページには「Project AirSim：条件付き9」とあったが、詳細18行を数えると△8だった。本書では詳細表の内訳を採用し、元の概要ページも8に訂正した。** **ここから「箱庭の全センサー機能が競合より上」と結論づけない。** Gazeboが標準で持つAirspeed、Thermal、Panoptic Segmentation、Force/Torque、GPU LiDAR等はこの18項目の対象外。単体ノイズ実装についての実測比較であり、ロボットワールド・FC連携の優劣とは別問題。[H7][C5][C9]

## 付録B　改訂履歴

### 第4版（第3版からの変更、2026-11-05）

| 変更 | 改訂内容 |
|---|---|
| 対象版 | 正式公開版をv5.0.0に。センサーモデルv2が無償版にも入ったことを冒頭に |
| PIL | 1章に「PIL（実ファーム）」の行、2.3節（離陸3/3回、RTF、SIHのビット一致、Renodeとの速度・命令一致）、3章の比較表にPILの行と「選ぶ理由」④ |
| 優先順位 | ArduPilotのPIL飛行を追加 |

### 第3版（第2版からの変更）

| 変更 | 改訂内容 |
|---|---|
| カメラ統合 | Drone PRO PR #335（RGB・深度）、#336（PDU定義v2・手順書）を反映 |
| 制御検証の比較 | 「選ぶ理由」と動かせるOSの行を追加。RflySimのArduPilotを公式資料で確認（公式の対応の記述なし） |
| 自社欄の表現 | HILを「標準では提供しない」と言い切りに |
| 元資料の訂正 | センサーv2の概要ページの「条件付き9」を8に訂正 |
| 表記 | 「製品保証書」、付録Aの太字記号の崩れを修正 |

### 第2版（第1版からの変更）

| 変更 | 改訂内容 |
|---|---|
| 主戦場を再定義 | 制御検証の比較を第Ⅰ部へ。RflySim／ArduPilot SITL／PX4 SIH／MATLABを追加 |
| 比較列を整理 | Microsoft AirSimを主要表から除外。Gazebo／Project AirSimは第Ⅱ部中心 |
| Airspeed・ArduPilot連携 | Gazebo Airspeedを**○**へ、Gazebo ArduPilotを**△（公式外部プラグイン）**へ修正 |
| Project AirSim ArduPilot | 公式実装は存在するが**最新版の検証は古い**と明記、△へ調整 |
| RPM振動 | ArduPilotも**モーター別RPM・連続位相・高調波**を実装していると訂正 |
| 定量指標 | 18全項目を付録化、平均倍率を抑え中央値・p99と実用上の絶対値を掲載 |
| 再現性の表現 | Gazebo共有乱数系列の挙動として中立的に説明 |
| 統合ステータス更新 | Drone PRO PR #334のRangefinder／3D LiDAR飛行試験3/3成功を反映 |

## 根拠資料（リポジトリ・公式資料）

各文中の `[H*]`、`[C*]` は下記に対応する。リンクは確認した一次資料または公式文書を優先した。

### 箱庭側：製品・仕様・試験

- **[H1]** [箱庭ドローン PRO v4.2.0](https://github.com/hakoniwalab/hakoniwa-drone-pro/releases/tag/v4.2.0)／2026-10-31版製品スペックシート（参考資料）。
- **[H2]** [PX4 Control Link vs SITL：X500の68項目照合](https://github.com/hakoniwalab/hakoniwa-drone-pro/blob/main/pro-docs/control-link/px4/x500-sitl-equivalence-20261011.md)。
- **[H3]** [ArduPilot Control Link vs SITL：X500の72項目照合](https://github.com/hakoniwalab/hakoniwa-drone-pro/blob/main/pro-docs/control-link/ardupilot/x500-sitl-equivalence-20261012.md)。
- **[H4]** [Drone PRO PR #334：外部センサーE1（距離計＋LiDAR実飛行試験）](https://github.com/hakoniwalab/hakoniwa-drone-pro/pull/334)、[PR #335：E2（カメラ）](https://github.com/hakoniwalab/hakoniwa-drone-pro/pull/335)、[PR #336：E3（PDU定義v2・手順書）](https://github.com/hakoniwalab/hakoniwa-drone-pro/pull/336)、[PR #331：設計](https://github.com/hakoniwalab/hakoniwa-drone-pro/pull/331)、[PR #332：レビュー対応](https://github.com/hakoniwalab/hakoniwa-drone-pro/pull/332)。
- **[H5]** [MuJoCo Sensors PRO PR #16：Foundation結合試験](https://github.com/hakoniwalab/hakoniwa-mujoco-sensors-pro/pull/16)、[PR #17：GLFW共存](https://github.com/hakoniwalab/hakoniwa-mujoco-sensors-pro/pull/17)、[PR #15：PDUサービス](https://github.com/hakoniwalab/hakoniwa-mujoco-sensors-pro/pull/15)、[PR #18：停止時のサービス](https://github.com/hakoniwalab/hakoniwa-mujoco-sensors-pro/pull/18)、[PR #19：PDU定義の道具](https://github.com/hakoniwalab/hakoniwa-mujoco-sensors-pro/pull/19)。
- **[H6]** [Camera PRO：センサー実装状況](https://github.com/tmori/hakoniwa-camera-pro/blob/main/sensors/STATUS.md)。
- **[H7]** [センサーv2：6軸結果](https://github.com/hakoniwalab/hakoniwa-drone-pro/blob/main/sensors/docs/results/README.md)、[軸2：18項目全内訳](https://github.com/hakoniwalab/hakoniwa-drone-pro/blob/main/sensors/docs/results/axis2-coverage.md)、[軸4：速度（中央値／p99）](https://github.com/hakoniwalab/hakoniwa-drone-pro/blob/main/sensors/docs/results/axis4-speed.md)、[軸3：再現性](https://github.com/hakoniwalab/hakoniwa-drone-pro/blob/main/sensors/docs/results/axis3-repeatability.md)、[試験証跡216／239](https://github.com/hakoniwalab/hakoniwa-drone-pro/blob/main/pro-docs/sensor-v2/test-tally.md)。
- **[H8]** [RPM連動IMU振動の設計／実装状況](https://github.com/hakoniwalab/hakoniwa-drone-pro/blob/main/pro-docs/sensor-vibration/propeller-vibration-design.md)。
- **[H9]** Athrill STM32（公開）：[箱庭との接続（PIL）](https://github.com/hakoniwalab/athrill-target-stm32/blob/main/docs/hakoniwa.md)、[SIHの再現性の検証](https://github.com/hakoniwalab/athrill-target-stm32/blob/main/docs/verification.md)、[ArduPilotとRenodeの比較](https://github.com/hakoniwalab/athrill-target-stm32/blob/main/docs/ardupilot.md)、[時間の設計](https://github.com/hakoniwalab/athrill-target-stm32/blob/main/docs/time-skip.md)。
- **[H10]** Athrill RISC-V（公開）：[PX4（Erbium）と箱庭](https://github.com/hakoniwalab/athrill-target-riscv/blob/main/docs/hakoniwa.md)。
- **[H11]** [athrill-device（公開）：箱庭のセンサーデバイス](https://github.com/hakoniwalab/athrill-device)。

### 競合側：公式資料・実装

- **[C1]** [RflySim公式：開発ツールチェーン全体像](https://rflysim.com/doc/en/1.Start/overview.html)、[故障注入と自動試験例](https://rflysim.com/doc/en/7/CoreExp.html)。
- **[C2]** [ArduPilot公式：SITLのシミュレーションパラメータ、異常・風・振動・SIM_SPEEDUP](https://ardupilot.org/dev/docs/SITL_simulation_parameters.html)。
- **[C3]** [PX4公式：SIH（軽量ヘッドレス、内蔵センサー、対象機体）](https://docs.px4.io/main/en/sim_sih/)。
- **[C4]** [MathWorks：UAV Toolbox](https://www.mathworks.com/help/uav/)、[PX4＋Simulink plant SITL](https://www.mathworks.com/help/uav/px4/ref/simulator-plant-model-example.html)、[ArduPilot SITL](https://www.mathworks.com/help/uav/ardupilot/ug/sitl-simulation.html)。
- **[C5]** [Gazebo Jetty：センサー](https://gazebosim.org/docs/jetty/sensors/)、[Gazebo Sensors library](https://gazebosim.org/libs/sensors/)。
- **[C6]** [Project AirSim：Controller一覧](https://github.com/iamaisim/ProjectAirSim/blob/main/docs/controllers/controllers.md)、[LiDAR](https://github.com/iamaisim/ProjectAirSim/blob/main/docs/sensors/lidar.md)。
- **[C7]** [Project AirSim公式：ArduPilot SITLのQuad／Hexaと互換性注意](https://github.com/iamaisim/ProjectAirSim/blob/v1.0.1/docs/controllers/ardupilot.md)、[ArduPilot公式保守のGazeboプラグイン](https://github.com/ArduPilot/ardupilot_gazebo)。
- **[C8]** [ArduPilot：RPM・位相・高調波に基づくIMU振動の実装](https://github.com/ArduPilot/ardupilot/blob/master/libraries/AP_InertialSensor/AP_InertialSensor_SITL.cpp)。
- **[C9]** [Gazebo Sensors API：AirSpeedSensor](https://gazebosim.org/api/sensors/10/AirSpeedSensor_8hh_source.html)。
- **[C10]** [RflySim公式：インストール（Windows）](https://rflysim.com/doc/en/1.Start/install.html)、[WinWSL](https://rflysim.com/doc/en/3.Soft/winwsl.html)、[対応フライトコントローラ（PX4系）](https://rflysim.com/doc/en/5.HW/b2-fcu/index.html)。

---

*技術評価注記：出典が付いていても、外部資料に記された検証例を本レポート執筆者がすべて再実行したわけではない。特定機体・条件・ソフトウェア版に関する結果を、一般的な適合性、耐故障性、実機の精度保証に拡張しない。契約対象・OS・ビルド設定・依存製品の違いに注意する。*
