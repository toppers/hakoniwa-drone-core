
# A. シミュレーションコア性能

## 物理エンジンの種類と精度 (空気抵抗、地面効果など)

| シミュレータ | 評価 | 理由 | 根拠URL |
| :--- | :---: | :--- | :--- |
| Gazebo | Ο | 標準でDARTを採用し、ODE, Bullet, Simbody等複数のエンジンを切替可能。目的に応じ最適なエンジンを選択できる。 | [-](https://gazebosim.org/libs/physics) |
| AirSim | Δ | Unreal Engineベースの独自物理エンジン (Fast Physics)を搭載。高速だが、高精度な物理再現には外部連携を想定。 | [-](https://microsoft.github.io/AirSim/physics/) |
| Pegasus | Ο | NVIDIA社の高性能物理エンジン「PhysX 5」を搭載。GPUアクセラレーションにより、複雑でリアルな物理演算を高速に実行。 | [-](https://pegasussimulator.github.io/PegasusSimulator/) |
| 箱庭 | Ο | MuJoCo等の外部物理エンジンと連携するハブとして機能。用途に応じ高精度なエンジンを組み込めるアーキテクチャ。デフォルトでは、数式ベースでの物理モデルが利用可能。また、MuJoCo による剛体シミュレーションに、独自実装のローターダイナミクス&バッテリーモデルをカップリングも可能。 | [-](https://hakoniwa-lab.net/products/drone-license/) |

## 物理エンジンの拡張性 (MuJoCo, Matlab連携など)

| シミュレータ | 評価 | 理由 | 根拠URL |
| :--- | :---: | :--- | :--- |
| Gazebo | Ο | Gazebo Pluginを介して物理演算の各要素(力、接触など)をカスタマイズ可能。外部エンジンとの連携実績は限定的。 |  |
| AirSim | X | 独自の物理エンジンに強く依存しており、MuJoCo等の外部物理エンジンを直接連携させる公式な仕組みは提供されていない。 | |
| Pegasus | X | NVIDIA PhysXで完結したエコシステム。外部物理エンジンとの直接連携は想定されておらず、サポートされていない。 | |
| 箱庭 | Ο | コアコンセプトが外部コンポーネント連携であり、PDUを介してMuJoCo等の外部物理エンジンを柔軟に接続可能。 | [-](https://github.com/toppers/hakoniwa-drone-core) |

## 機体特性の拡張性(重量、推力、バッテリー消費など)

| シミュレータ | 評価 | 理由 | 根拠URL |
| :--- | :---: | :--- | :--- |
| Gazebo | Ο | SDFファイル内で質量、慣性、モーター推力、バッテリー消費(LinearBatteryPlugin)などを詳細に定義可能。 | [-](http://sdformat.org/spec) |
| AirSim | Ο | settings.jsonファイルを通じて、機体の物理特性(モーター推力など)や搭載センサーを柔軟に設定・変更できる。 | [-](https://microsoft.github.io/AirSim/settings/) |
| Pegasus | Ο | USDファイル形式でロボットの物理特性(剛体、関節、材質など)を詳細に記述し、シミュレーションに反映させることが可能。 | |
| 箱庭 | Ο | アセットとして機体モデルを定義し、そのパラメータ(重量、推力など)を外部の物理エンジンに渡して計算させる構成。 | [-](https://github.com/toppers/hakoniwa-drone-core) |

## 標準センサーの種類と精度 (カメラ, IMU, LiDAR)

| シミュレータ | 評価 | 理由 | 根拠URL |
| :--- | :---: | :--- | :--- |
| Gazebo | Ο | カメラ、IMU、LIDAR、GPSなど多様なセンサーを標準提供。プラグインによる拡張も容易で、多くの研究で利用実績がある。 | [-](https://gazebosim.org/docs/garden/sensors) |
| AirSim | Ο | カメラ、IMU、LIDAR等、ドローンや自動車に必要な基本センサーをサポート。特にUEベースのカメラ映像のリアルさに定評。 | [-](https://microsoft.github.io/AirSim/sensors/) |
| Pegasus | Ο | RTX Lidarなど物理特性を忠実に再現する高性能センサーをシミュレート可能。現実との誤差を最小限に抑えた開発を実現。 | |
| 箱庭 | Ο | 物理モデルと連携し、基本的なセンサー情報をシミュレート。アーキテクチャの柔軟性を活かし独自のセンサーモデルを組込可能。カメラ/IMUに加え、LiDAR (AirSim と同機能) プラグインを公式公開済み。PDU 経由で本体と即接続できる。 | [-](https://github.com/toppers/hakoniwa-drone-core) |

## カスタムセンサーの拡張性

| シミュレータ | 評価 | 理由 | 根拠URL |
| :--- | :---: | :--- | :--- |
| Gazebo | Ο | センサープラグインの仕組みが提供されており、C++で独自のセンサーモデルを開発し、シミュレーションに追加することが可能。 | [-](https://gazebosim.org/docs/garden/sensors#custom-sensors) |
| AirSim | Δ | 公式なカスタムセンサーAPIはなく、Unreal EngineのエディタでC++やブループリントを用いて独自に実装する必要がある。 | [-](https://microsoft.github.io/AirSim/sensors/) |
| Pegasus | Δ | Python APIやOmniverse Kit拡張機能を用いて独自のセンサーを開発可能だが、Gazeboのプラグインほど手軽ではない。 | |
| 箱庭 | Ο | シミュレーション・ハブのアーキテクチャに基づき、ユーザーが開発したカスタムセンサーモデルを独立したPDUとして接続可能。 | [-](https://github.com/toppers/hakoniwa-drone-core) |

## 3D環境の再現度と拡張性 (自作・編集の自由度)

| シミュレータ | 評価 | 理由 | 根拠URL |
| :--- | :---: | :--- | :--- |
| Gazebo | Δ | Building EditorなどのGUIツールで環境を自作可能だが、フォトリアリスティックな表現力は専門ツールに劣る。 |  |
| AirSim | Ο | Unreal Engineのエディタをフル活用でき、マーケットプレイスの豊富なアセットを用いて高品質な3D環境を自由に構築可能。 | [-](https://microsoft.github.io/AirSim/unreal_custenv/) |
| Pegasus | Ο | USD形式で作成・インポートした高品質な3Dシーンを扱える。NVIDIA Omniverse プラットフォームの描画力を最大限に活用。 | |
| 箱庭 | Ο | 描画をUnity/Unreal Engineなどの外部ゲームエンジンに委ねる構成。これにより、各エンジンの持つ高度な描画能力と拡張性を活用できる。 | [-](https://github.com/toppers/hakoniwa-drone-core) |

## 外部環境の拡張性(風、気圧、障害物など)

| シミュレータ | 評価 | 理由 | 根拠URL |
| :--- | :---: | :--- | :--- |
| Gazebo | Ο | WorldファイルにWind Effectsプラグインを追加することで、風速や風向、突風などを詳細に設定可能。 |  |
| AirSim | Δ | 専用の天候APIはないが、Python APIのsimAddVehicleForce等を用いて機体に外力を加えることで、風の影響を擬似的に実装可能。 | [-](https://microsoft.github.io/AirSim/apis/) |
| Pegasus | Ο | 専用の天候機能はないが、Python APIを通じてシミュレーション中の物体に任意の力を加えられるため、自作スクリプトによる風の実装が可能。 | |
| 箱庭 | Ο | 拡張機能として環境シミュレーション機能(風効果など)が公式に提供されており、パラメータで設定可能。JSONで風や温度、気圧情報を設定し、それらの情報をPDUに変換する箱庭アセット (Pythonプログラム)もサンプルとして一般公開している。 | [-](https://github.com/toppers/hakoniwa-drone-core/tree/main/docs/drone_environment) |
