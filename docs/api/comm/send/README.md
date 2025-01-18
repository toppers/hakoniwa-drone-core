# ICommIO::send API 仕様書

## シグネチャ

```cpp
virtual bool send(const char* data, int datalen, int* send_datalen) = 0;
```

## 概要
`send` API は、インタフェース `ICommIO` に定義される純粋仮想関数であり、データを送信するためのものです。このAPIは、`ICommServer` または `ICommClient` の `create` メソッドで生成されたインスタンスを通じて呼び出されます。

本APIは、指定されたデータをインスタンス生成時に選択された通信方式に従って送信します。引数に異常な値が渡された場合、すべて `false` を返します。

## 引数

| 名前             | 型          | 必須 | 説明                                               |
|------------------|-------------|------|----------------------------------------------------|
| `data`           | `const char*` | Yes  | 送信するデータのバッファ                           |
| `datalen`        | `int`       | Yes  | 送信するデータの長さ（バイト単位）                 |
| `send_datalen`   | `int*`      | Yes  | 実際に送信されたデータ長を格納するためのポインタ   |

## 戻り値
- **成功時**: `true`
- **失敗時**: `false`（以下の場合に失敗します）
  - `data` が `nullptr` の場合
  - `datalen` が 0 または負の値の場合
  - `send_datalen` が `nullptr` の場合
  - その他の内部エラー

## 注意事項
1. 本APIを呼び出す前に、必ず `comm_init()` を呼び出して通信環境を初期化してください。
2. 本APIはスレッドセーフであることを保証しません。同時に複数のスレッドから呼び出す場合、適切なロック機構を用いてください。
3. 実装は、`ICommServer` または `ICommClient` に依存します。これらのインスタンスを生成する際に通信方式を指定する必要があります。

## 使用例

```cpp
#include "icomm_connector.hpp"

int main() {
    ICommIO* comm_instance = ICommClient::create("tcp://example.com:12345");

    if (!comm_instance) {
        std::cerr << "通信インスタンスの生成に失敗しました。" << std::endl;
        return -1;
    }

    if (!comm_init()) {
        std::cerr << "通信初期化に失敗しました。" << std::endl;
        return -1;
    }

    const char* data = "Hello, World!";
    int datalen = strlen(data);
    int send_datalen = 0;

    bool result = comm_instance->send(data, datalen, &send_datalen);

    if (result) {
        std::cout << "データ送信成功: 実際に送信された長さ = " << send_datalen << " バイト" << std::endl;
    } else {
        std::cerr << "データ送信失敗" << std::endl;
    }

    delete comm_instance;
    return 0;
}
```
