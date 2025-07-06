# ドキュメント作成方針

ドキュメントは基本的に、AIのサポートで作成することを指向する。

![image](ai-colab-overview.png)

上図の灰色部分は、AIのサポートで作成する部分である。

それ以外の部分は、人間が思考して作成する部分である。

## 管理している成果物

AI 生成フローの中で人間が用意する成果物と、その管理場所を以下にまとめます。

| 成果物 | 説明 | 保存場所 |
|--------|------|---------|
| API・テスト仕様プロンプト | 各 API の仕様書やテスト関連の指示をまとめた番号付きプロンプトファイル | `docs/prompts/*/01_api-doc.md` など <br>例: [comm I/O 用](prompts/comm/io/01_api-doc.md) |
| テンプレート類 | 生成物のフォーマット定義 | `docs/prompts` |
| API ヘッダ | API 定義を記述したヘッダファイル | `include/*.hpp` <br>例: [comm.hpp](../include/comm.hpp) |

プロンプトはコンポーネント毎に `docs/prompts/<コンポーネント>` に整理し、
共通で利用するテンプレートは `docs/prompts` 直下に配置しています。

その他のテンプレートや資料は順次整備中です (工事中)。

# API ドキュメント
- [comm](api/comm/api_comm.md)
- [mavlink](api/mavlink/api_mavlink.md)

# テスト仕様
 - [comm](test/comm)
 - [mavlink](test/mavlink)

# テストコード
 - [comm](../test/comm)
 - テストのビルドと実行は `tools/build_and_test.sh` で行えます

## Docker Compose を用いた通信テスト

`docker-compose.yml` を利用すると、通信サーバーとクライアントを別コンテナで起動して `test/comm/compose` のテストを実行できます。サーバー側では `comm_server_tcp` または `comm_server_udp` が起動し、クライアント側で `test_comm_tcp_compose` もしくは `test_comm_udp_compose` を実行します。

### 実行方法
1. Docker および Docker Compose が利用可能な環境を用意します。
2. リポジトリのルートで `PROTO=tcp docker compose up --build` を実行します。
   - `PROTO=udp` を指定すると UDP モードで動作します。
3. テスト完了後は `docker compose down` を実行してコンテナを終了します。

詳細なテスト仕様は [`docs/test/comm/compose/test_comm_compose.md`](test/comm/compose/test_comm_compose.md) を参照してください。

