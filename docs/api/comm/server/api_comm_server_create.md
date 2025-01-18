# ICommServer::create API ドキュメント

## シグネチャ

```c++
static std::unique_ptr<ICommClient> create(CommIoType type);
```

## 概要
このAPIは、指定された通信方式（TCP/UDP）で通信クライアントを生成します。

## 引数

| 名前     | 型                | 必須 | 説明                           |
|----------|-------------------|------|--------------------------------|
| `type`| `CommIoType` | Yes  | 通信方式(TCP/UDP) |

## 戻り値

- **成功時**: サーバーオブジェクトのユニークポインタを返します。
- **失敗時**: `nullptr` を返します。

## 注意事項

- 本APIを使用する前に必ず `comm_init()` を呼び出して、通信モジュールを初期化してください。

## 使用例

```c++
auto client = ICommClient::create(CommIoType::COMM_IO_TYPE_TCP);
if (client) {
    // 通信クライアント生成成功
} else {
    // 通信クライアント生成失敗
}
```
