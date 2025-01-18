# テスト仕様書

## ICommIO::send
- 正常なデータ送信が成功すること ... TEST001
- データポインタがNULLの場合にエラーとなること ... TEST002
- データ長が負の値の場合にエラーとなること ... TEST003
- send_datalenポインタがNULLの場合にエラーとなること ... TEST004

---

### テストケース詳細

#### TEST001
- **概要**: 有効なデータを指定して送信が成功することを確認する
- **条件**:
  - data: "test data" （有効な文字列データ）
  - datalen: 9 （データ長）
  - send_datalen: 有効なint型ポインタ
  - 前提条件:
    - comm_init()が実行済みであること
    - ICommServerまたはICommClientが正常に生成されていること
- **期待される結果**:
  - 戻り値: true
  - *send_datalenに実際に送信されたバイト数が設定されること
  - *send_datalenの値がdatalenと同じか、それ以下であること

---

#### TEST002
- **概要**: データポインタにNULLを指定した場合のエラー処理を確認する
- **条件**:
  - data: NULL
  - datalen: 10
  - send_datalen: 有効なint型ポインタ
  - 前提条件:
    - comm_init()が実行済みであること
    - ICommServerまたはICommClientが正常に生成されていること
- **期待される結果**:
  - 戻り値: false
  - *send_datalenが更新されないこと

---

#### TEST003
- **概要**: データ長に負の値を指定した場合のエラー処理を確認する
- **条件**:
  - data: 有効なデータポインタ
  - datalen: -1
  - send_datalen: 有効なint型ポインタ
  - 前提条件:
    - comm_init()が実行済みであること
    - ICommServerまたはICommClientが正常に生成されていること
- **期待される結果**:
  - 戻り値: false
  - *send_datalenが更新されないこと

---

#### TEST004
- **概要**: send_datalenポインタにNULLを指定した場合のエラー処理を確認する
- **条件**:
  - data: 有効なデータポインタ
  - datalen: 10
  - send_datalen: NULL
  - 前提条件:
    - comm_init()が実行済みであること
    - ICommServerまたはICommClientが正常に生成されていること
- **期待される結果**:
  - 戻り値: false
  - 送信処理が実行されないこと
