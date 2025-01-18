# ICommIO API 仕様書

## 概要

本ドキュメントは、`ICommIO` インターフェースに含まれる API に関する仕様を説明します。本 API は通信データの送受信および接続の終了操作を提供します。

---

## API 概要

### 対象API

- `bool send(const char* data, int datalen, int* send_datalen) = 0;`
- `bool recv(char* data, int datalen, int* recv_datalen) = 0;`
- `bool close() = 0;`

### ヘッダファイル

本 API を利用するには、以下のヘッダファイルをインクルードする必要があります。

```cpp
#include "comm.hpp"
```

### 実装クラス

本 API は仮想関数として定義されており、`ICommServer` または `ICommClient` の `create()` で生成されたインスタンスによって提供されます。

---

## 前提条件

1. 本 API を利用する前に、`comm_init()` 関数を呼び出して通信モジュールを初期化してください。
2. `ICommServer` または `ICommClient` の `create()` を使用して通信オブジェクトを生成してください。
3. データ送受信に必要なバッファは、呼び出し元で適切に確保・解放する必要があります。

---

## API 詳細

### 1. `send`

#### 関数シグネチャ

```cpp
bool send(const char* data, int datalen, int* send_datalen) = 0;
```

#### 説明
指定されたデータを送信します。

| パラメータ名     | 型              | 説明 |
|------------------|-----------------|------|
| `data`           | `const char*`  | 送信するデータのバッファへのポインタ。 |
| `datalen`        | `int`          | 送信するデータの長さ（バイト単位）。 |
| `send_datalen`   | `int*`         | 実際に送信されたデータ長（バイト単位）。 |

#### 戻り値

| 型    | 説明 |
|-------|------|
| `bool`| `true` の場合、送信に成功。`false` の場合、送信に失敗。 |

#### 注意事項

- TCP の場合、データの到達保証がありますが、一時的な通信エラーが発生した場合にはリトライを行い、`datalen` 分のデータ送信を試みます。
- UDP の場合、データ到達保証はありません。

---

### 2. `recv`

#### 関数シグネチャ

```cpp
bool recv(char* data, int datalen, int* recv_datalen) = 0;
```

#### 説明
指定されたバッファにデータを受信します。

| パラメータ名     | 型              | 説明 |
|------------------|-----------------|------|
| `data`           | `char*`        | 受信データを格納するバッファへのポインタ。 |
| `datalen`        | `int`          | バッファのサイズ（バイト単位）。 |
| `recv_datalen`   | `int*`         | 実際に受信されたデータ長（バイト単位）。 |

#### 戻り値

| 型    | 説明 |
|-------|------|
| `bool`| `true` の場合、受信に成功。`false` の場合、受信に失敗。 |

#### 注意事項

- 受信データが `datalen` を超える場合、超過分は破棄されます。
- TCP の場合、複数回の呼び出しで完全なデータを受信する必要がある場合があります。

---

### 3. `close`

#### 関数シグネチャ

```cpp
bool close() = 0;
```

#### 説明
通信を終了します。

#### 戻り値

| 型    | 説明 |
|-------|------|
| `bool`| `true` の場合、正常に通信を終了。`false` の場合、終了に失敗。 |

---

## 使用例

以下に `ICommIO` の使用例を示します。

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

    // データ送信
    const char* send_data = "Hello, Server!";
    int send_len = strlen(send_data);
    int sent_bytes;
    if (!comm_io->send(send_data, send_len, &sent_bytes)) {
        std::cerr << "Failed to send data" << std::endl;
    }

    // データ受信
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

1. 本 API は仮想関数であり、実際の実装は `ICommServer` または `ICommClient` のインスタンスによって提供されます。
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
- [comm/icomm_connector.hpp](https://github.com/toppers/hakoniwa-drone-core/blob/main/include/comm/icomm_connector.hpp)

