# ICommClient API 仕様書

## 概要

本ドキュメントは、`ICommClient` に含まれる API に関する仕様を説明します。`ICommClient` はクライアント通信を実現するためのインターフェースであり、データの送受信を行うための通信オブジェクトを生成および管理します。

---

## API 概要

### 対象API

- `static std::unique_ptr<ICommClient> create(CommIoType type);`
- `std::shared_ptr<ICommIO> client_open(ICommEndpointType *src, ICommEndpointType *dst) = 0;`

### ヘッダファイル

本 API を利用するには、以下のヘッダファイルをインクルードする必要があります。

```cpp
#include "comm.hpp"
```

### 実装クラス

本 API の実装は、`create()` メソッドで生成されるクラスインスタンスによって提供されます。

---

## 前提条件

1. 本 API を利用する前に、`comm_init()` 関数を呼び出して通信モジュールを初期化してください。
2. `create()` メソッドを使用して `ICommClient` オブジェクトを生成してください。
3. `client_open()` を使用して、通信に必要なオブジェクトを初期化してください。

---

## API 詳細

### 1. `create`

#### 関数シグネチャ

```cpp
static std::unique_ptr<ICommClient> create(CommIoType type);
```

#### 説明
指定された通信タイプに応じた `ICommClient` オブジェクトを生成します。

| パラメータ名 | 型            | 説明 |
|--------------|---------------|------|
| `type`       | `CommIoType`  | 作成する通信クライアントのタイプ。例: `TCP`, `UDP` |

#### 戻り値

| 型                                   | 説明 |
|-------------------------------------|------|
| `std::unique_ptr<ICommClient>`      | 指定された通信タイプに基づいて生成された `ICommClient` オブジェクト。 |
| `nullptr`                           | 生成に失敗した場合は `nullptr` を返します。 |

#### 注意事項

- 通信タイプが無効である場合、本関数は `nullptr` を返します。そのため、戻り値のチェックを必ず行ってください。

---

### 2. `client_open`

#### 関数シグネチャ

```cpp
std::shared_ptr<ICommIO> client_open(ICommEndpointType *src, ICommEndpointType *dst) = 0;
```

#### 説明
指定された送信元および送信先エンドポイントに基づいて通信オブジェクトを初期化します。

| パラメータ名 | 型                     | 説明 |
|--------------|------------------------|------|
| `src`        | `ICommEndpointType*`  | 送信元エンドポイント情報を格納したオブジェクトのポインタ。 |
| `dst`        | `ICommEndpointType*`  | 送信先エンドポイント情報を格納したオブジェクトのポインタ。 |

#### 戻り値

| 型                           | 説明 |
|------------------------------|------|
| `std::shared_ptr<ICommIO>`   | 指定されたエンドポイントに基づいて初期化された通信オブジェクト。 |
| `nullptr`                    | 初期化に失敗した場合は `nullptr` を返します。 |

#### 注意事項

- 送信元および送信先のエンドポイントが無効である場合、本関数は `nullptr` を返します。
- 戻り値が `nullptr` の場合は適切なエラーハンドリングを実装してください。

---

## 使用例

以下に `ICommClient` の使用例を示します。

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

    // クライアント通信オブジェクトのオープン
    ICommEndpointType src, dst;
    src.port = 5000;
    dst.address = "127.0.0.1";
    dst.port = 6000;

    auto comm_io = client->client_open(&src, &dst);
    if (comm_io == nullptr) {
        std::cerr << "Failed to open client connection" << std::endl;
        return -1;
    }

    // 通信オブジェクトの使用
    const char* send_data = "Hello, Server!";
    int send_len = strlen(send_data);
    int sent_bytes;
    if (!comm_io->send(send_data, send_len, &sent_bytes)) {
        std::cerr << "Failed to send data" << std::endl;
    }

    char recv_data[1024];
    int recv_bytes;
    if (!comm_io->recv(recv_data, sizeof(recv_data), &recv_bytes)) {
        std::cerr << "Failed to receive data" << std::endl;
    } else {
        std::cout << "Received: " << std::string(recv_data, recv_bytes) << std::endl;
    }

    // 通信の終了
    if (!comm_io->close()) {
        std::cerr << "Failed to close connection" << std::endl;
    }

    return 0;
}
```

---

## 注意事項

1. 本 API を利用する前に、`comm_init()` を必ず呼び出してください。
2. TCP と UDP の通信仕様を理解した上で、本 API を適切に利用してください。
3. 通信エラーが発生した場合は、リトライなどの適切なエラーハンドリングを実装してください。

---

## 関連情報

### クラス設計情報
- 詳細については、[api_comm.md](https://github.com/toppers/hakoniwa-drone-core/blob/main/docs/api/comm/api_comm.md) を参照してください。

### テンプレート
- 本仕様書は [api-template.md](https://github.com/toppers/hakoniwa-drone-core/blob/main/docs/templates/api-template.md) に基づいて作成されています。

### 関連ヘッダ
- [comm.hpp](https://github.com/toppers/hakoniwa-drone-core/blob/main/include/comm.hpp)


