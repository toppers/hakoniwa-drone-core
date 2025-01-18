# ICommClient::client_open API 仕様書

## 概要

本ドキュメントは、`ICommClient::client_open` API に関する仕様を説明します。本 API は、指定された送信元および送信先エンドポイントに基づいてクライアント通信オブジェクトを生成および取得するために使用されます。

---

## API 概要

### 関数シグネチャ

```cpp
virtual std::shared_ptr<ICommIO> client_open(ICommEndpointType *src, ICommEndpointType *dst) = 0;
```

### ヘッダファイル

本 API を利用するには、以下のヘッダファイルをインクルードする必要があります。

```cpp
#include "comm.hpp"
```

---

## 前提条件

1. 本 API を利用する前に、`comm_init()` 関数を呼び出して通信モジュールを初期化してください。
2. `ICommClient::create()` を使用して `ICommClient` オブジェクトを生成してください。
3. `create()` 時に指定する通信タイプ（`CommIoType`）に応じて適切な通信オブジェクトが生成されます。

---

## パラメータ

| パラメータ名 | 型                     | 説明 |
|--------------|------------------------|------|
| `src`        | `ICommEndpointType*`  | クライアント通信の送信元エンドポイント情報を格納したオブジェクトのポインタ。 |
| `dst`        | `ICommEndpointType*`  | クライアント通信の送信先エンドポイント情報を格納したオブジェクトのポインタ。 |

---

## 戻り値

| 型                           | 説明 |
|------------------------------|------|
| `std::shared_ptr<ICommIO>`   | 指定されたエンドポイントに基づいて生成された通信オブジェクト。成功時には有効なポインタを返します。 |
| `nullptr`                    | 無効なエンドポイントや通信オブジェクトの生成に失敗した場合は `nullptr` を返します。 |

---

## 例外

この関数は例外を投げません。ただし、エラー発生時には `nullptr` を返します。エラーハンドリングを適切に実装してください。

---

## 使用例

以下に `ICommClient::client_open` の使用例を示します。

### 使用コード例

```cpp
#include "comm.hpp"
#include <iostream>

int main() {
    // 通信モジュールの初期化
    comm_init();

    // ICommClient オブジェクトの作成
    auto client = ICommClient::create(CommIoType::TCP);

    if (client == nullptr) {
        std::cerr << "Failed to create ICommClient" << std::endl;
        return -1;
    }

    // エンドポイント設定
    ICommEndpointType src_endpoint;
    ICommEndpointType dst_endpoint;
    // 必要なエンドポイント情報を設定
    src_endpoint.port = 5000;
    dst_endpoint.address = "127.0.0.1";
    dst_endpoint.port = 6000;

    // クライアント通信オブジェクトのオープン
    auto comm_io = client->client_open(&src_endpoint, &dst_endpoint);

    if (comm_io == nullptr) {
        std::cerr << "Failed to open client connection" << std::endl;
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
2. `src` および `dst` パラメータには有効なエンドポイント情報を指定する必要があります。不正なエンドポイントを指定すると `nullptr` が返されます。
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


