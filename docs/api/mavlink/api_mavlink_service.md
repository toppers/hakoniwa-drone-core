# MAVLink Service API仕様書

## 概要

本APIは、MAVLinkプロトコルを使用した通信サービスを提供します。サービスの作成、メッセージの送受信、およびサービスの制御機能を提供します。

## 前提条件

- C++11以上の開発環境
- `mavlink.hpp`をインクルードすること

## クラス

### IMavLinkService

MAVLink通信サービスのインターフェースを提供します。

#### メソッド

##### create

```cpp
static std::shared_ptr<IMavLinkService> create(
    int index,
    MavlinkServiceIoType io_type,
    const IMavlinkCommEndpointType *server_endpoint,
    const IMavlinkCommEndpointType *client_endpoint
);
```

**説明**  
MAVLinkサービスのインスタンスを生成します。

**パラメータ**
- `index`: サービスの識別子
- `io_type`: 通信タイプ（TCP/UDP/SERIAL）
- `server_endpoint`: サーバー側エンドポイント情報
- `client_endpoint`: クライアント側エンドポイント情報

**戻り値**  
生成されたMAVLinkサービスインスタンス

**備考**  
指定された`io_type`に応じて、以下の通信オブジェクトが生成されます：
- `TCP`: TCPベースの通信
- `UDP`: UDPベースの通信

##### sendMessage

```cpp
bool sendMessage(MavlinkHakoMessage& message);
```

**説明**  
- MavlinkHakoMessageのtypeを必ず指定してください。
- 指定されたMAVLinkメッセージデータを送信します。

**パラメータ**
- `message`: 送信するMAVLinkメッセージ

**戻り値**
- `true`: 送信成功
- `false`: 送信失敗

##### readMessage

```cpp
bool readMessage(MavlinkHakoMessage& message, bool &is_dirty);
```

**説明**  
- MavlinkHakoMessageのtypeを必ず指定してください。
- 指定されたMAVLinkメッセージデータを受信バッファから取得します。

**パラメータ**
- `message`: 受信したメッセージを格納する変数
- `is_dirty`: メッセージが新規データかどうかを示すフラグ

**戻り値**
- `true`: 受信成功
- `false`: 受信失敗

##### startService

```cpp
bool startService();
```

**説明**  
MAVLinkサービスを開始します。

**戻り値**
- `true`: 開始成功
- `false`: 開始失敗

##### stopService

```cpp
void stopService();
```

**説明**  
MAVLinkサービスを停止します。

### MavLinkServiceContainer

複数のMAVLinkサービスを管理するコンテナクラス。

#### メソッド

##### addService

```cpp
void addService(std::shared_ptr<IMavLinkService> service);
```

**説明**  
MAVLinkサービスをコンテナに追加します。

**パラメータ**
- `service`: 追加するMAVLinkサービスインスタンス

##### getServices

```cpp
std::vector<std::shared_ptr<IMavLinkService>>& getServices();
```

**説明**  
登録されているMAVLinkサービスの一覧を取得します。

**戻り値**  
MAVLinkサービスインスタンスのベクター

## 使用例

```cpp
#include "mavlink.hpp"

// MAVLinkサービスの作成（TCP通信の場合）
auto tcp_endpoint_server = MavlinkTcpEndpoint("127.0.0.1", 14550);
auto tcp_endpoint_client = MavlinkTcpEndpoint("127.0.0.1", 14551);
auto service = IMavLinkService::create(
    0,
    TCP,
    &tcp_endpoint_server,
    &tcp_endpoint_client
);

// サービスコンテナの作成と登録
MavLinkServiceContainer container;
container.addService(service);

// サービスの開始
service->startService();

// メッセージの送受信
MavlinkHakoMessage message;
message.type = MavlinkMsgType::HIL_SENSOR;
message.data.hil_sensor.time_usec = 123456789;
message.data.hil_sensor.xacc = 1.0f;
message.data.hil_sensor.yacc = 2.0f;
message.data.hil_sensor.zacc = 3.0f;
message.data.hil_sensor.xgyro = 4.0f;
message.data.hil_sensor.ygyro = 5.0f;
message.data.hil_sensor.zgyro = 6.0f;
message.data.hil_sensor.xmag = 7.0f;
message.data.hil_sensor.ymag = 8.0f;
message.data.hil_sensor.zmag = 9.0f;
auto ret = service.sendMessage(message);


MavlinkHakoMessage actuator_message;
actuator_message.type = MavlinkMsgType::HIL_ACTUATOR_CONTROLS;
bool is_dirty;
ret = service.readMessage(actuator_message, is_dirty);

// サービスの停止
service->stopService();
```

## エラー処理

各メソッドは、操作が失敗した場合にfalseを返します。エラーの詳細は、実装依存のログ機能を通じて提供されます。


## パフォーマンスに関する考慮事項

- `sendMessage`と`readMessage`は非ブロッキング操作として実装されています。
- サービスの開始/停止操作は比較的時間のかかる処理となる可能性があります。
