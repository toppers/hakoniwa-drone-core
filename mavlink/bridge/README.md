# これは何？

**Mavlink 箱庭ブリッジ(箱庭アセット)** です。

Mission Planner からの転送される Mavlink UDPパケットを受信して、Vehicle の位置情報およびサーボ情報を元に、箱庭PDUデータとして書き込みします。


箱庭PDUデータに書き込みすると、箱庭アセットがそれらの情報を読み込みすることができますので、様々な展開が可能にアンリます。

例えば、箱庭Unityアセットを使えば、箱庭の中で Vehicle をドローンとして再現し、Unity空間の中で飛ばすことができます。

# 前提条件

本機能を利用するためには、箱庭ドローンシミュレータを事前にインストールしておく必要があります。

# インストール

```bash
cd hakoniwa-drone-core/mavlink
pip install -r requirements.txt
```

# 使い方

```bash
cd hakoniwa-drone-core/mavlink/bridge
```

```bash
python main.py --mavlink-config ../test_data/mavlink-custom.json --pdu-config ../test_data/custom.json --comm-config ../test_data/vehicle_comm.json udp 192.168.2.100:54001
```
- `--mavlink-config` : Mavlink設定ファイル
- `--pdu-config` : 箱庭PDU設定ファイル
- `--comm-config` : 通信設定ファイル
- `udp` : UDP通信を利用する場合、Mavlink箱庭ブリッジを起動するIPアドレスと受信ポート番号を指定します。


## レジトリ設定

Mavlink データを箱庭PDUデータに変換するための設定ファイルを指定することができます。

- registry/listen.py
  - リッスンするMavlinkパケットを指定します。
- registry/conv.py
  - 受信したMavlinkパケットを箱庭PDUデータに変換するための関数を指定します。


## 通信設定ファイル

Mission Plannner のIPアドレスと転送先のポート番号を指定します。対象エントリは、`vehicles` 内に設定します。エントリ名は、箱庭内のロボット名としてください。

また、転送先のポート番号は、Mavlink箱庭ブリッジを起動する際に指定したポート番号と一致している必要があります。

- ip_address：Mission Planner のIPアドレス
- port：Mission Planner からの転送ポート番号

また、Vehicle の初期位置を緯度経度高度で指定します。

- latitude：緯度、データ型はint32
- longitude：経度、データ型はint32
- altitude：高度、データ型はfloat32

設定例：
```json
{
    "vehicles": {
        "DroneAvatar": {
            "ip_address": "192.168.2.105",
            "port": 54001,
            "initial_position": {
                "latitude": -353632621,
                "longitude": 1491652374,
                "altitude": 584.0899658203125
            }
        }
    }
}
```

## Mavlink設定ファイル

箱庭のロボット名、および、受信するMavlinkパケットの種類を指定します。

`ロボット名` と `type` を指定してください。

設定例：
```json
{
    "robots": [
    {
      "name": "DroneAvatar",
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

## 箱庭PDU設定ファイル

Mavlinkパケットを箱庭PDUデータとして定義します。
ただし、MavlinkパケットをROSデータ型に変換する場合は、そのデータを指定してください。

```json
{
    "robots": [
    {
      "name": "DroneAvatar",
      "rpc_pdu_readers": [],
      "rpc_pdu_writers": [],
      "shm_pdu_readers": [
        {
          "type": "geometry_msgs/Twist",
          "org_name": "pos",
          "name": "DroneAvatar_pos",
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
          "name": "DroneAvatar_motor",
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

