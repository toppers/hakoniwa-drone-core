# Mavlink Prompts

## API Class Design Prompt

# タスクの説明
## タスクの概要

本タスクでは、[mavlink.hpp](https://github.com/toppers/hakoniwa-drone-core/blob/main/include/mavlink.hpp) のクラス設計情報を作成します。

クラス設計情報としては、以下の情報を整理します。

- クラス概要
- クラス図
- シーケンス図
- API リファレンスへの参照（リンクは不要です）

ドキュメントとしては、以下を参考にしてください。

https://github.com/toppers/hakoniwa-drone-core/blob/main/docs/api/comm/api_comm.md


## 対象

- MavlinkServiceIoType
- MavlinkMsgType
- MavlinkHakoMessage
- IMavlinkCommEndpointType
- IMavLinkService
- MavLinkServiceContainer

## 前提情報

- ユーザは、最初にMavLinkServiceContainerをインスタンス化します。
- 次に、IMavLinkServiceを create() で生成します。
- この際に、インスタンスのインデックス番号(0からの連番)とserver_endpointとclient_endpointを指定します。
- server_endpointは、自分がTCP \UDPのサーバーとしてのIPアドレスとポート番号を指定します。
- client_endpointは、自分がTCP \UDPのクライアントとしてのIPアドレスとポート番号を指定します。nullptrを指定すると、自動採番されます。
- 生成したIMavLinkServiceを、MavLinkServiceContainerに登録します。

## Service API Prompt

# タスクの説明
## タスクの概要

本タスクでは、IMavlinkService および MavlinkServiceContainer API のAPI仕様書を作成します。

## 対象API

- IMavLinkService
  - static std::shared_ptr<IMavLinkService> create(int index, MavlinkServiceIoType io_type, const IMavlinkCommEndpointType *server_endpoint, const IMavlinkCommEndpointType *client_endpoint);
  - bool sendMessage(MavlinkHakoMessage& message) = 0;
  - bool readMessage(MavlinkHakoMessage& message, bool &is_dirty) = 0;
  - bool startService() = 0;
  - void stopService() = 0;
- MavLinkServiceContainer
  - void addService(std::shared_ptr<IMavLinkService> service)
  - std::vector<std::shared_ptr<IMavLinkService>>& getServices()

## 前提情報

- ユーザは、mavlink.hppをインクルードして利用します。

## 入力情報

- クラス設計情報
  - [api_mavlink.md](https://github.com/toppers/hakoniwa-drone-core/blob/main/docs/api/mavlink/api_mavlink.md)
- API仕様書のテンプレート
  - [api-template.md](https://github.com/toppers/hakoniwa-drone-core/blob/main/docs/prompts/api-template.md)
- ヘッダ情報
  - [mavlink.hpp](https://github.com/toppers/hakoniwa-drone-core/blob/main/include/mavlink.hpp)

## タスク
- API仕様書をAPI仕様書のテンプレートの書式に従って作成してください。
- API仕様書を作成する上で、クラス設計情報は大切なので、必ず参照して理解を進めてください。
- create()時に指定する通信タイプによって、適切な通信オブジェクトが生成されますので、その点も記載してください。
- コード例をAPI毎に書くと冗長になるので、まとめて書いてください。
- 出力は、README.md形式でテキストで日本語出力してください。

## Test Spec Prompt (sendMessage API)

1. タスクの説明：
AIを利用して、API仕様から効率的にテストケースを設計・生成したいと考えています。

オーバービュー：ai-colab-overview.png
対象API: sendMessage API
API仕様：README.md

mavlink.hppおよび関連するヘッダファイルを渡します。
sendMessage APIのAPI仕様書を基に、テスト仕様書を作成してください。

出力は、テキスト形式で日本語で記載してください。README.md形式で構成してください。

テンプレートの書式：../../test-template.md を参照してください。

2. テストの意図：
- 正常系: 有効なMavlinkHakoMessageを指定して送信に成功すること。
- 異常系:
  - MavlinkHakoMessage.typeにUNKNOWNを指定した場合。
  - startService()を呼び出していない状態で送信した場合。
  - ネットワークエラーが発生した場合。

3. テストの対象API：
bool sendMessage(MavlinkHakoMessage& message) = 0;

## Test Spec Prompt (readMessage API)

1. タスクの説明：
AIを利用して、API仕様から効率的にテストケースを設計・生成したいと考えています。

オーバービュー：ai-colab-overview.png
対象API: readMessage API
API仕様：README.md

mavlink.hppおよび関連するヘッダファイルを渡します。
readMessage APIのAPI仕様書を基に、テスト仕様書を作成してください。

出力は、テキスト形式で日本語で記載してください。README.md形式で構成してください。

テンプレートの書式：../../test-template.md を参照してください。

2. テストの意図：
- 正常系: 新しいメッセージを受信できること。
- 異常系:
  - 受信バッファにメッセージがない場合。
  - startService()を呼び出していない状態でreadMessage()を実行した場合。

3. テストの対象API：
bool readMessage(MavlinkHakoMessage& message, bool &is_dirty) = 0;

## Test Code Prompt (sendMessage API)

1. タスクの説明：
AIを利用して、テスト仕様から効率的にテストコードを生成したいと考えています。
対象API: sendMessage API
ヘッダ：mavlink.hppおよび関連するヘッダファイルを渡します。
テスト仕様：README.md形式で渡します。

以下のテンプレートに従って、テストコードを生成してください。

2. テンプレートの書式：../../test-code-template.cpp を参照してください。

3. テスト条件：

- MavLinkServiceContainerおよびIMavLinkServiceの初期化を事前に行なってください。
- sendMessageをテストする際は、startService()を呼び出して通信を開始してください。
- ネットワークI/Oは別スレッドで処理し、テスト終了後にサービスを停止してリソースを解放してください。
- Google Testを利用してください。

## Test Code Prompt (readMessage API)

1. タスクの説明：
AIを利用して、テスト仕様から効率的にテストコードを生成したいと考えています。
対象API: readMessage API
ヘッダ：mavlink.hppおよび関連するヘッダファイルを渡します。
テスト仕様：README.md形式で渡します。

以下のテンプレートに従って、テストコードを生成してください。

2. テンプレートの書式：../../test-code-template.cpp を参照してください。

3. テスト条件：

- MavLinkServiceContainerおよびIMavLinkServiceの初期化を事前に行なってください。
- readMessageをテストする際は、startService()を呼び出して通信を開始してください。
- ネットワークI/Oは別スレッドで処理し、テスト終了後にサービスを停止してリソースを解放してください。
- Google Testを利用してください。

