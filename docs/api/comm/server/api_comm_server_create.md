# ICommServer::create API 仕様書

## シグネチャ

```cpp
static std::unique_ptr<ICommServer> create(CommIoType type);
```

---

## 概要
`ICommServer::create`は、指定された通信方式（TCPまたはUDP）に基づいて通信サーバーを生成します。このAPIは、通信方式に応じた`ICommServer`インスタンスを作成し、サーバー機能を提供します。

---

## 引数

| 名前   | 型           | 必須 | 説明                                 |
|--------|--------------|------|--------------------------------------|
| `type` | `CommIoType` | Yes  | サーバーの通信方式（TCPまたはUDP）。 |

---

## 戻り値

- **成功時**:
  - `std::unique_ptr<ICommServer>`型の通信サーバーインスタンス。
- **失敗時**:
  - `nullptr`（実装依存で返される場合があります）。

---

## 注意事項

- 本APIを利用する前に、必ず`hako::comm::comm_init()`を呼び出して通信ライブラリを初期化してください。  
  初期化が行われていない場合、正しく動作しない可能性があります。

---

## 使用例

以下に`ICommServer::create`の使用例を示します。

```cpp
#include "comm.hpp"

int main() {
    // 通信ライブラリの初期化
    if (hako::comm::comm_init() != 0) {
        return -1; // 初期化失敗
    }

    // TCP通信サーバーの生成
    auto server = hako::comm::ICommServer::create(hako::comm::COMM_IO_TYPE_TCP);
    if (!server) {
        // サーバー生成失敗
        return -1;
    }

    // サーバーのエンドポイント設定
    hako::comm::ICommEndpointType endpoint = {"127.0.0.1", 8080};
    auto connection = server->server_open(&endpoint);

    // 通信処理（省略）
    return 0;
}
```

---

## 関連情報

- **列挙型 `CommIoType`**:
  - `COMM_IO_TYPE_TCP`: TCP通信を指定。
  - `COMM_IO_TYPE_UDP`: UDP通信を指定。
- **関連API**:
  - `comm_init`: 通信ライブラリを初期化するグローバル関数。
  - `ICommServer::server_open`: サーバーを指定されたエンドポイントでオープンする。
```
