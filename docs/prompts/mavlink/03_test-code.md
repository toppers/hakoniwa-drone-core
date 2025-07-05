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

