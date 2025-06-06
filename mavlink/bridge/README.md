# Mavlink 箱庭ブリッジ (箱庭アセット)

## これは何？

**Mavlink 箱庭ブリッジ**は、Mission Planner から送信される Mavlink UDP パケットを受信し、Vehicle の位置情報およびサーボ情報を箱庭 PDU データとして書き込みます。

これにより、以下のような利用が可能になります：
- **箱庭 Unity アセット**を使うことで、Unity 空間で Vehicle をドローンとして再現し、仮想環境内でビジュアライズ可能。
- 他の箱庭シミュレーションシステムとのデータ連携やカスタマイズが容易。

---

## 前提条件

以下を事前に準備してください：
1. [箱庭ドローンシミュレータ](https://github.com/toppers/hakoniwa-px4sim) をインストールしてください。
2. Mission Planner からの UDP パケットを送信する設定を行ってください。

---

## インストール

Python 環境を用意し、以下のコマンドで必要なライブラリをインストールします。

```bash
cd hakoniwa-drone-core/mavlink
pip install -r requirements.txt
```

---

## 使い方

以下のコマンドで Mavlink 箱庭ブリッジを起動します：

```bash
cd hakoniwa-drone-core/mavlink/bridge
python main.py --mavlink-config ../test_data/mavlink-custom.json --pdu-config ../test_data/custom.json --comm-config ../test_data/vehicle_comm.json udp 192.168.2.100
```

### コマンドオプション
- `--mavlink-config` : Mavlink 設定ファイルを指定します。
- `--pdu-config` : 箱庭 PDU 設定ファイルを指定します。
- `--comm-config` : 通信設定ファイルを指定します。
- `udp` : UDP 通信を使用する場合の IP アドレスを指定します（例: `192.168.2.100`）。

---

## 設定ファイルについて

### 通信設定ファイル

Mission Planner の IP アドレス、転送ポート番号、Vehicle の初期位置を指定します。

#### 設定例:
```json
{
    "vehicles": {
        "Drone": {
            "ip_address": "192.168.2.105",
            "port": 54001,
            "my_port": 54001,
            "initial_position": {
                "latitude": -353632621,
                "longitude": 1491652374,
                "altitude": 584.0899658203125
            }
        },
        "Rover": {
            "ip_address": "192.168.2.107",
            "port": 54002,
            "my_port": 54002,
            "initial_position": {
                "latitude": -353632621,
                "longitude": 1491652374,
                "altitude": 584.0899658203125,
                "fixed_altitude": {
                    "value": 0
                }
            }
        }
    }
}
```

**説明**：
`vehicles` コンテナ配下に、各 Vehicle の設定を記述します。

ロボットの名前をコンテナ名として以下の情報を記述します：

- `ip_address`: Mission Planner の IP アドレスを指定してください。このIPアドレスにマッチしないデータは無視されます。マッチした場合は、当該コンテナの名前をロボット名として扱います。
- `port`: Mission Planner の送信先ポート番号。
- `my_port`: 本ツールを起動するマシンのポート番号。portと同じ番号としてください。
- `initial_position`: Vehicle の初期位置（緯度・経度・高度）を指定。
  - `latitude`: 緯度。
  - `longitude`: 経度。
  - `altitude`: 高度。
  - `fixed_altitude`: 高度固定値を指定する場合は、`value` に高度値を指定してください。

---

### Mavlink 設定ファイル

受信する Mavlink パケットの種類を指定します。

#### 設定例:
```json
{
    "robots": [
    {
      "name": "Drone",
      "shm_pdu_readers": [
        {
        "type": "hako_mavlink_msgs/HakoSERVO_OUTPUT_RAW"
        },
        {
        "type": "hako_mavlink_msgs/HakoAHRS2"
        }
       ],
       "shm_pdu_writers": []
    },
    {
      "name": "Rover",
      "shm_pdu_readers": [
        {
        "type": "hako_mavlink_msgs/HakoSERVO_OUTPUT_RAW"
        },
        {
        "type": "hako_mavlink_msgs/HakoAHRS2"
        }
       ],
       "shm_pdu_writers": []
    }
    ]
}
```

**説明**：
- `name`: Vehicle 名称（箱庭内のロボット名と一致）。
- `type`: 受信する Mavlink パケットの種類。

---

### 箱庭 PDU 設定ファイル

Mavlink パケットを箱庭 PDU データとして定義します。データ型の変換には、必要に応じて ROS メッセージ型を指定してください。

#### 設定例:
```json
{
    "robots": [
    {
      "name": "Drone",
      "rpc_pdu_readers": [],
      "rpc_pdu_writers": [],
      "shm_pdu_readers": [
        {
          "type": "geometry_msgs/Twist",
          "org_name": "pos",
          "name": "Drone_pos",
          "class_name": "Hakoniwa.PluggableAsset.Communication.Pdu.Raw.RawPduReader",
          "conv_class_name": "Hakoniwa.PluggableAsset.Communication.Pdu.Raw.RawPduReaderConverter",
          "channel_id": 0,
          "pdu_size": 72,
          "write_cycle": 1,
          "method_type": "SHM"
        },
        {
          "type": "hako_mavlink_msgs/HakoHilActuatorControls",
          "org_name": "motor",
          "name": "Drone_motor",
          "class_name": "Hakoniwa.PluggableAsset.Communication.Pdu.Raw.RawPduReader",
          "conv_class_name": "Hakoniwa.PluggableAsset.Communication.Pdu.Raw.RawPduReaderConverter",
          "channel_id": 1,
          "pdu_size": 112,
          "write_cycle": 1,
          "method_type": "SHM"
        }
      ],
      "shm_pdu_writers": []
    },
    {
      "name": "Rover",
      "rpc_pdu_readers": [],
      "rpc_pdu_writers": [],
      "shm_pdu_readers": [
        {
          "type": "geometry_msgs/Twist",
          "org_name": "pos",
          "name": "Drone_pos",
          "class_name": "Hakoniwa.PluggableAsset.Communication.Pdu.Raw.RawPduReader",
          "conv_class_name": "Hakoniwa.PluggableAsset.Communication.Pdu.Raw.RawPduReaderConverter",
          "channel_id": 0,
          "pdu_size": 72,
          "write_cycle": 1,
          "method_type": "SHM"
        },
        {
          "type": "hako_mavlink_msgs/HakoHilActuatorControls",
          "org_name": "motor",
          "name": "Drone_motor",
          "class_name": "Hakoniwa.PluggableAsset.Communication.Pdu.Raw.RawPduReader",
          "conv_class_name": "Hakoniwa.PluggableAsset.Communication.Pdu.Raw.RawPduReaderConverter",
          "channel_id": 1,
          "pdu_size": 112,
          "write_cycle": 1,
          "method_type": "SHM"
        }
      ],
      "shm_pdu_writers": []
      }    
    ]
}
```

**説明**：
- `type`: PDU のデータ型（例: `geometry_msgs/Twist`）。
- `channel_id`: データを識別するためのチャネル ID。
- `pdu_size`: PDU データサイズ。
- `write_cycle`: 書き込みサイクル。

---

## レジストリ設定

### `registry/listen.py`
受信する Mavlink パケットを定義します。

### `registry/conv.py`
受信した Mavlink パケットを箱庭 PDU データに変換する関数を指定します。

---

## 注意事項

- Mission Planner の設定で、UDP 通信が有効になっていることを確認してください。
- 各設定ファイルで指定したポート番号が正しいことを確認してください。

