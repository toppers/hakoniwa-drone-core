# ICommIO::send API仕様書

## シグネチャ

```cpp
virtual bool send(const char* data, int datalen, int* send_datalen) = 0;
```

## 概要
このAPIは、指定されたデータを、ICommServerもしくはICommClientのcreateで生成された通信インスタンスを使用して送信します。

## 引数
| 名前           | 型            | 必須 | 説明                                    |
|----------------|---------------|------|----------------------------------------|
| `data`         | `const char*` | Yes  | 送信するデータへのポインタ              |
| `datalen`      | `int`         | Yes  | 送信するデータのバイト長                |
| `send_datalen` | `int*`        | Yes  | 実際に送信されたデータ長を格納するポインタ |

## 戻り値
- **成功時**: `true`
- **失敗時**: `false`
  - データポインタがNULLの場合
  - データ長が0以下の場合
  - send_datalenポインタがNULLの場合
  - 通信エラーが発生した場合

## 注意事項
- このAPIを使用する前に、必ず`comm_init()`を呼び出す必要があります。
- 本APIは仮想関数であり、実際の実装はICommServerもしくはICommClientのcreate()で生成されたインスタンスによって提供されます。
- 送信データのバッファは、呼び出し元で適切に確保・解放する必要があります。
- 実際に送信されたデータ長は、要求された送信長（datalen）よりも小さい場合があります。
- 通信タイプ（TCP/UDP）によって、データの到達保証レベルが異なります。

## 使用例
```cpp
#include "comm.hpp"

int main() {
    // 通信の初期化
    if (hako::comm::comm_init() != 0) {
        return -1;
    }

    // サーバーインスタンスの作成
    auto server = hako::comm::ICommServer::create(hako::comm::COMM_IO_TYPE_TCP);
    
    // エンドポイントの設定
    hako::comm::ICommEndpointType endpoint = {
        .ipaddr = "127.0.0.1",
        .portno = 8080
    };
    
    // サーバーの開始
    auto comm = server->server_open(&endpoint);
    if (comm == nullptr) {
        return -1;
    }

    // データ送信
    const char* send_data = "Hello, World!";
    int send_len = 13;
    int actual_send_len = 0;
    
    if (comm->send(send_data, send_len, &actual_send_len)) {
        printf("送信成功: %d バイト\n", actual_send_len);
    } else {
        printf("送信失敗\n");
    }

    return 0;
}
```
