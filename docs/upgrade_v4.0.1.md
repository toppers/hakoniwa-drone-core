# Hakoniwa Drone Simulator v4.0.0 → v4.0.1 アップデート手順

## はじめに

Hakoniwa Drone Simulator v4.0.1 は、v4.0.0 で導入した Control Link / Scenario Link と Controller Orchestrator を実運用へ向けて拡張した、箱庭ドローンPRO向けのアップデートです。

主な変更点は次のとおりです。

- Control Link のインタフェース仕様、ビルド手順、Quick Start の整備
- Scenario Link のビルド・実行手順と外乱注入手順の整備
- EKF、PX4 パラメータ連携、PID tuning の拡張
- Business Pack 向け Recipe とクロスプラットフォーム・ビルド入口の追加
- 複数プロセスへ機体を均等配分する fleet split の改善
- ArduPilot / PX4 / MuJoCo Viewer / External RPC 周辺の修正
- Docker イメージ版 `v3.1.0` への更新

本ドキュメントでは、v4.0.0 から v4.0.1 へ更新する際の変更点、互換上の注意、更新後の確認方法を説明します。

> **公開範囲について**
>
> v4.0.1 は `hakoniwa-drone-pro` に存在するPRO向けリリース履歴であり、無償版 `hakoniwa-drone-core` のバイナリリリースを示すものではありません。ただし、製品全体の更新履歴とPRO版の機能をユーザへ案内するため、このアップデート文書自体は無償版リポジトリでも公開します。文書の公開は、PRO対象ソースや配布物の公開を意味しません。

---

## 対象バージョン

- 更新元: `v4.0.0`
- 更新先: `v4.0.1`
- MuJoCo: `3.9.0`（変更なし）
- Docker イメージ: `toppersjp/hakoniwa-drone-core:v3.1.0`

### 履歴上の注意

`v4.0.1` タグ時点の `VERSION.txt` は `4.0.0` のままです。これは当時のリリース履歴に残る不整合です。v4.0.1 を識別する場合は `VERSION.txt` だけで判断せず、`v4.0.1` タグまたは納品物に記録された commit SHA を確認してください。

この文書では履歴を修正せず、実際のタグ差分に基づいて v4.0.1 の内容を説明します。

---

## アップデート方法

### 顧客環境

既存の v4.0.0 ディレクトリへ直接上書きせず、箱庭ラボから納品された v4.0.1 のアーカイブを新しいディレクトリへ展開してください。

その後、顧客固有の次のファイルだけを内容を確認しながら移行します。

- 機体設定
- controller 設定
- launcher 設定
- tuning profile と調整結果
- 独自の Control Adapter / Scenario Link 連携コード

内部インタフェースと設定項目が変更されているため、v4.0.0 の build tree や生成済みオブジェクトは流用せず、クリーンビルドしてください。

### 開発・保守環境

リポジトリへアクセスできる保守環境では、次のようにタグと submodule を揃えます。

```bash
git fetch --tags
git checkout v4.0.1
git submodule update --init --recursive
```

タグに含まれる submodule SHA を利用し、個別の submodule だけを無条件に最新化しないでください。

---

## 重要な互換ポイント

### 1. MuJoCo は 3.9.0 のまま

v4.0.1 では `MUJOCO_VERSION.txt` の値は `3.9.0` です。v4.0.0 から MuJoCo SDK を入れ替える必要はありません。

macOS では、利用中の実行ファイルが 3.9.0 の dylib を参照していることを確認してください。

```bash
otool -L ./mac/<binary-name> | grep -i mujoco
```

### 2. Control Link / Scenario Link はPROライセンス対象

Control Link、Scenario Link、EKF・PID tuning、PX4 parameter integration などはPROまたはオプションライセンスの対象です。これらのソース、設定、内部仕様、手順書を無償版へコピーしないでください。

### 3. Controller / Adapter 周辺は再ビルドする

Controller Orchestrator、Control Adapter context、Mixer、EKF 周辺の型と実装が更新されています。独自 Adapter や内部ヘッダへ依存するコードは、v4.0.1 のヘッダで再ビルドしてください。

### 4. 設定ファイルは差分移行する

v4.0.1 では controller、EKF、tuning、fleet、Business Pack Recipe の設定が追加・更新されています。v4.0.0 の設定ディレクトリ全体を上書きコピーせず、利用中の独自値だけを v4.0.1 の標準設定へ反映してください。

### 5. Docker とPRO本体の版番号は一致しない

この時点の Docker イメージ版は `v3.1.0` です。PRO本体の `v4.0.1` とは版番号体系が異なります。Docker の更新では `docker/latest_version.txt` と利用するイメージタグを確認してください。

---

# 主な変更点

## 1. Control Link の利用手順と仕様を整備

外部制御システムと箱庭ドローンPROを接続する Control Link について、次の情報を追加・整理しました。

- interface specification
- Quick Start
- macOS / Ubuntu のビルド・インストール手順
- fault injection control の例
- PID tuning の手順

独自 Control Adapter を利用している場合は、v4.0.1 の interface specification と実装を照合し、Control Adapter context と backend の接続を確認してください。

