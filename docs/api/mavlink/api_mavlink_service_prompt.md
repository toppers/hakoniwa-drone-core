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
  - [api-template.md](https://github.com/toppers/hakoniwa-drone-core/blob/main/docs/templates/api-template.md)
- ヘッダ情報
  - [mavlink.hpp](https://github.com/toppers/hakoniwa-drone-core/blob/main/include/mavlink.hpp)

## タスク
- API仕様書をAPI仕様書のテンプレートの書式に従って作成してください。
- API仕様書を作成する上で、クラス設計情報は大切なので、必ず参照して理解を進めてください。
- create()時に指定する通信タイプによって、適切な通信オブジェクトが生成されますので、その点も記載してください。
- コード例をAPI毎に書くと冗長になるので、まとめて書いてください。
- 出力は、README.md形式でテキストで日本語出力してください。

