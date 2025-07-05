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