関連文書:

```text
pro-docs/control-link/
```

## 2. Scenario Link の利用手順を整備

Scenario Link について、外乱を箱庭ドローンへ入力するまでのビルド、runtime setup、実行手順を追加しました。

主な対象は次のとおりです。

- macOS
- native Ubuntu
- Docker を利用する Ubuntu 構成
- tuned result の適用
- disturbance / fault injection

関連文書:

```text
pro-docs/scenario-link/
tools/setup-scenario-link-runtime.bash
tools/setup_scenario_link_runtime.py
```

## 3. EKF と PX4 tuning を拡張

PX4 の EKF パラメータを箱庭ドローンPROへ取り込み、tuning pipeline で評価するための設定とツールを追加しました。

主な追加内容:

- EKF controller / mixer の設計文書
- PX4 parameter export tool
- PX4 parameter integration guide
- angle / hover の EKF 評価 phase と score
- PID tuning profile 作成ツール
- tuning suite の timing と評価処理の改善

既存の tuning profile を利用する場合は、v4.0.1 の標準 profile と比較し、追加された EKF および timing 項目を取り込んでください。

関連:

```text
tuning/px4/
tuning/tools/create_pid_tuning_profile.py
pro-docs/control-link/pid-tuning.md
```

## 4. Business Pack Recipe と `hako.py` を追加

Business Pack 環境で、依存関係の確認、ビルド、テスト、インストール、パッケージ作成を同じ入口から実行するための `tools/hako.py` と Recipe を追加しました。

```text
tools/hako.py
recipes/
hakoniwa-build.yaml
pro-docs/business-pack/build.md
```

環境によって Foundation の場所や前提パッケージが異なるため、最初に `doctor` で構成を確認してください。

```bash
python3.12 tools/hako.py doctor
```

## 5. fleet split の配分を改善

1機から複数機までの fleet を複数プロセスへ分割する処理を見直し、余りの機体を最終プロセスへ割り当てる構成に更新しました。

これにより、機体数がプロセス数で割り切れない場合や、小規模 fleet の分割結果が安定します。既存の自動生成済み fleet 設定は、v4.0.1 の generator で再生成してください。

```text
tools/gen_fleet_split_config.py
```

## 6. ArduPilot / PX4 / Viewer を改善

次の実行経路に修正を加えています。

- ArduPilot runner と aircraft service
- PX4 aircraft service
- MuJoCo Viewer の camera control
- drone service / RC service
- Visual State Publisher
- External RPC の command とサンプルアプリ

該当機能を利用する場合は、設定ファイルだけでなく実行バイナリと launcher も同じ v4.0.1 の成果物へ揃えてください。

## 7. Docker イメージを v3.1.0 へ更新

Dockerfile、PDU bridge 設定、README を更新し、`docker/latest_version.txt` を `v3.1.0` に変更しました。

```bash
docker pull toppersjp/hakoniwa-drone-core:v3.1.0
```

既存環境で `latest` を使用している場合も、再現性のため明示的な `v3.1.0` タグの利用を推奨します。

---

## 更新後の確認

### 1. リビジョン確認

保守環境では、v4.0.1 タグを指していることを確認します。

```bash
git describe --tags --exact-match
git rev-parse HEAD
git submodule status
```

`VERSION.txt` は前述の履歴上の不整合により `4.0.0` と表示されるため、v4.0.1 の確認には使用しません。

### 2. ビルドとテスト

利用OSの標準手順でクリーンビルドし、テストを実行します。Business Pack 統合環境では次の順序で確認します。

```bash
python3.12 tools/hako.py doctor
python3.12 tools/hako.py build
python3.12 tools/hako.py test
```

### 3. 基本飛行

少なくとも次を確認してください。

- 標準機体が起動する
- 離陸、ホバリング、着陸ができる
- Viewer に機体姿勢が反映される
- 利用中の External RPC / RC 操作が完了する

### 4. PRO連携

契約・利用範囲に応じて次を確認してください。

- Control Adapter を読み込める
- Control Link の各 backend が期待どおり呼び出される
- Scenario Link から外乱・故障を入力できる
- EKF / PID tuning profile を読み込める
- ArduPilot または PX4 SITL と接続できる

### 5. 複数機体

fleet 設定を再生成し、機体数がプロセスへ期待どおり配分されることを確認してください。特に、機体数がプロセス数で割り切れない構成を1つ確認します。

---

## まとめ

v4.0.1 は、v4.0.0 のPRO機能を実際の構築・調整・連携で使うための仕様、ツール、Recipe、手順を大きく補強したリリースです。

更新時の要点は次のとおりです。

- MuJoCo は `3.9.0` のまま維持する
- PRO対象ソースや配布物を無償版へ同期しない
- Controller / Adapter 周辺をクリーンビルドする
- 独自設定は v4.0.1 の標準設定へ差分移行する
- fleet 設定を再生成して配分を確認する
- Docker は本体と異なる `v3.1.0` タグを使用する
- v4.0.1 の識別にはタグまたは commit SHA を使う
