# ドローンシミュレータ比較（2026年10月版・下書き）

この文書は、研究者が目的に合うシミュレータを選ぶための判断材料です。公式資料に基づく提供状況の文献調査であり、各製品を起動して性能や精度を測った比較ではありません。機能の有無だけでなく、公式機能か、追加実装が必要か、どの条件で測った値かを区別します。2025年版は[履歴](../README.md)として残しています。

## 選定の要点

- **Gazebo Jetty**は、ROS 2を中心に既存のロボット資産と接続し、物理・センサー・描画等をプラグインで組み合わせたい用途に向きます。PX4 SITLとの同期実行、GUIなしのサーバー構成も扱います。
- **Project AirSim**は、Unrealの描画やカメラとGISタイルを使う航空シーン、機体ごとに物理モデルを選ぶ構成に向きます。PX4・ArduPilot連携には対応版や検証状況の条件があります。
- **Pegasus**は、Isaac Sim 5.1上でPX4を使ったドローン検証を組み立てる用途に向きます。ArduPilotは実験的でv5.1.0では未テストです。
- **Isaac Sim**は、高品質なRTX描画、視覚センサー、合成データ生成を重視する用途に向きます。一方、公式最小構成はRAM 32 GB、GeForce RTX 4080、VRAM 16 GBで、軽量なCPUのみの用途には向きません。
- **箱庭（無償版）**は、軽量な画面表示なしのコア、PX4・ArduPilot、PDUによる疎結合な拡張、Python API、複数機実行に向きます。これは `hakoniwa-drone-core` のカスタム非商用ライセンス版であり、商用利用可能という意味ではありません。高品質な描画やGPUを使う大規模画像生成を単体の強みとはしません。
- **箱庭 PRO**は、決定論を重視した反復、高速な制御検証、SITLとの定量照合、軽い画面表示なし実行に向きます。Scenario Linkによる外乱・故障注入も選択できます。PROの基本ライセンスと各オプションは別です。

箱庭の2026年の特徴は「接続できること」だけでなく、同じ機体モデルとあらかじめ決めた条件を用い、高速な代役制御とPX4・ArduPilot SITLの制御応答を定量的に照合し、報告できることです。ただし、その照合は定義した許容差に対する判定であり、軌跡の完全一致や実機との一致を意味しません。

比較に用いたx500とEAMSの機体モデルは、メーカーから許可・提供を受けたデータではなく、公式サイト等の公開情報から推定して作成したシミュレーションモデルです。実機またはメーカー公認モデルとの一致を示すものではありません。

## 文書

- [比較結果](./results.md)
- [評価項目の定義](./terms.md)
- [評価理由と根拠](./results-reason/README.md)

## 比較対象の状況

本版は2026年10月時点です。Gazebo Jettyは2025年9月公開のLTS、Project AirSimはv1.0.1、Pegasusはv5.1.0、Isaac Simはv6.2.0を対象にします。Microsoft AirSimはMicrosoftによる更新が終了しています。Colosseumは2026年10月時点でアーカイブ済みのため、比較列には含めません。

競合情報の出典は、[Gazebo releases](https://gazebosim.org/docs/latest/releases/)、[PX4とGazebo](https://docs.px4.io/v1.18/en/sim_gazebo_gz/)、[Project AirSim v1.0.1](https://github.com/iamaisim/ProjectAirSim/releases/tag/v1.0.1)、[Pegasus v5.1.0](https://github.com/PegasusSimulator/PegasusSimulator/releases/tag/v5.1.0)、[Isaac Sim 6.2.0](https://docs.isaacsim.omniverse.nvidia.com/6.2.0/installation/download.html)です。
