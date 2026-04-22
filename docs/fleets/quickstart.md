# fleets クイックスタート（5分）

このページは、最短で fleets を起動して動作確認する手順です。

## 0. 前提

- 作業ディレクトリ: `hakoniwa-drone-pro` ルート
- Python3 が使えること

## 1. N=10 で起動

```bash
bash tools/launch-fleets-scale-perf.bash 10
```

## 2. ブラウザ接続（同一PC）

```text
http://127.0.0.1:8000/index.html?viewerConfigPath=/config/viewer-config-fleets.json&wsUri=ws://127.0.0.1:8765&wireVersion=v2&dynamicSpawn=true&templateDroneIndex=0&maxDynamicDrones=10
```

`connect` を押す。

## 3. ミッション実行（別ターミナル）

```bash
bash drone_api/external_rpc/apps/run_square_mission.bash --drone-count 10 --phase-step 1
```

## 4. 動作確認ポイント

- 10機体が表示される
- square mission で機体が移動する
- launcher 側でエラー終了していない

## 5. つまずいたら

- [troubleshooting.md](./troubleshooting.md) を参照
- 詳細運用は [operations.md](./operations.md) を参照
