# 📘 これは何？
ここでは、「箱庭ドローンシミュレータ」がどのように設計されており、他のシステムとどのように連携できるかを説明します。
シンプルな単体利用から、共有メモリ通信、コンテナを活用した複雑な構成まで、3つの代表的なパターンに分けて解説します。

# 箱庭ドローンシミュレータの全体アーキテクチャ

箱庭ドローンシミュレータは、箱庭コア機能の上で「箱庭アセット」として動作する、柔軟なドローンシミュレータです。
本シミュレータは、箱庭システム全体の中で「Hakoniwa Asset（実行ユニット）」として機能し、ドローンの物理モデルおよび制御モデルを提供します。

---

## 箱庭のアーキテクチャ

ここで、その箱庭とは何か？

それは、複数のシミュレータやシステムを統合し、統一された時間軸で動作させるための「シミュレーション・ハブ」です。
その中核には「箱庭コア機能」があり、これはシミュレータ向けのリアルタイムOSとも言える存在です。

箱庭は以下の5つの主要要素で構成されており、それぞれがハブとしての機能を支えています：

![image](/docs/images/architecture-hakoniwa.png)

---

### 🟨 箱庭アセット

既存のシミュレータや制御プログラムを「箱庭アセット」として登録し、箱庭APIを介して接続することで、異なる環境・実装のモジュール間でも統一的な通信と相互運用が可能になります。

**ユースケース例：**

* Gazeboによる物理シミュレーションと、Unityによる視覚的ビジュアライズの同時実行
* ROSベースの制御ノードと、C#ベースのXRアプリケーションの連携
* 箱庭ドローンシミュレータとUnity、MAVLink、XRの統合利用

---

### 🔌 箱庭API

マルチ言語対応（Python、C/C++、C#、Rust、Elixirなど）を前提に設計された中核的インターフェースです。
これにより、既存資産を活かしつつ、柔軟にアセット開発・統合が可能となります。

---

### ⏱ 箱庭時刻同期

分散環境で整合性のあるシミュレーションを成立させるには、アセット間の時刻同期が不可欠です。
箱庭では、最大許容遅延を考慮した独自の時刻同期機構を導入しており、リアルタイム性と再現性を両立しつつ、複数アセットの並行実行を実現しています。

---

### 📨 箱庭PDUデータ

アセット間の通信データは「PDU（Protocol Data Unit）」形式で標準化されます。
ROS IDL（Interface Definition Language）で定義されたデータ構造をもとに、自動的に型変換・シリアライズ／デシリアライズされる仕組みです。

対応プロトコルの例：

* ROS 2 / DDS
* Zenoh
* MQTT
* UDP
* 共有メモリ（MMAP）

---

### 🟩 箱庭コンポーネント

主要コンポーネントには、以下のようなものがあります：

* **箱庭コンダクタ**：シミュレーション環境全体の制御、時刻同期、負荷分散を担う
* **箱庭ブリッジ**：仮想空間と現実空間をつなぐ中継役として機能し、リアルタイム通信を支援

---

## 箱庭ドローンシミュレータのアーキテクチャ

箱庭ドローンシミュレータは、箱庭アセットの一つとして、ドローンの物理モデルおよび制御モデルを提供します。
他のシミュレータやシステムと連携し、リアルなドローンシミュレーションを実現可能です。

まず、最小構成のアーキテクチャが以下です：

![image](/docs/images/architecture-hakoniwa-drone.png)

箱庭ドローンシミュレータは、以下の2つの主な層で構成されています：

* **Service**
  ドローンの物理モデルや制御モデルを提供する層（箱庭非依存で単体実行可能）

* **Hakoniwa**
  上記Service層の機能を外部へ公開し、箱庭コアと通信する層

この構成により、用途に応じて柔軟に構成・拡張が可能です。以下に3つの代表的なアーキテクチャ例を紹介します。


---

### 箱庭なし版：シングルパターン

![image](/docs/images/architecture-service.png)

箱庭ドローンシミュレータをCライブラリとして単独で使用する構成です。
箱庭コアとの通信は行わず、Service層のみで動作します。

呼び出し方法の例：

* **Unreal Engine**：C++から直接呼び出し
* **Unity**：C#からP/Invokeで呼び出し
* **Java (JME)**：JNIで連携
* **Python**：C拡張モジュールとして組み込み可能

---

### 箱庭あり版：共有メモリパターン

![image](/docs/images/architecture-hakoniwa-drone-1.png)

箱庭コアと共有メモリ（MMAP）を介して接続する構成です。
低レイテンシな通信が可能となり、リアルタイム性の高いシミュレーションを実現します。

連携例：

* Unity/Unreal Engineによるリアルタイムビジュアライズ
* 環境変化（風・温度など）を模擬するアセットとの連携
* Pythonスクリプトからの制御
* ビジュアライズと制御を分離した構成

---

### 箱庭あり版：コンテナパターン

![image](/docs/images/architecture-hakoniwa-drone-2.png)

箱庭および箱庭ドローンシミュレータをDockerコンテナ上で一括実行する構成です。
環境差異を吸収し、柔軟なデプロイが可能です。

**注意点：**

* GUIアプリ（UnityやUnreal Engine）はコンテナ内では動作しないため、ネイティブホスト側で実行し、**箱庭ブリッジ**を介して連携する必要があります。
* 例として、`hakoniwa-webserver` を中継として活用する構成が有効です。


---

## さらなる拡張

ここで説明したアーキテクチャは、ほんの一例であり、他の構成も可能です。例えば、リアルシステムのロボットとの連携などデジタルツイン構成も実現できます。

それを実現するのは、箱庭ブリッジ機能が大きな役割を果たしています。

![image](/docs/images/architecture-bridge.png)

- [AR Bridge](https://github.com/toppers/hakoniwa-ar-bridge):
  ARデバイス（HoloLensなど）と箱庭を接続し、リアルタイムでのAR体験を提供します。
- [Web Server](https://github.com/toppers/hakoniwa-webserver):
   WebSocketサーバーであり、クライアントと箱庭間の双方向通信を可能にします。
- [ROS Bridge](https://github.com/toppers/hakoniwa-bridge):
  Zenoh/ROS2通信を通してROSノードと箱庭を接続し、ROSエコシステムとの統合を実現します。
- [MAVLINK Bridge](https://github.com/toppers/hakoniwa-drone-core/tree/main/mavlink/bridge):
  MAVLinkプロトコルを使用して、Mission PlannerなどのGCSと箱庭を接続します。
- MCP Server:
  Model Context Protocol（MCP）を使用して、箱庭とAIエージェント間のデータ交換を実現します。