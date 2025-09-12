# これは何？

PX4 を用いた複数機体のシミュレーション環境を構築するための手順です。

# 事前準備

１台での PX4 シミュレーション環境構築が済んでいることを前提とします。

コンテナパターンでの PX4 セットアップ手順は、[こちら](/docs/getting_started/container.md)を参照ください。

## PX4（複数機体）セットアップ

### 事前準備（ディレクトリ構成）

複数機体連携する場合、PX4 のリポジトリを**機体数分**用意します。

以下、例として 2 機体分のディレクトリ構成を示します。

```tree
px4-controllers/
├─ c1/
│  └─ PX4-Autopilot/     # PX4 リポジトリ (機体0用)
│     └─ build/…         # 各自のビルド成果物
└─ c2/
　  └─ PX4-Autopilot/     # PX4 リポジトリ (機体1用)
　     └─ build/…
```

* `c1/PX4-Autopilot` と `c2/PX4-Autopilot` は **別クローン**（またはビルド・作業ディレクトリを分ける）。
* それぞれで **ビルド** を実施。ブランチ/タグは同一にしておくと無難です。

また、`hakoniwa-drone-core/config` 以下に、以下のような**機体定義ファイル**を用意します。
(`-2` は 2 機体用の定義ファイル）

```tree
hakoniwa-drone-core/config
├── drone
│   ├── px4-1   # 1機分の定義ディレクトリ
│   │   └── drone_config_0.json
│   └── px4-2   # 2機分の定義ディレクトリ
│       ├── drone_config_0.json  #1台目
│       └── drone_config_1.json  #2台目
└── pdudef
    ├── webavatar-2.json # 2機分の定義(1台目：Drone, 2台目：Drone1)
    └── webavatar.json   # 1機分の定義
```

### ポート設計（本リポのスクリプト既定）

* 機体 `INSTANCE=i` のとき:

  * 機体0 → `14540`
  * 機体1 → `14541`

* 送信先は 2 系統

  * `udp:127.0.0.1:<PORT>`（Docker内 Python 用）
  * `udp:<HOST_IP>:<PORT>`（QGroundControl 用）

> `HOST_IP` は **ホスト（Windows 側）の IP** を指定。WSL2 の場合は注意。
> OS のファイアウォールで該当ポートの UDP を許可しておく。

---

## 実行手順

### 1) PX4（WSL2）

```bash
# 機体0
bash -x hakoniwa-drone-core/tools/px4/run.bash \
  px4-controllers/c1/PX4-Autopilot 0

# 機体1
bash -x hakoniwa-drone-core/tools/px4/run.bash \
  px4-controllers/c2/PX4-Autopilot 1
```

* **GPS が有効**になってから次へ（HOME セット等が済むまで待機）。

### 2) 箱庭（Docker）

```bash
bash hakoniwa-drone-core/docker/tools/run-hako.bash px4 \
  hakoniwa-drone-core/config/pdudef/webavatar-2.json 2
```


### 3) Python スクリプト（Docker 内）

```bash
cd hakoniwa-drone-core/drone_api/pymavlink

python3 -m hakosim_mavlink --name Drone  \
  --connection udp:127.0.0.1:14540 --type px4

python3 -m hakosim_mavlink --name Drone1 \
  --connection udp:127.0.0.1:14541 --type px4
```

### 4) 動作確認

* QGroundControl から `UDP 14540` / `UDP 14541` に接続。
* 2 機が離陸し、三角移動（隊列）することを確認。

---

## インスタンス対応表（例）

| 機体 | Sim (Docker内, TCP) | QGC (WSL2 IP, UDP) | Drone名 (Python) | 設定ファイル                |
| -- | --------------------- | ------------------ | --------------- | --------------------- |
| 0  | tcp:127.0.0.1:4560    | WSL2\_IP:14540     | `Drone`         | `drone_config_0.json` |
| 1  | tcp:127.0.0.1:4561    | WSL2\_IP:14541     | `Drone1`        | `drone_config_1.json` |

