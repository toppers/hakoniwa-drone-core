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
   - 箱庭あり：ロボットシステム(ROS)や、スマホやXR、Webと連携したシミュレーションが可能。
   - 箱庭なし：ドローンの物理モデルや制御モデルを独立して実行することが可能。PX4/Ardupilotとの連携も可能。

また、箱庭ドローンシミュレータの特徴を、他OSS(Gazebo, AirSimなど)と比較すると、以下のような点が挙げられます。
詳細な情報は、[箱庭ドローンシミュレータの特徴と他OSSとの比較](docs/evaluation/README.md)をご覧ください。

## 連携を前提とした「開かれた」ドローンシミュレータ：
箱庭ドローンシミュレータは、それ単体で完結するクローズドなシミュレータではなく、デジタルツインやAIシステムとの連携を前提とした、開かれた設計思想に基づいています。さらに、軽量でクロスプラットフォームに対応しており、多様な実行環境への展開が可能です。

## 柔軟性を支えるモジュール設計と「エンジンの切り出し」：
この柔軟性を支えるのが、箱庭全体に共通する「マイクロサービスアーキテクチャ」です。箱庭ドローンシミュレータも徹底したモジュール設計がなされており、特に注目すべきは、一般的に困難とされる「ドローンシミュレータのエンジン部分の切り出し」を実現した点です。このエンジン部分はライブラリとして独立しているため、スマートフォンやXRデバイスなどから直接呼び出すことができます。これにより、教育・研究・デモ用途など、多様な現場に柔軟に適応可能です。

## 国産ならではの手厚いサポート体制：
一方、既存のOSS（Gazebo, AirSimなど）は海外製が主流であり、導入やカスタマイズには高い技術知識が求められ、特に教育機関や中小規模の組織には敷居が高いのが現状です。
その点、箱庭ドローンシミュレータは日本国内で開発されており、公式サポートや教育サービスの提供により、導入・運用のハードルを大きく下げています。特に国内の教育・研究機関において、日本語による手厚い支援体制は大きなアドバンテージとなります。

# 依存ライブラリ

## 外部

- [glm](https://github.com/g-truc/glm.git) : 数学ライブラリ。
- [mavlink_c_library_v2](https://github.com/mavlink/c_library_v2.git) : MAVLink通信ライブラリ。
- [nlohmann/json](https://github.com/nlohmann/json.git) : JSON操作ライブラリ。

## 内部

- [hakoniwa-core-cpp-client](https://github.com/toppers/hakoniwa-core-cpp-client.git) : 箱庭シミュレーションとの統合。
- [hakoniwa-ros2pdu](https://github.com/toppers/hakoniwa-ros2pdu.git) : 箱庭PDUとの統合。

# アーキテクチャ

箱庭ドローンシミュレータは、\*\*「箱庭システム」上で動作するアセット（実行ユニット）\*\*として設計された、モジュール型ドローンシミュレータです。

> 🧩 **箱庭とは？**
> 複数のシミュレータや制御ノードを、共通の時刻・通信基盤のもとで接続し、**分散協調動作を実現するシミュレーション・ハブ**です。
> 実機・XR・ROS・Webなど多様なシステムとリアルタイムでつながる、開かれたアーキテクチャを特徴とします。

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

# ✅ シミュレータ準備チェックリスト

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
| ROS2連携 (任意) | [hakoniwa-ros2pdu](https://github.com/toppers/hakoniwa-ros2pdu) など | ✅ | ❌ |

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
- `hako_service_c`（ライブラリ）
- など

使用する構成に応じて、必要なファイルを選んでください。

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
