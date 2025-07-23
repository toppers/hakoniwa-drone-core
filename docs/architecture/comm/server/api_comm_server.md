# ICommServer API 仕様書

## 概要

本ドキュメントは、`ICommServer` に含まれる API に関する仕様を説明します。`ICommServer` はサーバ通信を実現するためのインターフェースであり、データの送受信を行うための通信オブジェクトを生成および管理します。

---

## API 概要

### 対象API

- `static std::unique_ptr<ICommServer> create(CommIoType type);`
- `std::shared_ptr<ICommIO> server_open(ICommEndpointType *endpoint) = 0;`

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
2. `create()` メソッドを使用して `ICommServer` オブジェクトを生成してください。
3. `server_open()` を使用して、通信に必要なオブジェクトを初期化してください。

---

## API 詳細

### 1. `create`

#### 関数シグネチャ

```cpp
static std::unique_ptr<ICommServer> create(CommIoType type);
```

#### 説明
指定された通信タイプに応じた `ICommServer` オブジェクトを生成します。

| パラメータ名 | 型            | 説明 |
|--------------|---------------|------|
| `type`       | `CommIoType`  | 作成する通信サーバのタイプ。例: `TCP`, `UDP` |

#### 戻り値

| 型                                   | 説明 |
|-------------------------------------|------|
| `std::unique_ptr<ICommServer>`      | 指定された通信タイプに基づいて生成された `ICommServer` オブジェクト。 |
| `nullptr`                           | 生成に失敗した場合は `nullptr` を返します。 |

#### 注意事項

- 通信タイプが無効である場合、本関数は `nullptr` を返します。そのため、戻り値のチェックを必ず行ってください。

---

### 2. `server_open`

#### 関数シグネチャ

```cpp
std::shared_ptr<ICommIO> server_open(ICommEndpointType *endpoint) = 0;
```

#### 説明
指定されたエンドポイントに基づいてサーバ通信オブジェクトを初期化します。

| パラメータ名 | 型                     | 説明 |
|--------------|------------------------|------|
| `endpoint`   | `ICommEndpointType*`  | サーバ通信のエンドポイント情報を格納したオブジェクトのポインタ。 |

#### 戻り値

| 型                           | 説明 |
|------------------------------|------|
| `std::shared_ptr<ICommIO>`   | 指定されたエンドポイントに基づいて初期化された通信オブジェクト。 |
| `nullptr`                    | 初期化に失敗した場合は `nullptr` を返します。 |

#### 注意事項

- エンドポイントが無効である場合、本関数は `nullptr` を返します。
- 戻り値が `nullptr` の場合は適切なエラーハンドリングを実装してください。
- **通信方式によるブロック動作の違い**
  - **TCP**: `server_open()` はクライアントからの接続が確立するまでブロックします。
  - **UDP**: `server_open()` はソケットを準備したあと即座に復帰します。最初のパケット待ち合わせは `recv()` で行います。

---

## 使用例

以下に `ICommServer` の使用例を示します。

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

    // サーバ通信オブジェクトのオープン
    ICommEndpointType endpoint;
    endpoint.port = 8080;

    auto comm_io = server->server_open(&endpoint);
    if (comm_io == nullptr) {
        std::cerr << "Failed to open server connection" << std::endl;
        return -1;
    }

    // 通信オブジェクトの使用
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
 - 本仕様書は [api-template.md](https://github.com/toppers/hakoniwa-drone-core/blob/main/docs/prompts/api-template.md) に基づいて作成されています。

### 関連ヘッダ
- [comm.hpp](https://github.com/toppers/hakoniwa-drone-core/blob/main/include/comm.hpp)


