# MuJoCo Runtime Generation

この文書は、MuJoCo 用 fleet runtime を生成するための最小手順をまとめる。

まず 2 機の MuJoCo + Python `external_rpc` を一度通したい場合は、先に
[MuJoCo external_rpc Quickstart](mujoco-external-rpc-quickstart.md)
を読むほうが早い。

対象ツール:

- `tools/gen_fleet_scale_config.py`
- `tools/gen_mujoco_multidrone_xml.py`

この文書では、2 機の MuJoCo API runtime を例にする。

## 1. 何を生成するか

MuJoCo fleet runtime では、少なくとも次の 4 種類のファイルが必要である。

- fleet config
  - 例: `config/drone/fleets/api-mujoco-instance-2.json`
- service config
  - 例: `config/drone/fleets/services/api-mujoco-instance-2-service.json`
- pdudef
  - 例: `config/pdudef/drone-pdudef-mujoco-instance-2.json`
- MuJoCo XML
  - 例: `config/drone/mujoco-current/drone.xml`

役割の分担は次のとおりである。

- `gen_fleet_scale_config.py`
  - fleet config
  - service config
  - pdudef
- `gen_mujoco_multidrone_xml.py`
  - MuJoCo XML

## 2. 前提ファイル

JSON 系 generator は、type config を参照する。

例:

- `config/drone/fleets/types/api-mujoco.json`

XML generator は、scene template と 1 機分の body template を参照する。

例:

- `config/drone/fleets/types/mujoco-scene.xml.template`
- `config/drone/fleets/types/mujoco-drone.xml.template`

scene template には、ground、building、obstacle、light などを自由に書ける。
generator は `__DRONE_BODIES__` に N 機分の body を差し込む。

### 2.1 scene template の役割

`mujoco-scene.xml.template` は、MuJoCo scene 全体を定義するテンプレートである。

ここには、たとえば次を書ける。

- ground
- landmark
- building
- obstacle
- light
- camera や site

一方、複数機体の body 自体はここへ直接書かない。
複数機体 body は generator が `__DRONE_BODIES__` へ差し込む。

つまり責務は次のように分かれる。

- scene template
  - world 全体の見た目と障害物
- drone body template
  - 1 機ぶんの body 構造
- generator
  - 1 機 body を N 回複製して scene に埋め込む

### 2.2 scene template で守るべきこと

scene template を編集するときは、次の 3 点を守ればよい。

- `__DRONE_BODIES__` を消さない
- drone body が初期的に重なりそうな位置へ障害物を置かない
- `<mujoco>`, `<worldbody>` などの基本構造を壊さない

特に `__DRONE_BODIES__` は generator の差し込み位置なので、これを削除すると複数機の body が生成されない。

### 2.3 scene template の最小イメージ

たとえば scene template の本質は次のような構造である。

```xml
<mujoco>
  ...
  <worldbody>
    <light .../>
    <geom name="ground" .../>
    <body name="landmark_box_1" ...>...</body>
    <body name="building_1" ...>...</body>

    __DRONE_BODIES__
  </worldbody>
</mujoco>
```

つまり、ユーザは `__DRONE_BODIES__` の前後に自由に scene 要素を足せる。

1 機分 body template では、位置は固定でよい。
初期配置は Hakoniwa 側の `position_meter` / `angle_degree` が責務を持つ。

## 3. fleet / service / pdudef の生成

2 機の MuJoCo API fleet config を生成する例:

```bash
python3 tools/gen_fleet_scale_config.py \
  -n 2 \
  --layout packed-rings \
  --ring-spacing-meter 1 \
  --type-name api-mujoco \
  --type-config-path config/drone/fleets/types/api-mujoco.json \
  --fleet-path config/drone/fleets/api-mujoco-instance-2.json \
  --pdudef-path config/pdudef/drone-pdudef-mujoco-instance-2.json \
  --service-config-path config/drone/fleets/services/api-mujoco-instance-2-service.json \
  --service-out-path config/drone/fleets/services/api-mujoco-instance-2-service.json \
  --enable-mujoco-overrides
```

このとき generator は、各 drone entry に次の MuJoCo override を出力する。

- `mujoco.modelName`
  - `d1_b_drone_base`, `d2_b_drone_base`, ...
- `mujoco.propNames`
  - `d1_b_prop1` ... `d1_b_prop4`
  - `d2_b_prop1` ... `d2_b_prop4`

つまり、fleet config 側の naming は XML generator の naming 規則と一致している必要がある。

### 3.1 主な引数

