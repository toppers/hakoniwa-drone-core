# ICommServer::create API ドキュメント

## シグネチャ

```c++
std::unique_ptr<ICommServer> create(const std::string& address, int port);
```

## 概要
このAPIは、指定されたアドレスおよびポートで通信サーバーのインスタンスを作成します。通信サーバーはクライアントからの接続を受け付けるための基盤を提供します。

## 引数

| 名前     | 型                | 必須 | 説明                           |
|----------|-------------------|------|--------------------------------|
| `address`| `const std::string&` | Yes  | サーバーがバインドされるアドレス (例: "127.0.0.1") |
| `port`   | `int`             | Yes  | サーバーがリスンするポート番号 (例: 8080) |

## 戻り値

- **成功時**: サーバーオブジェクトのユニークポインタを返します。
- **失敗時**: `nullptr` を返します。

## 注意事項

- 本APIを使用する前に必ず `comm_init()` を呼び出して、通信モジュールを初期化してください。
- 引数 `address` に無効なアドレスを指定した場合や、`port` が適切な範囲 (1～65535) 外の場合、APIは失敗します。
- このAPIはスレッドセーフですが、複数スレッドで使用する場合は適切な同期を行ってください。

## 使用例

```cpp
#include <iostream>
#include "comm.hpp"
#include "icomm_connector.hpp"

int main() {
    // 初期化
    if (!comm_init()) {
        std::cerr << "通信モジュールの初期化に失敗しました。" << std::endl;
        return -1;
    }

    // サーバーの生成
    auto server = ICommServer::create("127.0.0.1", 8080);
    if (!server) {
        std::cerr << "サーバーの作成に失敗しました。" << std::endl;
        comm_finalize();
        return -1;
    }

    std::cout << "サーバーが正常に作成されました。" << std::endl;

    // サーバー処理...

    return 0;
}
```

