# これは何？

Ardupilot を用いた複数機体のシミュレーション環境を構築するための手順です。

# 事前準備

１台での Ardupilot シミュレーション環境構築が済んでいることを前提とします。

コンテナパターンでの Ardupilot セットアップ手順は、[こちら](/docs/getting_started/container.md)を参照ください。

## Ardupilot（複数機体）セットアップ

### 事前準備（ディレクトリ構成）

複数機体連携する場合、Ardupilot のリポジトリを**機体数分**用意します。

以下、例として 2 機体分のディレクトリ構成を示します。

```tree
ardupilot-controllers/
├─ c1/
│  └─ ardupilot/        # ArduPilot リポジトリ (機体0用)
│     └─ build/…        # 各自のビルド成果物
└─ c2/
　  └─ ardupilot/        # ArduPilot リポジトリ (機体1用)
　     └─ build/…
```

* `c1/ardupilot` と `c2/ardupilot` は **別クローン**（またはビルド・作業ディレクトリを分ける）。
* それぞれで **ビルド** を実施。ブランチ/タグは同一にしておくと無難です。


また、`hakoniwa-drone-core/config` 以下に、以下のような**機体定義ファイル**を用意します。
(`-2` は 2 機体用の定義ファイル）

```tree
hakoniwa-drone-core/config
├── drone
│   ├── ardupilot-1 #1機分の定義ディレクトリ
│   │   └── drone_config_0.json
│   └── ardupilot-2 #2機分の定義ディレクトリ
│       ├── drone_config_0.json  #1台目
│       └── drone_config_1.json  #2台目
└── pdudef
    ├── webavatar-2.json # 2機分の定義(1台目：Drone, 2台目：Drone1)
    └── webavatar.json   # 1機分の定義
```


### ポート設計（本リポのスクリプト既定）

* 機体 `INSTANCE=i` のとき: `MAVLINK_OUT_PORT = 14550 + 10 * i`

  * 機体0 → `14550`、機体1 → `14560`
* 送信先は 2 系統

  * `udp:127.0.0.1:<PORT>`（Docker内 Python 用）
  * `udp:<HOST_IP>:<PORT>`（Mission Planner 用）

> `HOST_IP` は **ホスト（Windows 側）の IP** を指定。WSL2 の場合は注意。
> OS のファイアウォールで該当ポートの UDP を許可しておく。

---

## 実行手順

### 1) Ardupilot（WSL2）

```bash
# 機体0
bash -x hakoniwa-drone-core/tools/ardupilot/run.bash \
  ardupilot-controllers/c1/ardupilot/ <HOST_IP> 0

# 機体1
bash -x hakoniwa-drone-core/tools/ardupilot/run.bash \
  ardupilot-controllers/c2/ardupilot/ <HOST_IP> 1
```

* `HOST_IP` はホスト IP（Mission Planner が動く側）。
* **GPS が有効**になってから次へ（HOME セット等が済むまで待機）。

### 2) 箱庭（Docker）

```bash
bash hakoniwa-drone-core/docker/tools/run-hako.bash ardupilot \
  hakoniwa-drone-core/config/pdudef/webavatar-2.json 2
```

### 3) Python スクリプト（Docker 内）

```bash
cd hakoniwa-drone-core/drone_api/pymavlink

python3 -m hakosim_mavlink --name Drone  \
  --connection udp:127.0.0.1:14550 --type ardupilot

python3 -m hakosim_mavlink --name Drone1 \
  --connection udp:127.0.0.1:14560 --type ardupilot
```

### 4) 動作確認

* Mission Planner から `UDP 14550` / `UDP 14560` に接続。
* 2 機が離陸し、三角移動（隊列）することを確認。

---

## インスタンス対応表（例）

| 機体 |  MAVLink UDP (Docker内) | MAVLink UDP (MissionPlanner) | Drone名 (Python) | 設定ファイル                |
| -- | --------------------- | ---------------------------- | --------------- | --------------------- |
| 0 | 127.0.0.1:14550       | HOST\_IP:14550               | `Drone`         | `drone_config_0.json` |
| 1 | 127.0.0.1:14560       | HOST\_IP:14560               | `Drone1`        | `drone_config_1.json` |

---

