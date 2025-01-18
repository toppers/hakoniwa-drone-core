# ICommServer::server_open API 仕様書

## 概要

本ドキュメントは、`ICommServer::server_open` API に関する仕様を説明します。本 API は、指定されたエンドポイントに基づいてサーバ通信オブジェクトを生成および取得するために使用されます。

---

## API 概要

### 関数シグネチャ

```cpp
virtual std::shared_ptr<ICommIO> server_open(ICommEndpointType *endpoint) = 0;
```

### ヘッダファイル

本 API を利用するには、以下のヘッダファイルをインクルードする必要があります。

```cpp
#include "comm.hpp"
```

---

## 前提条件

1. 本 API を利用する前に、`comm_init()` 関数を呼び出して通信モジュールを初期化してください。
2. `ICommServer::create()` を使用して `ICommServer` オブジェクトを生成してください。
3. `create()` 時に指定する通信タイプ（`CommIoType`）に応じて適切な通信オブジェクトが生成されます。

---

## パラメータ

| パラメータ名 | 型                     | 説明 |
|--------------|------------------------|------|
| `endpoint`   | `ICommEndpointType*`  | サーバ通信のエンドポイント情報を格納したオブジェクトのポインタ。 |

---

## 戻り値

| 型                           | 説明 |
|------------------------------|------|
| `std::shared_ptr<ICommIO>`   | 指定されたエンドポイントに基づいて生成された通信オブジェクト。成功時には有効なポインタを返します。 |
| `nullptr`                    | 無効なエンドポイントやサーバのオープンに失敗した場合は `nullptr` を返します。 |

---

## 例外

この関数は例外を投げません。ただし、エラー発生時には `nullptr` を返します。エラーハンドリングを適切に実装してください。

---

## 使用例

以下に `ICommServer::server_open` の使用例を示します。

### 使用コード例

```cpp
#include "comm.hpp"
#include <iostream>

int main() {
    // 通信モジュールの初期化
    comm_init();

    // ICommServer オブジェクトの作成
    auto server = ICommServer::create(CommIoType::TCP);

    if (server == nullptr) {
        std::cerr << "Failed to create ICommServer" << std::endl;
        return -1;
    }

    // サーバのエンドポイント設定
    ICommEndpointType endpoint;
    // 必要なエンドポイント情報を設定
    endpoint.port = 8080;

    // サーバ通信オブジェクトのオープン
    auto comm_io = server->server_open(&endpoint);

    if (comm_io == nullptr) {
        std::cerr << "Failed to open server" << std::endl;
        return -1;
    }

    // 通信オブジェクトの使用
    // ...

    return 0;
}
```

---

## 注意事項

1. 本 API を利用する前に、必ず `comm_init()` および `create()` を呼び出してください。
2. `endpoint` パラメータには有効なエンドポイント情報を指定する必要があります。不正なエンドポイントを指定すると `nullptr` が返されます。
3. 戻り値が `nullptr` の場合は、エラー内容に応じた適切な対処を行ってください。

---

## 関連情報

### クラス設計情報
- 詳細については、[api_comm.md](https://github.com/toppers/hakoniwa-drone-core/blob/main/docs/api/comm/api_comm.md) を参照してください。

### テンプレート
- 本仕様書は [api-template.md](https://github.com/toppers/hakoniwa-drone-core/blob/main/docs/templates/api-template.md) に基づいて作成されています。

### 関連ヘッダ
- [comm.hpp](https://github.com/toppers/hakoniwa-drone-core/blob/main/include/comm.hpp)
- [comm/icomm_connector.hpp](https://github.com/toppers/hakoniwa-drone-core/blob/main/include/comm/icomm_connector.hpp)

