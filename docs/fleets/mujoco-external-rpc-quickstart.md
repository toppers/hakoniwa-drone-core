# MuJoCo external_rpc Quickstart

この文書は、MuJoCo 複数機シミュレータを生成し、Hakoniwa drone service を起動し、Python `external_rpc` サンプルから 2 機を操作するまでの最短手順をまとめる。

対象読者:

- MuJoCo + fleet + Python API を最初に 1 回通したい
- `mujoco_two_drone_demo.py` をいつ使うのか知りたい
- 生成ファイルの関係を最短で理解したい

## 1. ゴール

最終的に次を実行できる状態にする。

```bash
python3 drone_api/external_rpc/samples/mujoco_two_drone_demo.py
```

このサンプルは次を 2 機へ同時に行う。

1. `SetReady`
2. `TakeOff`
3. `GoTo`
4. `GetState`
5. `Land`

## 2. 生成されるファイル

今回使う runtime は次の 4 種類のファイルで構成される。

- fleet config
  - `config/drone/fleets/api-current.json`
- service config
  - `config/drone/fleets/services/api-current-service.json`
- pdudef
  - `config/pdudef/drone-pdudef-current.json`
- MuJoCo XML
  - `config/drone/mujoco-current/drone.xml`

役割は次のとおりである。

- fleet config
  - 機体数、機体名、初期位置、MuJoCo per-instance override
- service config
  - Python `external_rpc` が接続する service 定義
- pdudef
  - Hakoniwa PDU 定義
- MuJoCo XML
  - 実際の MuJoCo scene と複数機体 body

## 3. fleet / service / pdudef を生成する

2 機の MuJoCo API 用 config を `current` 系へ生成する。

```bash
python3 tools/gen_fleet_scale_config.py \
  -n 2 \
  --layout packed-rings \
  --ring-spacing-meter 1 \
  --type-name api-mujoco \
  --type-config-path config/drone/fleets/types/api-mujoco.json \
  --fleet-path config/drone/fleets/api-current.json \
  --pdudef-path config/pdudef/drone-pdudef-current.json \
  --service-config-path config/drone/fleets/services/api-current-service.json \
  --service-out-path config/drone/fleets/services/api-current-service.json \
  --enable-mujoco-overrides
```

この結果、`api-current.json` の各 drone entry には次が入る。

- `mujoco.modelName`
  - `d1_b_drone_base`, `d2_b_drone_base`
- `mujoco.propNames`
  - `d1_b_prop1..4`, `d2_b_prop1..4`

## 4. MuJoCo XML を生成する

scene template と 1 機 body template から、複数機の `drone.xml` を生成する。

```bash
python3 tools/gen_mujoco_multidrone_xml.py \
  -n 2 \
  --scene-template-path config/drone/fleets/types/mujoco-scene.xml.template \
  --drone-template-path config/drone/fleets/types/mujoco-drone.xml.template \
  --output-path config/drone/mujoco-current/drone.xml
```

## 5. MuJoCo service を起動する

Hakoniwa 側の MuJoCo drone service を起動する。

```bash
./mac/mac-main_hako_drone_service \
  config/drone/fleets/api-current.json \
  config/pdudef/drone-pdudef-current.json \
  --real-sleep-msec 1
```

viewer を使いたい場合:

```bash
./mac/mac-main_hako_drone_service \
  config/drone/fleets/api-current.json \
  config/pdudef/drone-pdudef-current.json \
  --mujoco-viewer \
  --real-sleep-msec 1
```

viewer 操作:

- `c`
  - follow / free camera 切り替え
- `v`
  - camera orientation reset
- `1`〜`9`
  - follow 対象機体を切り替え

## 6. Python サンプルを実行する

別ターミナルで次を実行する。

```bash
python3 drone_api/external_rpc/samples/mujoco_two_drone_demo.py
```

このサンプルは `use_async_shared=True` を使う。
つまり、後方互換の同期 wrapper ではなく、shared runtime の複数機経路を通る。

## 7. どこを見ればよいか

動作確認の観点では、次の 3 点だけ見ればよい。

- service 側が 2 機を読み込めているか
- viewer で `1` / `2` を押すと follow 対象が切り替わるか
- Python サンプルで `set_ready`, `takeoff`, `goto`, `land` のログが 2 機分出るか

## 8. よくあるハマりどころ

- `mujoco_two_drone_demo.py` 実行前に service が起動していない
- `api-current.json` と `api-current-service.json` を生成し直していない
- `drone.xml` を `config/drone/mujoco-current/drone.xml` に出していない
- `FleetRpcController` を自作するとき `use_async_shared=True` を付け忘れる

## 9. 次に読む文書

- runtime 生成の詳細:
  - [MuJoCo Runtime Generation](mujoco-runtime-generation.md)
- Python API の基本:
  - [external_rpc Tutorial](external-rpc-tutorial.md)
- external_rpc 全体の構成:
  - [external_rpc README](../../drone_api/external_rpc/README.md)
