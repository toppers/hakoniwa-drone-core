# MAVLink Service API仕様書

## 概要

本APIは、MAVLinkプロトコルを使用した通信サービスを提供します。本サービスは基本的にサーバーとして動作し、接続が確立されてからメッセージの送受信が可能になります。サービスの作成、メッセージの送受信、およびサービスの制御機能を提供します。

### MAVPROXYへの自発的送信

通常、本サービスはサーバーとして動作するため、接続確立前にメッセージを送信することはできません。しかし、MAVPROXYのような特定のクライアントに対しては、自発的にメッセージを送信する機能が提供されています。この場合、`HakoMavLinkProtocolConfigType` の設定は不要です。

この機能を利用するには、`MavLinkServiceContainer::addService` メソッドを使用するか、`sendMessage` メソッドの引数で `MAVPROXY` を指定します。これにより、サービスは接続確立を待たずにMAVPROXYへメッセージを送信できます。

**注意点**: この自発的送信機能は、MAVPROXYへの送信のみをサポートしており、MAVPROXYからのメッセージ受信はサポートしていません。

## 前提条件

- C++11以上の開発環境
- `mavlink.hpp`をインクルードすること

### 型

#### **MavLinkServiceDesitinationType**
メッセージ送信先を表す列挙体です。`sendMessage()` 等で利用します。

- `SITL` : シミュレータ(PX4/Ardupilot)への送信
- `MAVPROXY` : MAVProxyクライアントへの送信

#### **MavLinkUserCustomDecoderType**
ユーザー定義デコード処理を登録するための構造体です。
- `type` : 対象となるMAVLinkメッセージタイプ
- `user_custom_decode` : 生データを `MavlinkHakoMessage` に変換する関数ポインタ

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

##### addMavProxyClient

```cpp
bool addMavProxyClient(MavlinkServiceIoType io_type,
                       const IMavlinkCommEndpointType& mavproxy_endpoint);
```

**説明**
MAVProxyクライアントへの送信先を追加登録します。

**パラメータ**
- `io_type`: MAVProxyとの通信方式 (TCP/UDP)
- `mavproxy_endpoint`: MAVProxy側のエンドポイント情報

**戻り値**
- `true`: 登録成功
- `false`: 登録失敗

##### setReceiverCallback

```cpp
bool setReceiverCallback(IMavLinkServiceCallback& callback);
```

**説明**
メッセージ受信時に呼び出されるコールバックを設定します。

**パラメータ**
- `callback`: 受信通知を受け取るコールバックオブジェクト

**戻り値**
- `true`: 設定成功
- `false`: 設定失敗

##### sendMessage

```cpp
bool sendMessage(MavLinkServiceDesitinationType destination,
                 MavlinkHakoMessage& message);
bool sendMessage(MavlinkHakoMessage& message);
```

**説明**
- `MavlinkHakoMessage` の `type` を必ず指定してください。
- 送信先を明示したい場合は第一引数に `destination` を指定します。
- 引数を 1 つだけ指定した場合は `SITL` 宛てに送信されます。

**パラメータ**
- `destination`: 送信先種別 (`SITL` または `MAVPROXY`)
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

##### setUserCustomDecoder

```cpp
bool setUserCustomDecoder(MavLinkUserCustomDecoderType decoder);
```

**説明**
ユーザー定義のデコード処理を登録します。標準フォーマットに当てはまらない受信データを解析したい場合に使用します。

**パラメータ**
- `decoder`: デコード設定を格納した構造体

**戻り値**
- `true`: 設定成功
- `false`: 設定失敗

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

// MAVPROXYへの自発的送信を含む使用例
// main_aircraft_service_ardupilot.cpp からの抜粋
#define HAKO_MAVLINK_BRIDGE_PORTNO 54001

