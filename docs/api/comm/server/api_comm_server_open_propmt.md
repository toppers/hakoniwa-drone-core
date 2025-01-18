# タスクの説明
## タスクの概要

本タスクでは、ICommServer の server_open API のAPI仕様書を作成します。

## 対象API

std::shared_ptr<ICommIO> server_open(ICommEndpointType *endpoint) = 0;

## 前提情報

- ユーザは、comm.hppをインクルードして利用します。
- 本APIを利用する場合は、必ず、comm_init()およびcreate()を呼び出す必要があることを注意点として記載してください。

## 入力情報

- クラス設計情報
  - [api_comm.md](https://github.com/toppers/hakoniwa-drone-core/blob/main/docs/api/comm/api_comm.md)
- API仕様書のテンプレート
  - [api-template.md](https://github.com/toppers/hakoniwa-drone-core/blob/main/docs/templates/api-template.md)
- ヘッダ情報
  - [comm.hpp](https://github.com/toppers/hakoniwa-drone-core/blob/main/include/comm.hpp)
  - [comm/icomm_connector.hpp](https://github.com/toppers/hakoniwa-drone-core/blob/main/include/comm/icomm_connector.hpp)

## タスク
- ICommServer の server_open API の API仕様書をAPI仕様書のテンプレートの書式に従って作成してください。
- API仕様書を作成する上で、クラス設計情報は大切なので、必ず参照して理解を進めてください。
- create()時に指定する通信タイプによって、適切な通信オブジェクトが生成されますので、その点も記載してください。
- 出力は、README.md形式でテキストで日本語出力してください。


