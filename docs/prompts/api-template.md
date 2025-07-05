---
template_version: "1.0"
---
# API ドキュメントのテンプレート

## シグネチャ

```c
int hako_asset_register(const char* asset_name, const char* config_path, hako_asset_callbacks_t* callback, hako_time_t delta_usec, HakoAssetModelType model);
```

## 概要
このAPIは、箱庭シミュレーション環境内でアセットを登録します。

## 引数
| 名前          | 型                       | 必須 | 説明                                         |
|---------------|--------------------------|------|----------------------------------------------|
| `asset_name`  | `const char*`            | Yes  | 登録するアセットの名前                      |
| `config_path` | `const char*`            | Yes  | アセットの設定ファイルのパス                |
| `callback`    | `hako_asset_callbacks_t*`| Yes  | コールバック関数へのポインタ                |
| `delta_usec`  | `hako_time_t`            | Yes  | シミュレーション時間のタイムステップ（μs単位）|
| `model`       | `HakoAssetModelType`     | Yes  | アセットのモデルタイプ                      |

## 戻り値
- **成功時**: `0`
- **失敗時**: 非 0 のエラーコード。
  - `EINVAL`: 無効な引数が渡された場合。
  - `ENOENT`: 指定されたファイルが存在しない場合。
  - `EIO`: 入出力エラーが発生した場合。

## 注意事項
- このAPIはスレッドセーフではありません。
- `callback` に渡す関数ポインタは、必ず`hako_asset_callbacks_t`構造体で初期化してください。
- `config_path` は絶対パスを指定してください。

## 使用例
```c
#include <stdio.h>
#include "hako_asset.h"

int main() {
    hako_asset_callbacks_t callback = {/* 初期化コード */};
    int result = hako_asset_register("example_asset", "/config/path", &callback, 1000, HAKO_ASSET_MODEL_CONTROLLER);

    if (result == 0) {
        printf("アセット登録成功！\n");
    } else {
        printf("アセット登録に失敗しました。エラーコード: %d\n", result);
    }
    return result;
}
