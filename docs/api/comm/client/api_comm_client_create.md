# ICommClient::create API 仕様書

## 概要

本ドキュメントは、`ICommClient::create` API に関する仕様を説明します。本 API は `ICommClient` オブジェクトを生成するために提供されます。

---

## API 概要

### 関数シグネチャ

```cpp
static std::unique_ptr<ICommClient> create(CommIoType type);
```

### ヘッダファイル

本 API を利用するには、以下のヘッダファイルをインクルードする必要があります。

```cpp
#include "comm.hpp"
```

---

## 前提条件

本 API を利用する前に、`comm_init()` 関数を呼び出して通信モジュールを初期化してください。

---

## パラメータ

| パラメータ名 | 型               | 説明 |
|--------------|------------------|------|
| `type`       | `CommIoType`     | 作成する `ICommClient` の通信タイプを指定します。この値に応じて適切なクライアントオブジェクトが生成されます。 |

---

## 戻り値

| 型                                   | 説明 |
|-------------------------------------|------|
| `std::unique_ptr<ICommClient>`      | 指定された通信タイプに基づいて生成された `ICommClient` オブジェクトを返します。 |
| `nullptr`                           | 無効な通信タイプが指定された場合や、生成に失敗した場合は `nullptr` を返します。 |

---

## 例外

この関数は例外を投げません。ただし、`nullptr` が返された場合はエラーハンドリングを行う必要があります。

---

## 使用例

以下に `ICommClient::create` の使用例を示します。

### 使用コード例

```cpp
#include "comm.hpp"
#include <iostream>

int main() {
    // 通信モジュールの初期化
    comm_init();

    // ICommClient オブジェクトの作成
    auto client = ICommClient::create(CommIoType::UDP);

    if (client == nullptr) {
        std::cerr << "Failed to create ICommClient" << std::endl;
        return -1;
    }

    // クライアントの使用処理
    // ...

    return 0;
}
```

---

## 注意事項

1. 本 API を利用する前に、`comm_init()` を必ず呼び出してください。初期化されていない場合、API の動作は保証されません。
2. `type` に無効な値を指定した場合、本関数は `nullptr` を返します。そのため、戻り値のチェックを必ず行ってください。

---

## 関連情報

### クラス設計情報
- 詳細については、[api_comm.md](https://github.com/toppers/hakoniwa-drone-core/blob/main/docs/api/comm/api_comm.md) を参照してください。

### テンプレート
- 本仕様書は [api-template.md](https://github.com/toppers/hakoniwa-drone-core/blob/main/docs/templates/api-template.md) に基づいて作成されています。

### 関連ヘッダ
- [comm.hpp](https://github.com/toppers/hakoniwa-drone-core/blob/main/include/comm.hpp)
- [comm/icomm_connector.hpp](https://github.com/toppers/hakoniwa-drone-core/blob/main/include/comm/icomm_connector.hpp)

