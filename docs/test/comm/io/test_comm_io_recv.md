# テスト仕様書

## ICommIO::recv
- データ受信が成功すること ... TEST001
- dataがNULLの場合にエラーとなること ... TEST002
- datalenが負の値の場合にエラーとなること ... TEST003
- 受信バッファがデータ長より小さい場合でも受信が成功すること ... TEST004

---

### テストケース詳細

#### TEST001
- **概要**: バッファを指定してデータ受信が成功することを確認する
- **条件**:
  - data: 受信バッファ(十分なサイズ)
  - datalen: バッファサイズ
  - recv_datalen: 有効なint型ポインタ
  - 前提条件:
    - comm_init()が実行済みであること
    - ICommServerまたはICommClientが正常に生成されていること
- **期待される結果**:
  - 戻り値: true
  - *recv_datalenに実際に受信したバイト数が設定されること
  - *recv_datalenの値がdatalen以下であること

---

#### TEST002
- **概要**: dataにNULLを指定した場合のエラー処理を確認する
- **条件**:
  - data: NULL
  - datalen: 10
  - recv_datalen: 有効なint型ポインタ
  - 前提条件:
    - comm_init()が実行済みであること
    - ICommServerまたはICommClientが正常に生成されていること
- **期待される結果**:
  - 戻り値: false
  - *recv_datalenが更新されないこと

---

#### TEST003
- **概要**: datalenに負の値を指定した場合のエラー処理を確認する
- **条件**:
  - data: 有効なバッファ
  - datalen: -1
  - recv_datalen: 有効なint型ポインタ
  - 前提条件:
    - comm_init()が実行済みであること
    - ICommServerまたはICommClientが正常に生成されていること
- **期待される結果**:
  - 戻り値: false
  - *recv_datalenが更新されないこと

---

#### TEST004
- **概要**: 受信バッファがメッセージ長より小さい場合の受信動作を確認する
- **条件**:
  - data: サイズ10バイトのバッファ
  - datalen: 10
  - recv_datalen: 有効なint型ポインタ
  - 前提条件:
    - comm_init()が実行済みであること
    - ICommServerまたはICommClientが正常に生成されていること
- **期待される結果**:
  - 戻り値: true
  - *recv_datalenの値がdatalen以下であること
  - バッファに受信データが格納されること
