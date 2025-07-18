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
