# ICommIO Prompts

## API Documentation Prompt

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
  - [api-template.md](https://github.com/toppers/hakoniwa-drone-core/blob/main/docs/prompts/api-template.md)
- ヘッダ情報
  - [comm.hpp](https://github.com/toppers/hakoniwa-drone-core/blob/main/include/comm.hpp)

## タスク
- ICommIO の API仕様書をAPI仕様書のテンプレートの書式に従って作成してください。
- API仕様書を作成する上で、クラス設計情報は大切なので、必ず参照して理解を進めてください。
- create()時に指定する通信タイプによって、適切な通信オブジェクトが生成されますので、その点も記載してください。
- コード例をAPI毎に書くと冗長になるので、まとめて書いてください。
- 出力は、README.md形式でテキストで日本語出力してください。



## Test Spec Prompt (send API)

1. タスクの説明：
AIを利用して、API仕様から効率的にテストケースを設計・生成したいと考えています。  
オーバービュー：ai-colab-overview.png
対象API: send API  
API仕様：README.md

comm.hppおよび関連するヘッダファイルを渡します。  
send APIのAPI仕様書を基に、テスト仕様書を作成してください。  

出力は、テキスト形式で日本語で記載してください。README.md形式で構成してください。

テンプレートの書式：../../test-template.md を参照してください。

2. テストの意図：
- 正常系: 有効な引数を与えた場合に成功すること。
- 異常系: 
  - NULLポインタを渡した場合。
  - データ長が負の場合。
  - send_datalenがNULLの場合。

3. テストの対象API：
virtual bool send(const char* data, int datalen, int* send_datalen) = 0;


## Test Spec Prompt (recv API)

1. タスクの説明：
AIを利用して、API仕様から効率的にテストケースを設計・生成したいと考えています。

オーバービュー：ai-colab-overview.png
対象API: recv API
API仕様：README.md

comm.hppおよび関連するヘッダファイルを渡します。
recv APIのAPI仕様書を基に、テスト仕様書を作成してください。

出力は、テキスト形式で日本語で記載してください。README.md形式で構成してください。

テンプレートの書式：../../test-template.md を参照してください。

2. テストの意図：
- 正常系: 有効な引数を与えた場合に成功すること。
- 異常系:
  - NULLポインタを渡した場合。
  - データ長が負の場合。
  - recv_datalenがNULLの場合。

3. テストの対象API：
virtual bool recv(char* data, int datalen, int* recv_datalen) = 0;

## Test Code Prompt

1. タスクの説明：
AIを利用して、テスト仕様から効率的にテストコードを生成したいと考えています。  
対象API: send API  
ヘッダ：comm.hppおよび関連するヘッダファイルを渡します。  
テスト仕様：README.md形式で渡します。

以下のテンプレートに従って、テストコードを生成してください。

2. テンプレートの書式：../../test-code-template.cpp を参照してください。

3. テスト条件：

- データ送信するための初期化処理を事前に行なってください。
- データ送信前にサーバー側を事前に起動してください。
- server_open するとブロックされますので、別スレッドで起動してください。
- マルチスレッドでのテストであるため、スレッドセーフな実装を行なってください。
- テスト終了後は、スレッドの待ち合わせおよび、リソースの解放処理を行なってください。
- Google Testを利用してください。
