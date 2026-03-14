[English Version](README.en.md)

このリポジトリでは、[hakoniwa-px4sim](https://github.com/toppers/hakoniwa-px4sim) を発展させ、拡張性と汎用性を高めたドローンシミュレータのコア機能を提供します。PX4やArdupilot、ロボットシステム(ROS)、さらにはスマホ、XR、Webとの連携も視野に入れた柔軟な設計が特徴です。

# 🚨 License Notice / ライセンスについて
This project is distributed under a custom non-commercial license.
本プロジェクトはカスタム非商用ライセンスの下で配布されています。

- 📄 License (English): [LICENSE](LICENSE.md)
- 📄 ライセンス (日本語): [LICENSE-ja](LICENSE-ja.md)

⚠️ Commercial use is prohibited | 商用利用は禁止されています

For commercial licensing inquiries:

商用ライセンスに関するお問い合わせ: tmori@hakoniwa-lab.net

👉 For the PRO version license (commercial use), see:  
👉 商用利用可能な PRO 版ライセンスについては以下をご覧ください:  
🔗 [Drone PRO License (Japanese)](https://github.com/hakoniwalab/hakoniwa-license/blob/main/licenses/drone-pro-license)

# コンセプト

「シミュレーションの世界を飛び出す！」をモットーに、以下の3つを柱としています：

- **シンプルさ**: 誰でも簡単に使えるドローンシミュレータ。  
- **多様性**: ゲーム、教育、研究、ビジネスなど、幅広いアプリケーションに対応。  
- **接続性**: PX4/Ardupilot、Unity、Unreal Engine、ROS、スマホ、XR、Webとのシームレスな連携。

---

## 「シミュレーションの世界を飛び出す！」とは？

仮想空間の中に閉じず、**現実世界の課題解決や価値創造**を目指したシステム設計を意味します：

### **1. 現実世界との接続**
- **PX4/Ardupilot** や **ROS** と連携し、実機さながらの制御を実現。  
- **物流試験や展示用途**での活用に対応。  
- 仮想シミュレーションの結果を、すぐに実機テストや運用に反映可能。  

### **2. 多様なプラットフォーム対応**
- **スマホ、XR、Web、Unity、Unreal Engine** など、さまざまなデバイスや環境で動作。  
- ゲームやエンターテインメントコンテンツとしても展開可能。  

### **3. ユーザーの創造性を拡大**
- 教育向けに、学生や学習者が簡単にモデリングや制御工学を体験できるツールを提供。  
- 非専門家でも気軽に利用できる設計で、ゲームや展示会での体験提供にも最適。

---


# ユースケース

- ゲーム: ドローン操縦を手軽に楽しむ。
- エンタメ: 展示用途（例: 万博でのデモ）。
- 訓練: プロ操縦者向けのリアルな動作再現。
- 教育: 制御工学やモデリング学習。
- 研究: 環境や機体のシミュレーション。
- 物流: 実証実験場として活用。


# 特徴

1. C/C++ ベース： 箱庭ドローン・コア機能をCライブラリとして提供し、他の言語での拡張を容易化。
2. 複数プラットフォーム対応: Windows, Mac, Linux, WSL2 など主要OSをサポート。
3. 箱庭モードと非箱庭モードのサポート
   - 箱庭あり：箱庭ドローン操作用 Python API、外部環境(風や温度など)、スマホやXR、Web、ロボットシステム(ROS)と連携したシミュレーションが可能。
   - 箱庭なし：ドローンの物理モデルや制御モデルを独立して実行することが可能。PX4/Ardupilotとの連携も可能。


> 🧩 **箱庭とは？**
> 複数のシミュレータや制御ノードを、共通の時刻・通信基盤のもとで接続し、**分散協調動作を実現するシミュレーション・ハブ**です。
> 実機・XR・ROS・Webなど多様なシステムとリアルタイムでつながる、開かれたアーキテクチャを特徴とします。


以下、箱庭あり版を利用することで実現できる機能を中心に紹介します。

## 箱庭ドローン操作用 Python API

箱庭ドローンシミュレータは、Python APIを通じてドローンの操作やフライトプランの記述をサポートします。これにより、ユーザーはPythonスクリプトから直接ドローンの動作を制御できます。

例えば、以下のような操作が可能です：

* ドローンのテイクオフ
* ドローンの移動
* ドローンの位置情報のデバッグ表示
* 荷物の搬送
* ドローン前方のカメラ画像の取得とファイル保存
* 3DLiDARデータの取得とデバッグ表示
* ドローンの着陸

さらに、本APIは、用途に応じて2種類を利用できます。

- 📘 詳細: [箱庭ドローン操作用 Python API](drone_api/README-ja.md)
  - 箱庭システムを前提としたAPI。
  - ドローンを直接PDU経由で制御し、Unity/Unrealの可視化や外部環境シミュレーションと統合可能。
  - 教育・実習・デモ用途に最適。
- 📘 詳細: [External RPC Driver](drone_api/external_rpc/README.md)
  - 箱庭 service API を使って `SetReady` / `TakeOff` / `GetState` / `GoTo` / `Land` を実行する最小 Python driver。
  - fleet config の `serviceConfigPath` と `controller.serviceMode = "rpc"` を前提とする。
  - `HakoniwaRpcDroneClient` による単一機体制御と、`FleetRpcController` による複数機体同時制御の入口を提供する。
  - 箱庭あり版の service 制御の結合確認やテストドライバ用途を想定。
- 📘 詳細: [Python API (Ardupilot / PX4 対応)](docs/python_api/mavlink_api.md)
  - `pymavlink` を利用し、ArdupilotやPX4 SITLと連携可能。
  - Ardupilot/PX4の制御モードや状態遷移を吸収し、同一のAPIで操作可能。
  - 複数機体・混在環境（Ardupilot + PX4）もサポート。

## 外部環境(風や温度など)のシミュレーション(小規模の場合)

箱庭ドローンシミュレータは、風や温度などの外部環境をシミュレーションする機能を提供します。これにより、ドローンの動作に対する外的要因の影響をリアルに再現できます。
例えば、以下のようなシミュレーションが可能です：

* 風の影響を受けたドローンの飛行
* 温度変化によるドローンの性能変化
* 気圧変化によるドローンの飛行特性の変化
* バウンダリー（天井や床、壁など）によるプロペラ風の影響

詳細は、[こちら](/docs/environment/README-ja.md)を参照ください。

なお、外部環境のシミュレーション実行用のサンプルプログラムを Python で提供しています。
本サンプルを利用される場合は、事前に、[箱庭ドローン操作用 Python API](#箱庭ドローン操作用-python-api)のセットアップを行ってください。

## 外部環境(風や温度など)のシミュレーション(大規模の場合)

より大規模な外部環境（風・温度・気圧・電波強度・都市データ等）でのシミュレーションを行う場合は、以下の新バージョンを利用してください。 

- [hakoniwa-map-viewer](https://github.com/hakoniwalab/hakoniwa-map-viewer)

## 複数機体でのシミュレーション

箱庭ドローンシミュレータは、複数のドローン機体を同時にシミュレーションする機能を提供します。
複数の機体を用いた隊列飛行の検証など、より高度なシナリオのシミュレーションが可能です。

複数機体のシミュレーションは、以下のフライトコントローラに対応しています。

- Ardupilot
- PX4 
- 箱庭ドローン操作用 Python API での制御

legacy 形式では `drone_config_x.json` の列挙で、新方式では fleet file で、2機にとどまらず N 機体の同時シミュレーションが可能です。

※ 実行可能な台数はマシンの性能に左右されます。

### 複数機体のアーキテクチャ

以下の図は、複数機体シミュレーションにおける構成を示しています。

- MAVLink経由の制御では、各ドローンごとに FCU (Ardupilot/PX4) インスタンスを起動し、
  Python クライアントは MAVLink ポートを通じて個別に接続します。
- Hakoniwa PDU経由の制御では、Python クライアントが直接 PDU を介して
  各ドローンインスタンスを制御します。
- legacy 形式では各機体に対応する `drone_config_x.json` が存在し、aircraft と controller の設定を定義します。
- new 形式では fleet file を入口にし、type 定義と個体配置から各機体の `DroneConfig` を構成します。
- 箱庭 service 制御を使う場合は、fleet file に `serviceConfigPath` を持たせ、type 定義側で `controller.serviceMode = "rpc"` を指定します。

![image](/docs/images/multi-drone-architecture.png)

### 複数機体のセットアップおよび実行方法

- [Ardupilotでの複数機体シミュレーション](/docs/multi_drones/ardupilot.md)
- [PX4での複数機体シミュレーション](/docs/multi_drones/px4.md)
- [箱庭ドローン操作用 Python APIでの複数機体制御](/docs/multi_drones/hakoniwa_python.md)

## 100台+同時シミュレーション（大規模フリート）

v3.6.0 では、**1台のマシン上で100台以上を同時実行できる fleet-oriented architecture** を導入しました。  
実測では、**100 / 128 / 200 / 256 機体**で同時シミュレーション実行を確認しています。

従来、大規模マルチエージェントのリアルタイム検証は専用サーバー群を前提にすることが一般的でした。  
本リリースでは、**手元の1台のMac上で同等のスケールを運用可能**な構成を示しています。

デモ動画:
- 200台同時シミュレーション: https://www.youtube.com/watch?v=p-0IIz8a55M

このリリースの本質:
- `fleet abstraction`（`type定義 + fleetインスタンス定義`）を中核にしたスケール設計
- 「機体ごとの個別通信」ではなく「ノード単位の集約通信」で水平展開
- 1台のPC上で、プロセス分割による分散シミュレーションを完結可能

スコープ / 前提:
- 100台構成では `MuJoCo` / `PX4` / `Ardupilot` は利用せず、内蔵コントローラ + 共有メモリを前提
- 衝突判定なし
- 外部制御は Python からの低頻度コマンド（`GoTo` 等）を前提
- 検証環境は Arm Mac（macOS）に限定（他OSは未検証）

ユースケース:
- バーチャルドローンショーでのデモ
- 群制御アルゴリズムの検証
- 大規模シミュレーション研究（分散実行の評価）

v3.6.0での対応:
1. ドローン設定のコンパクト化
   - `drone_config_x.json` 列挙型から `type定義 + fleetインスタンス定義` へ移行
   - `pdudef` も `paths`（型定義）+ `robots`（インスタンス列挙）の分離構成に統一
2. ログ出力のオプション化
   - 100台運用で CSV ログを無効化可能
3. Python制御の複数機体対応
   - `FleetRpcController` を中心に同時指令・非同期待機を実装
   - `run_square_mission.bash` / `run_show.bash` で多機体シナリオを実行可能
4. 内蔵コントローラの選択性
   - controller 設定を type 側で扱い、差し替えしやすい構成に整理

通信モデル:
- 共有メモリ + PDU ベースで低オーバーヘッド通信
- 200機体状態の実データ量（合計）は `約10KB/step`（packed payload）
- 100機体単位に分割する運用では `約5KB/packet` が目安
- `DroneVisualStateArray` は `pdu_size=16384 bytes (=16KB)` で運用（固定フレーム確保）
- サイズ設計の考え方: 1パケットあたりの実測値（100機体: 約4〜5KB）を基準に、将来の項目追加・運用余裕を見込んで 16KB 枠を採用

並列実行の実測結果:
- 200機体 `show-runner` 実測
- `1 process: wall-clock 232.65s`
- `4 processes: wall-clock 135.62s`
- `約42%` 実行時間短縮
- ※ 考察: 理論線形短縮（75%）より小さい理由:
  共有メモリ同期・サービス登録/初期化待ち・制御オーケストレーションの固定コストが残るため

スケーリング見通し（推計）:
- `1 node ≈ 200 drones`
- `5 nodes ≈ 1000 drones`
- 単一PC内でも「複数ノード相当の分割実行」を再現可能（ローカル分散構成）
- サーバーは個別1000機体ではなく集約5ノードを受信
- 5ノード時の概算（状態PDUのみ）: `約50KB/step`（20ms周期で `約2.5MB/s`）
  - 計算: `50KB / 0.02s ≈ 2.5MB/s`
  - ※ Conductor でノード時刻同期を行う構成では、別途同期トラフィックが加わる
  - ※ 1000機体の分散実測は次フェーズで検証予定

次フェーズ（性能検証）:
- 1ノード/5ノードで同条件の end-to-end レイテンシ計測
- jitter（周期ゆらぎ）と packet drop 率の定量化
- 同一フォーマットでの再現可能なベンチマーク公開

今回のアーキテクチャ:
- fleets 構成では、`type定義 + fleetインスタンス定義` を入口に、`drone-service`（分割実行可）+ `VisualStatePublisher` + `WebBridge` + `External RPC` で群制御します。
- 詳細は以下の構成図と fleets ドキュメントを参照してください。

![Fleets 100+ Architecture](docs/fleets/architecture.png)

関連ドキュメント:
- [fleets ドキュメント索引](docs/fleets/README.md)
- [fleets 実行時コンフィグ構成（どれを使うか）](docs/fleets/config-runtime-map.md)
- [fleets 機体数依存コンフィグ範囲](docs/fleets/config-scope.md)
- [hakoniwa-core 固定パラメータ設計](docs/fleets/core-parameter-sizing.md)
- [Drone Show Runbook](docs/fleets/drone-show-runbook.md)
- [性能レポート](docs/fleets/performance-report.md)
- [External RPC Driver](drone_api/external_rpc/README.md)

## ログリプレイ機能

本シミュレータは、記録された飛行ログ（`drone_dynamics.csv`）を再生するログリプレイ機能を搭載しています。
この機能により、過去のシミュレーション飛行を再現し、詳細な分析やデバッグを行うことが可能です。

主な特徴：
*   **シミュレーションの再現**: ログデータに基づき、ドローンの動きを忠実に再現します。
*   **再生制御**: 再生範囲の指定や、再生速度の変更（スロー再生など）が可能です。
*   **透過的な切り替え**: 通常のシミュレーションと同じインターフェースを利用するため、可視化環境（Unity/Unreal）などをそのまま利用してリプレイを確認できます。

リプレイ機能の詳細な設定方法や実行手順については、以下のドキュメントを参照してください。

*   [ログリプレイ機能の詳細 (replay/README.md)](replay/README.md)

## 他OSSとの比較

箱庭ドローンシミュレータの特徴を、他OSS(Gazebo, AirSimなど)と比較すると、以下のような点が挙げられます。
詳細な情報は、[箱庭ドローンシミュレータの特徴と他OSSとの比較](docs/evaluation/README.md)をご覧ください。

### 連携を前提とした「開かれた」ドローンシミュレータ：
箱庭ドローンシミュレータは、それ単体で完結するクローズドなシミュレータではなく、デジタルツインやAIシステムとの連携を前提とした、開かれた設計思想に基づいています。さらに、軽量でクロスプラットフォームに対応しており、多様な実行環境への展開が可能です。

### 柔軟性を支えるモジュール設計と「エンジンの切り出し」：
この柔軟性を支えるのが、箱庭全体に共通する「マイクロサービスアーキテクチャ」です。箱庭ドローンシミュレータも徹底したモジュール設計がなされており、特に注目すべきは、一般的に困難とされる「ドローンシミュレータのエンジン部分の切り出し」を実現した点です。このエンジン部分はライブラリとして独立しているため、スマートフォンやXRデバイスなどから直接呼び出すことができます。これにより、教育・研究・デモ用途など、多様な現場に柔軟に適応可能です。

### 国産ならではの手厚いサポート体制：
一方、既存のOSS（Gazebo, AirSimなど）は海外製が主流であり、導入やカスタマイズには高い技術知識が求められ、特に教育機関や中小規模の組織には敷居が高いのが現状です。
その点、箱庭ドローンシミュレータは日本国内で開発されており、公式サポートや教育サービスの提供により、導入・運用のハードルを大きく下げています。特に国内の教育・研究機関において、日本語による手厚い支援体制は大きなアドバンテージとなります。

# 依存ライブラリ

箱庭ドローンシミュレータのライブラリ群は、以下の外部ライブラリと内部ライブラリ(箱庭プロジェクトで開発されているもの)に依存しています。

## 外部

- [glm](https://github.com/g-truc/glm.git) : 数学ライブラリ。
- [mavlink_c_library_v2](https://github.com/mavlink/c_library_v2.git) : MAVLink通信ライブラリ。
- [nlohmann/json](https://github.com/nlohmann/json.git) : JSON操作ライブラリ。

## 内部

- [hakoniwa-core-pro](https://github.com/hakoniwalab/hakoniwa-core-pro) : 箱庭シミュレーションとの統合。
- [hakoniwa-pdu-registry](https://github.com/hakoniwalab/hakoniwa-pdu-registry.git) : 箱庭PDUの定義・生成・管理。(hakoniwa-core-proに含まれる)

# アーキテクチャ

箱庭ドローンシミュレータは、 **「箱庭システム」上で動作するアセット（実行ユニット）** として設計された、モジュール型ドローンシミュレータです。

---

本シミュレータは、以下のような多様な構成パターンに対応しており、**目的や連携対象に応じて柔軟に選択可能**です：

1. 箱庭なし版：**シングルパターン**  
   - Cライブラリとして単独動作し、Unity・Unreal・Pythonから直接呼び出し可能

2. 箱庭あり版：**共有メモリパターン**
   - 箱庭コアとMMAPで高速連携し、Unity/Unrealとのリアルタイム可視化に最適

3. 箱庭あり版：**コンテナパターン**
   - Dockerコンテナ上で分散構成を実現。Bridge経由でROS2やWebとも接続可能


📌 アーキテクチャ図と背景の詳細は以下をご覧ください：

* 🖼️ [全体アーキテクチャを見る](docs/architecture/overview.md)
* 🔬 [内部アーキテクチャの技術詳細を見る](docs/architecture/detail.md)
* 🛰️ [DroneVisualStatePublisher 設計メモを見る](docs/architecture/visual_state_publisher.md)


# 動作環境

* サポートOS
  * Arm系Mac
  * Windows 11
  * Windows WSL2
  * Ubuntu 22.0.4, 24.04

* ビルド・テストツール
  * cmake
  * googletest

* 必要なツール類
  * pyenv
    * python: version 3.12.0
      * 3.13以降では動きません。
* MacOSの場合、homebrewでインストールしたものでは動きません。

# シミュレータ準備チェックリスト

このシミュレータは、以下のように **箱庭あり／なし** の2モードで利用可能です。  
それぞれに必要な環境やツールが異なるため、事前に以下のチェックリストをご確認ください。

| 項目 | 説明 | 箱庭あり版 | 箱庭なし版 |
|------|------|------------|------------|
| OS環境 | Windows / macOS (Arm対応) / Linux / WSL2 | ✅ | ✅ |
| Python環境 | `Python 3.12.0` を使用 | ✅ | ✅ |
| Unity | [hakoniwa-unity-drone](https://github.com/hakoniwalab/hakoniwa-unity-drone) の実行に必要 | ✅ | ❌ |
| Unreal Engine | [hakoniwa-unreal-drone](https://github.com/hakoniwalab/hakoniwa-unreal-drone) の実行に必要 | ✅ | ❌ |
| hakoniwa-core-cpp-client | 箱庭コアとの接続に必須 | ✅ | ❌ |
| QGroundControl | PX4連携時の操作に使用 | ✅ | ✅ |
| MissionPlanner | Ardupilot連携時の操作に使用 | ✅ | ✅ |
| Gameコントローラ | ラジコン操作に使用 (任意) | ✅ | ❌ |
| Drone用Python API | フライトプラン記述に使用可能 | ✅ | ❌ |
| [風のシミュレーション](docs/environment/README-ja.md) | 風の影響を受けたドローンの動作を確認 | ✅ | ❌ |
| 衝突検出 | ドローンの衝突を検出する機能 | ✅ | ❌ |
| Web連携 (任意) | [hakoniwa-webserver](https://github.com/toppers/hakoniwa-webserver) など | ✅ | ❌ |
| ROS2連携 (任意) | [hakoniwa-pdu-registry](https://github.com/hakoniwalab/hakoniwa-pdu-registry) など | ✅ | ❌ |

📌 **備考**
- Pythonは **3.12.0** 固定（それ以外は非対応）
- Mac環境では `homebrew` 経由のPythonでは動作しません
- Unityエディタは、Unity6.0以降が必要です
- Unreal Engineは、Unreal Engine 5.6以降で動作確認しています
- Gameコントローラを使う場合は `rc/rc_config/` の設定ファイルを確認してください

---

# 📦 バイナリの入手方法

本シミュレータの実行には、以下のページから **各OS向けのバイナリZIPファイル** をダウンロード・解凍する必要があります：

👉 [🔗 最新バイナリはこちら（Releases）](https://github.com/toppers/hakoniwa-drone-core/releases)

### ✅ ファイル一覧（例）

| ファイル名 | 対応OS | 説明 |
|------------|--------|------|
| `mac.zip`  | macOS  | M1/M2/M3などのArm Mac対応 |
| `lnx.zip`  | Ubuntu | Ubuntu 22.04 / 24.04対応 |
| `win.zip`  | Windows | Windows 11対応 |

ZIPを展開すると、以下のようなバイナリファイルが含まれています：

- `mac-aircraft_service_px4`
- `mac-drone_service_rc`
- `mac-main_hako_drone_service`
- `mac-drone_visual_state_publisher`
- `hako_service_c`（ライブラリ）
- など

使用する構成に応じて、必要なファイルを選んでください。

大規模 fleet / drone show 構成では、`DroneVisualStatePublisher` のバイナリも必要です。
配布バイナリでは各OSごとに以下の名前で同梱されます。

- macOS: `mac-drone_visual_state_publisher`
- Linux: `linux-drone_visual_state_publisher`
- Windows: `win-drone_visual_state_publisher.exe`

`tools/launch-fleets-scale-perf.bash` などの launcher 系スクリプトは、既定でこの配布先バイナリを利用します。
必要に応じて `HAKO_VISUAL_STATE_PUBLISHER_BIN` で上書きできます。

> 📁 解凍場所に制限はありませんが、**日本語や空白を含まないパス**を推奨します。



# チュートリアル（Getting Started）

本シミュレータは、構成パターンに応じてセットアップ手順が異なります。  
以下のチュートリアルから、ご自身の目的に合った構成をお選びください。

---

## 🔹 シングルパターン（箱庭なし）

- 箱庭なしで動作する最小構成です。
- Unity/Unreal から直接呼び出すCライブラリや、CUIアプリ／Pythonスクリプトとして動作します。

📘 [シングルパターンのチュートリアルを見る](docs/getting_started/single.md)

---

## 🔸 共有メモリパターン（箱庭あり）

- MMAPを使って箱庭コアと連携し、Unity/Unrealとのリアルタイム同期や複数アセットとの協調が可能です。

📘 [共有メモリパターンのチュートリアルを見る](docs/getting_started/mmap.md)

---

## 🔶 コンテナパターン（箱庭あり）

- Dockerコンテナ環境で動作し、Bridgeを介してROS2やWebと連携できます。
- デモ・教育・遠隔環境での利用に適しています。

📘 [コンテナパターンのチュートリアルを見る](docs/getting_started/container.md)
