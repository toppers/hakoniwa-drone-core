# comm テスト概要

通信テストは基本的に **Docker Compose** を利用してサーバーとクライアントを分離した状態で実行することを推奨しています。
`docker-compose.yml` を用いた通信テストでは、サーバーとクライアントを別コンテナで起動して `ICommIO` API の動作を確認します。サーバープログラムは `test/comm/compose` ディレクトリにある `comm_server_tcp` または `comm_server_udp` を使用します。

## 実行方法
1. Docker と Docker Compose をインストールしておきます。
2. リポジトリのルートで次を実行します。
   ```bash
   PROTO=tcp docker compose up --build
   ```
   UDP モードで実行する場合は `PROTO=udp` を指定してください。
3. テスト実行後は `docker compose down` でコンテナを停止します。

テストケースの詳細は [compose/test_comm_compose.md](compose/test_comm_compose.md) を参照してください。