// ... (省略: サービスの初期化と設定) ...

    auto mavlink_service_container = std::make_shared<MavLinkServiceContainer>();
    for (int i = 0; i < aircraft_num; i++) {
        std::cout << "INFO: aircraft_num=" << i << std::endl;
        IMavlinkCommEndpointType server_endpoint = {server_ip, server_port + i};
        IMavlinkCommEndpointType client_endpoint = {server_ip, client_port + i};
        auto mavlink_service = IMavLinkService::create(i, MavlinkServiceIoType::UDP, &server_endpoint, &client_endpoint);
        // MAVPROXYクライアントの追加
        mavlink_service->addMavProxyClient(MavlinkServiceIoType::UDP, {server_ip, HAKO_MAVLINK_BRIDGE_PORTNO});
        mavlink_service_container->addService(mavlink_service);
    }

    // ... (省略: aircraft_serviceの初期化) ...

    HakoMavLinkProtocolConfigType protocol_config = {};
    protocol_config.rx.msg_id = MavlinkMsgType::HIL_ACTUATOR_CONTROLS;
    protocol_config.rx.user_custom_decode = user_custom_decode;
    protocol_config.tx.push_back({MavlinkMsgType::USER_CUSTOM, 3000, MavLinkServiceDesitinationType::SITL, user_custom_encode});
    // MAVPROXYへのメッセージ送信設定
    protocol_config.tx.push_back({MavlinkMsgType::SERVO_OUTPUT_RAW, 100000, MavLinkServiceDesitinationType::MAVPROXY, nullptr});
    protocol_config.tx.push_back({MavlinkMsgType::AHRS2, 20000, MavLinkServiceDesitinationType::MAVPROXY, nullptr});
    if (!aircraft_service->setProtocolConfig(protocol_config)) {
        std::cerr << "[ERROR] Failed to set MAVLink protocol config." << std::endl;
    }
// ... (省略: サービスの開始とループ) ...
```

## HakoMavLinkProtocolConfigType

MAVLinkプロトコルの送受信設定を定義する構造体です。`IAircraftServiceContainer::setProtocolConfig` メソッドで使用されます。

```cpp
typedef struct {
    HakoMavLinkProtocolRxConfigType rx;
    std::vector<HakoMavLinkProtocolTxConfigType> tx;
} HakoMavLinkProtocolConfigType;
```

**メンバー**
- `rx`: 受信メッセージの設定 (`HakoMavLinkProtocolRxConfigType`)
- `tx`: 送信メッセージの設定のリスト (`std::vector<HakoMavLinkProtocolTxConfigType>`)

### HakoMavLinkProtocolRxConfigType

受信メッセージの設定を定義する構造体です。主に、受信したパケットが標準のMAVLinkパケット形式に合致しない場合に、カスタムデコーダを定義するために使用されます。

```cpp
typedef struct {
    hako::mavlink::MavlinkMsgType msg_id;
    bool (*user_custom_decode) (int index, const void* data, int detalen, hako::mavlink::MavlinkHakoMessage& message);
} HakoMavLinkProtocolRxConfigType;
```

**メンバー**
- `msg_id`: 受信するMAVLinkメッセージのタイプ。
- `user_custom_decode`: ユーザー定義のデコード関数へのポインタ。受信した生データを `MavlinkHakoMessage` に変換するために使用されます。

### HakoMavLinkProtocolTxConfigType

送信メッセージの設定を定義する構造体です。主に、MAVPROXYへの定期的なメッセージ送信設定に使用されます。

```cpp
typedef struct {
    hako::mavlink::MavlinkMsgType msg_id;
    uint64_t send_cycle_usec;
    mavlink::MavLinkServiceDesitinationType destination;
    bool (*user_custom_encode) (aircraft::IAirCraft& aircraft, hako::mavlink::MavlinkHakoMessage& message, uint64_t time_usec);
} HakoMavLinkProtocolTxConfigType;
```

**メンバー**
- `msg_id`: 送信するMAVLinkメッセージのタイプ。
- `send_cycle_usec`: メッセージを送信する周期（マイクロ秒単位）。
- `destination`: メッセージの送信先 (`MavLinkServiceDesitinationType::SITL` または `MavLinkServiceDesitinationType::MAVPROXY`)。
- `user_custom_encode`: ユーザー定義のエンコード関数へのポインタ。`IAirCraft` のデータから `MavlinkHakoMessage` を生成するために使用されます。



各メソッドは、操作が失敗した場合にfalseを返します。エラーの詳細は、実装依存のログ機能を通じて提供されます。


## パフォーマンスに関する考慮事項

- `sendMessage`と`readMessage`は非ブロッキング操作として実装されています。
- サービスの開始/停止操作は比較的時間のかかる処理となる可能性があります。
