# タスクの説明
## タスクの概要

本タスクでは、 ICommIO のAPI仕様書を作成します。

## 対象API

- bool send(const char* data, int datalen, int* send_datalen) = 0;
- bool recv(char* data, int datalen, int* recv_datalen) = 0;
- bool close() = 0;

## 前提情報

- ユーザは、comm.hppをインクルードして利用します。
- 本APIを利用する場合は、必ず、comm_init()およびcreate()を呼び出す必要があることを注意点として記載してください。
- 本APIは仮想関数であり、実際の実装はICommServerもしくはICommClientのcreate()で生成されたインスタンスによって提供されます。
- 送信データのバッファは、呼び出し元で適切に確保・解放する必要があります。
- TCPの場合、データの到達保証があるが、UDPの場合は到達保証がないことを注意点として記載してください。
- TCPの場合、実際に送信されたデータ長は、要求された送信長（datalen）よりも小さい場合がありますが、本API仕様として、通信の一時的なエラーが発生した場合、リトライしてdatalenまで送信することを記載してください。
- TCPの場合、データ送信の場合と同様に、データ受信の場合も、実際に受信されたデータ長は、要求された受信長（datalen）よりも小さい場合がありますが、本API仕様として、通信の一時的なエラーが発生した場合、リトライしてdatalenまで受信することを記載してください。

## 入力情報

- クラス設計情報
  - [api_comm.md](https://github.com/toppers/hakoniwa-drone-core/blob/main/docs/api/comm/api_comm.md)
- API仕様書のテンプレート
  - [api-template.md](https://github.com/toppers/hakoniwa-drone-core/blob/main/docs/templates/api-template.md)
- ヘッダ情報
  - [comm.hpp](https://github.com/toppers/hakoniwa-drone-core/blob/main/include/comm.hpp)
  - [comm/icomm_connector.hpp](https://github.com/toppers/hakoniwa-drone-core/blob/main/include/comm/icomm_connector.hpp)
- 共通プロンプト
  - [api_comm_prompt.md](https://github.com/toppers/hakoniwa-drone-core/blob/main/docs/api/comm/api_comm_prompt.md)

## タスク
- [api_comm_prompt.md](https://github.com/toppers/hakoniwa-drone-core/blob/main/docs/api/comm/api_comm_prompt.md)を参照してください。
- ICommIO の API仕様書をAPI仕様書のテンプレートの書式に従って作成してください。
- API仕様書を作成する上で、クラス設計情報は大切なので、必ず参照して理解を進めてください。
- create()時に指定する通信タイプによって、適切な通信オブジェクトが生成されますので、その点も記載してください。
- コード例をAPI毎に書くと冗長になるので、まとめて書いてください。
- 出力は、README.md形式でテキストで日本語出力してください。


