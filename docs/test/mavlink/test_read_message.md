# テスト仕様書

## IMavLinkService::readMessage
- 新しいメッセージを受信できること ... TEST001
- 受信バッファにメッセージがない場合にエラーとなること ... TEST002
- startService()を呼び出していない状態でreadMessage()を実行した場合にエラーとなること ... TEST003

---

### テストケース詳細

#### TEST001
- **概要**: 受信バッファにあるメッセージを正しく取得できることを確認する
- **条件**:
  - サービスはstartService()で開始済み
  - 送信側からHEARTBEATメッセージが送信されている
  - is_dirty: 変数参照を渡す
- **期待される結果**:
  - 戻り値: true
  - message.typeがMavlinkMsgType::HEARTBEATであること
  - is_dirtyがtrueとなること

---

#### TEST002
- **概要**: 受信バッファにメッセージがない場合の挙動を確認する
- **条件**:
  - サービスはstartService()で開始済み
  - 送信側からメッセージは送られていない
  - is_dirty: 変数参照を渡す
- **期待される結果**:
  - 戻り値: false
  - is_dirtyがfalseとなること

---

#### TEST003
- **概要**: startService()を呼び出していない状態でreadMessage()を実行した場合のエラー処理を確認する
- **条件**:
  - startService()は未呼び出し
  - is_dirty: 変数参照を渡す
- **期待される結果**:
  - 戻り値: false
  - メッセージは取得されないこと
