# テスト仕様書

## IMavLinkService::sendMessage
- 有効なMavlinkHakoMessageを送信できること ... TEST001
- MavlinkHakoMessage.typeにUNKNOWNを指定した場合にエラーとなること ... TEST002
- startService()を呼び出さずに送信した場合にエラーとなること ... TEST003
- ネットワークエラー発生時に送信失敗となること ... TEST004

---

### テストケース詳細

#### TEST001
- **概要**: HEARTBEATメッセージを指定して正常に送信できることを確認する
- **条件**:
  - message.type: MavlinkMsgType::HEARTBEAT
  - サービスはstartService()で開始済み
- **期待される結果**:
  - 戻り値: true
  - 送信先にメッセージが到達すること

---

#### TEST002
- **概要**: MavlinkHakoMessage.typeにUNKNOWNを指定した場合のエラー処理を確認する
- **条件**:
  - message.type: MavlinkMsgType::UNKNOWN
  - サービスはstartService()で開始済み
- **期待される結果**:
  - 戻り値: false
  - メッセージは送信されないこと

---

#### TEST003
- **概要**: startService()を呼び出さずにsendMessage()を実行した場合のエラー処理を確認する
- **条件**:
  - message.type: MavlinkMsgType::HEARTBEAT
  - startService()は未呼び出し
- **期待される結果**:
  - 戻り値: false
  - メッセージは送信されないこと

---

#### TEST004
- **概要**: 送信途中でネットワークエラーが発生した場合の挙動を確認する
- **条件**:
  - message.type: MavlinkMsgType::HEARTBEAT
  - サービスはstartService()で開始済み
  - 送信先との通信を遮断する
- **期待される結果**:
  - 戻り値: false
  - エラーログが出力されること
