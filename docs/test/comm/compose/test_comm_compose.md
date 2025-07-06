# テスト仕様書

## Docker Compose で ICommIO テストを実行
- `docs/test/comm/io` の仕様に基づくテストをノード分離環境で実行できること ... TEST001_TCP, TEST001_UDP

---

### テストケース詳細

#### TEST001_TCP
- **概要**: docker compose を用いて server と client を分離し、`test_comm_tcp_compose` を実行してすべてのテストが成功することを確認する
- **条件**:
  - `docker-compose.yml` の server と client サービスを起動する (環境変数 `PROTO=tcp`)
  - client サービスは `test_comm_tcp_compose` を実行する
- **期待される結果**:
  - client のテスト結果に `PASSED` が含まれること

#### TEST001_UDP
- **概要**: docker compose を用いて server と client を分離し、`test_comm_udp_compose` を実行してすべてのテストが成功することを確認する
- **条件**:
  - `docker-compose.yml` の server と client サービスを起動する (環境変数 `PROTO=udp`)
  - client サービスは `test_comm_udp_compose` を実行する
- **期待される結果**:
  - client のテスト結果に `PASSED` が含まれること