- `-n`, `--drone-count`
  - 機体数
- `--type-name`
  - fleet config に書く type 名
- `--type-config-path`
  - fleet config の `types.<type-name>` に書く path
- `--fleet-path`
  - fleet config の出力先
- `--pdudef-path`
  - pdudef の出力先
- `--service-config-path`
  - fleet config に書く `serviceConfigPath`
- `--service-out-path`
  - service config の出力先
- `--enable-mujoco-overrides`
  - per-instance の `mujoco.modelName` / `propNames` を出力する

## 4. MuJoCo XML の生成

2 機の MuJoCo XML を生成する例:

```bash
python3 tools/gen_mujoco_multidrone_xml.py \
  -n 2 \
  --scene-template-path config/drone/fleets/types/mujoco-scene.xml.template \
  --drone-template-path config/drone/fleets/types/mujoco-drone.xml.template \
  --output-path config/drone/mujoco-current/drone.xml
```

このツールは、

- scene template の `__DRONE_BODIES__`
- drone body template 内の `d1_*`, `d2_*`, ... placeholder

を展開し、1 つの `drone.xml` にまとめる。

### 4.1 主な引数

- `-n`, `--drone-count`
  - 機体数
- `--scene-template-path`
  - scene template
- `--drone-template-path`
  - 1 機分 body template
- `--output-path`
  - 生成する MuJoCo XML

## 5. naming 規則

現在の命名規則は次のとおりである。

- drone 1 root body
  - `d1_b_drone_base`
- drone 1 freejoint
  - `d1_j_free`
- drone 1 prop bodies
  - `d1_b_prop1` ... `d1_b_prop4`
- drone 2 root body
  - `d2_b_drone_base`
- drone 2 freejoint
  - `d2_j_free`
- drone 2 prop bodies
  - `d2_b_prop1` ... `d2_b_prop4`

この naming は、

- fleet config の `mujoco.modelName`
- fleet config の `mujoco.propNames`
- MuJoCo XML 内の body 名

の 3 者で一致している必要がある。

## 6. scene template の編集

scene template では、`<worldbody>` 配下に landmark、building、obstacle を自由に追加できる。
generator は `__DRONE_BODIES__` を置換するだけなので、それ以外の scene 記述はそのまま残る。

ここでの考え方は、

- drone を増やしたい
  - generator に任せる
- world を richer にしたい
  - scene template を編集する

である。

### 6.1 landmark を追加する

距離感を掴みやすくするには、まず landmark を数個置くのがよい。

たとえば landmark を増やしたい場合:

```xml
<body name="landmark_box_3" pos="5 -2 1.2">
  <geom name="landmark_box_3_geom" type="box" size="0.8 0.8 1.2" rgba="0.9 0.7 0.2 1"/>
</body>
```

### 6.2 building を追加する

建物を置きたい場合:

```xml
<body name="building_1" pos="8 3 4.0">
  <geom name="building_1_geom" type="box" size="2.0 2.0 4.0" rgba="0.6 0.6 0.6 1"/>
</body>
```

### 6.3 obstacle を追加する

細い障害物を置きたい場合:

```xml
<body name="obstacle_pole_1" pos="-4 1 1.5">
  <geom name="obstacle_pole_1_geom" type="cylinder" size="0.08 1.5" rgba="0.8 0.3 0.3 1"/>
</body>
```

### 6.4 編集時の注意

重要なのは次の 2 点だけである。

- `__DRONE_BODIES__` は消さない
- drone body と重なる位置に障害物を置かない

まずは landmark や building を数個置いて、viewer 上で距離感を掴みやすくするのがよい。

### 6.5 どういう時に scene template を触るか

scene template を触るべき典型例は次のとおりである。

- viewer 上で距離感がつかみにくい
- 障害物回避や接触確認をしたい
- 建物の間を飛ばしたい
- 実験ごとに別の scene を切り替えたい

一方、機体数を増減したいだけなら scene template は触らず、generator の `-n` だけ変えればよい。

## 7. dry-run

generator の出力内容だけ確認したい場合は `--dry-run` を使う。

例:

```bash
python3 tools/gen_fleet_scale_config.py -n 2 --enable-mujoco-overrides --dry-run
```

```bash
python3 tools/gen_mujoco_multidrone_xml.py -n 2 --dry-run
```

## 8. 関連ドキュメント

- [fleet + MuJoCo runtime 設計](../architecture/config/fleet-mujoco-runtime-design.md)
- [config runtime map](config-runtime-map.md)
