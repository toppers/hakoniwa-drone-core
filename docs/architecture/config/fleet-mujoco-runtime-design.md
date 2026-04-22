# Fleet MuJoCo Runtime Design

この文書は、fleet compact config を入口として MuJoCo ベースの複数機体 runtime を扱うための設計方針を整理する。

今回の主眼は次の 2 点である。

- Python `external_rpc` から MuJoCo ベースの箱庭ドローンを操作できるようにすること
- fleet compact config の運用を崩さず、MuJoCo に必要な per-instance 情報を扱えるようにすること

## 1. 背景

既存の fleet compact config では、

- type 側に共通設定を置く
- instance 側には最小差分だけを置く

という方針を取っている。

たとえば `config/drone/fleets/types/api.json` をベース type とし、`config/drone/fleets/api-1.json` の各 drone entry では次だけを持つ。

- `name`
- `type`
- `position_meter`
- `angle_degree`

この形式は、BodyFrame 系や既存 API runtime では扱いやすい。

一方、MuJoCo 複数機体 runtime では、各 instance ごとに少なくとも次の差分が必要になる。

- `components.droneDynamics.mujoco.modelName`
- `components.droneDynamics.mujoco.propNames`

これは MuJoCo の 1 つの XML 内で、各機体 body が別名で存在するためである。

## 2. 今回の方針

今回の第 1 ステップでは、一般的な大規模 generator はまだ導入しない。

代わりに、次の最短ルートを採用する。

1. fleet instance 側に MuJoCo 用の per-instance override を持たせる
2. fleet loader / resolver がその override を base type に上書きする
3. MuJoCo XML は hand-authored または template から生成したものを使う

要するに、

- type 側は共通仕様
- instance 側は MuJoCo runtime 解決に必要な差分

として扱う。

この段階では、instance 側の冗長さは許容する。
人手で大量管理するのではなく、必要なら後で自動生成すればよい、という考え方を取る。

### 2.1 後方互換

今回追加する `mujoco` は、fleet instance に対する optional extension である。

- base type が MuJoCo でない場合:
  - 従来どおり `name`, `type`, `position_meter`, `angle_degree` だけでよい
- base type が MuJoCo の場合:
  - 必要に応じて instance 側の `mujoco` override を解釈する

したがって、この設計は fleet compact config 全体の共通仕様を置き換えるものではない。
あくまで MuJoCo runtime を扱う場合だけに使う追加オプションであり、非 MuJoCo の既存ケースとの後方互換を保つ。

## 3. なぜ `drone_config_i.json` に戻らないのか

`drone_config_i.json` を大量に持つ方式は、台数が増えたときに破綻する。

問題点:

- ファイル数が増えすぎる
- `modelName` と `propNames` だけ違う設定が大量に増える
- 差分管理が困難になる
- compact fleet の利点が失われる

したがって、instance 管理の正本は今後も fleet compact config とする。

## 4. MuJoCo instance override

第 1 ステップでは、fleet instance 側に次のような MuJoCo override を許可する想定とする。

```json
{
  "name": "Drone-1",
  "type": "api",
  "position_meter": [0, 0, 0],
  "angle_degree": [0, 0, 0],
  "mujoco": {
    "modelName": "d1_b_drone_base",
    "propNames": ["d1_b_prop1", "d1_b_prop2", "d1_b_prop3", "d1_b_prop4"]
  }
}
```

ここでの `mujoco` は、base type の

- `components.droneDynamics.mujoco.modelName`
- `components.droneDynamics.mujoco.propNames`

を instance ごとに上書きするための情報である。

この `mujoco` key は optional であり、MuJoCo runtime のときだけ意味を持つ。
BodyFrame 系や既存 API runtime では、この key は不要である。

第 1 ステップでは、上書き対象はこの 2 項目だけで十分である。

## 5. MuJoCo XML Template

複数機体の `drone.xml` を手書きで増やすのは保守性が低い。
したがって、MuJoCo XML は将来的に template ベースで管理する。

ただし、第 1 ステップで template が担う責務は最小限とする。

### 5.1 template の責務

- 1 機分の body 構造をユーザが自由に記述できる
- 複数機体化のために必要な名前だけを可変化する

### 5.2 template で可変にするもの

- root body 名
- freejoint 名
- prop body 名
- 必要なら geom / site 名

### 5.3 template で可変にしないもの

- 初期位置
- 初期姿勢

初期配置は Hakoniwa 側の fleet / `DroneConfig` が責務を持つ。
したがって、MuJoCo XML template では 1 機分の body を原点に置いてよい。

## 6. template の最小契約

template は、少なくとも次のプレースホルダを持つ 1 機分 body ブロックを表現できる必要がある。

- `__DRONE_BASE_NAME__`
- `__FREEJOINT_NAME__`
- `__PROP1_BODY_NAME__`
- `__PROP2_BODY_NAME__`
- `__PROP3_BODY_NAME__`
- `__PROP4_BODY_NAME__`

概念例:

```xml
<body name="__DRONE_BASE_NAME__" pos="0 0 0">
  <freejoint name="__FREEJOINT_NAME__"/>
  ...
  <body name="__PROP1_BODY_NAME__">...</body>
  <body name="__PROP2_BODY_NAME__">...</body>
  <body name="__PROP3_BODY_NAME__">...</body>
  <body name="__PROP4_BODY_NAME__">...</body>
</body>
```

この契約だけ守れば、ユーザは 1 機分の機体構造を自由にカスタマイズできる。

## 7. 命名規則

MuJoCo XML template 展開後の命名規則は安定させる。

第 1 ステップでは、既存の複数機体 MuJoCo 例と整合する次の規則を採用する。

- drone 1 root body: `d1_b_drone_base`
- drone 1 freejoint: `d1_j_free`
- drone 1 prop bodies: `d1_b_prop1` ... `d1_b_prop4`
- drone 2 root body: `d2_b_drone_base`
- drone 2 freejoint: `d2_j_free`
- drone 2 prop bodies: `d2_b_prop1` ... `d2_b_prop4`

この規則の利点:

- XML 生成時の名前解決が単純
- fleet instance 側の `mujoco.modelName` / `propNames` と対応付けしやすい
- 既存の `config/drone/mujoco-2` と整合しやすい

## 8. loader / resolver の責務

第 1 ステップで必要な実装責務は次のとおりである。

1. fleet validator が instance 側の optional `mujoco` key を受け入れる
2. fleet resolver が instance 側 `mujoco` を解釈する
3. resolved `DroneConfig` の `components.droneDynamics.mujoco.*` に反映する

これにより、base type はそのままにしつつ、MuJoCo runtime に必要な per-instance 差分だけを instance 側から注入できる。

非 MuJoCo type に対しては、この拡張は使わない。
したがって、既存の compact fleet resolver の基本動作は維持される。

## 9. 第 1 ステップの非 goal

この設計では、次はまだやらない。

- 大規模 fleet 向けの完全自動 runtime generator
- 100 台以上を想定した MuJoCo XML 自動 synthesis
- MuJoCo XML template の汎用 DSL 化

まずは 1 台 / 2 台の Python API 制御を成立させることを優先する。

## 10. 将来拡張

第 1 ステップが動いたら、次の拡張が可能になる。

- MuJoCo XML template から N 台分の `drone.xml` を生成するツール
- fleet instance 側の `mujoco` override 自動生成
- compact fleet + MuJoCo template から runtime 一式を生成する専用 generator

将来 generator を導入しても、

- fleet compact を入口にする
- MuJoCo XML template はユーザカスタマイズ可能にする
- loader 側の override 仕様を維持する

という基本方針は変えない。

## 11. Generator Design

MuJoCo fleet runtime を将来的に自動生成する場合、generator の責務は 1 つにまとめず、既存ツールの再利用を優先して分割する。

### 11.1 そのまま使えるもの

- `tools/gen_fleet_split_config.py`
  - fleet / service の分割専用ツール
  - MuJoCo 固有の知識を持たないため、そのまま利用する

### 11.2 修正すれば生かせるもの

- `tools/gen_fleet_scale_config.py`
  - 既存で次をまとめて生成している
    - fleet json
    - pdudef
    - service json
  - したがって、MuJoCo fleet runtime でも再利用価値が高い

MuJoCo 向けに拡張する場合、このツールに追加したい責務は次である。

- type path を `api.json` 固定にしない
- fleet instance に `mujoco` override を出力できるようにする
- `serviceConfigPath` / `service out path` / `pdudef path` を MuJoCo 用出力に切り替えられるようにする

つまり、fleet / service / pdudef 側の生成は、既存 generator を拡張して担わせる方が自然である。

### 11.3 新規作成するもの

MuJoCo XML 生成については、既存 generator では扱っていないため、新規ツールを追加する。

想定ツール:

- `tools/gen_mujoco_multidrone_xml.py`

責務:

- `mujoco-drone.xml.template` を入力として読む
- `drone_count` を受け取る
- 1 機分 body block を `N` 回展開する
- `d1_*`, `d2_*`, ... の命名規則で名前を埋める
- multi-drone `drone.xml` を出力する

このツールは、spawn layout までは扱わない。
初期位置・姿勢は Hakoniwa 側の fleet instance が責務を持つため、XML generator は名前展開だけに集中する。

### 11.4 推奨する分割

責務分割は次を推奨する。

- `gen_fleet_scale_config.py`
  - fleet
  - pdudef
  - service
  - fleet instance 側の MuJoCo override 生成
- `gen_mujoco_multidrone_xml.py`
  - MuJoCo XML template 展開
  - 命名規則の付与

この分割の利点:

- JSON 系生成と XML 系生成を分離できる
- MuJoCo template のユーザカスタマイズ性を維持しやすい
- 既存の fleet/service 生成ロジックを再利用できる

### 11.5 実装順

実装順は次を想定する。

1. loader 側で fleet instance の `mujoco` override を扱えるようにする
2. sample として hand-authored `api-mujoco-instance-2.json` を置く
3. `gen_fleet_scale_config.py` を MuJoCo fleet 用に拡張する
4. `gen_mujoco_multidrone_xml.py` を新規追加する
5. 必要なら両者を束ねる wrapper を追加する

第 1 ステップでは 1 台 / 2 台を主対象とし、generator は設計方針だけを先に固める。

## 12. Generated Files and Responsibilities

MuJoCo fleet runtime を扱うときは、生成対象を明確に分けて管理する。
ここでは、何を生成するのか、どこへ出力するのか、どのツールが責務を持つのかを固定する。

### 12.1 生成ファイル一覧

| 区分 | ファイル | 役割 | 出力先 | 担当ツール |
| --- | --- | --- | --- | --- |
| fleet | `api-mujoco-instance-N.json` | fleet instance 一覧。`types`、`serviceConfigPath`、各機体の `name` / `position_meter` / `angle_degree` / `mujoco` override を持つ | `config/drone/fleets/` | `gen_fleet_scale_config.py` を MuJoCo 対応拡張 |
| type | `api-mujoco.json` | MuJoCo API 用の共通 type 設定 | `config/drone/fleets/types/` | hand-authored の canonical file |
| template | `mujoco-drone.xml.template` | 1 機分の MuJoCo body template | `config/drone/fleets/types/` | hand-authored の canonical file |
| service | `api-mujoco-instance-N-service.json` | 箱庭 RPC service 定義 | `config/drone/fleets/services/` | `gen_fleet_scale_config.py` を MuJoCo 対応拡張 |
| pdudef | `drone-pdudef-mujoco-instance-N.json` | service が参照する robot / pdutypes 定義 | `config/pdudef/` | `gen_fleet_scale_config.py` を MuJoCo 対応拡張 |
| mujoco runtime | `drone.xml` | N 機分を含む MuJoCo 実行用 XML | 当面は `config/drone/<runtime-name>/`、将来は runtime 出力ディレクトリでも可 | `gen_mujoco_multidrone_xml.py` |

### 12.2 役割分担

#### `api-mujoco.json`

- 共通設定の正本
- MuJoCo を使う API runtime の type 定義
- `modelPath` の default や controller mode を持つ

このファイルは hand-authored の canonical config とする。

#### `api-mujoco-instance-N.json`

- 複数機体の instance 一覧
- fleet compact config の入口
- 各機体の MuJoCo override を持つ

このファイルは、small-N では hand-authored sample として置いてもよい。
将来的には generator で出力できるようにする。

#### `api-mujoco-instance-N-service.json`

- 箱庭 RPC service の定義
- `DroneSetReady` / `DroneTakeOff` / `DroneGoTo` / `DroneGetState` / `DroneLand` を各機体ごとに持つ

service 定義は既存の fleet 系 generator で自動生成する対象である。

#### `drone-pdudef-mujoco-instance-N.json`

- service config が参照する PDU 定義
- robot 名と `pdutypes_id` を結ぶ

これも service config と対で generator が生成する。

#### `drone.xml`

- MuJoCo runtime が実際に読み込む XML
- `mujoco-drone.xml.template` から N 機分へ展開した結果

このファイルだけは、JSON generator ではなく MuJoCo XML generator が責務を持つ。

### 12.3 出力先の考え方

第 1 ステップでは、分かりやすさを優先して既存 config tree 配下へ出力する。

- fleet: `config/drone/fleets/`
- type/template: `config/drone/fleets/types/`
- service: `config/drone/fleets/services/`
- pdudef: `config/pdudef/`
- MuJoCo XML: `config/drone/<runtime-name>/`

ここで `<runtime-name>` は、たとえば次のような runtime 単位のディレクトリ名を想定する。

- `mujoco-2`
- `mujoco-api-2`
- `mujoco-shibuya-api-10`

ただし将来的には、runtime 生成物を `tmp/` や `generated/` に出す方式へ移行してもよい。

### 12.4 推奨するツール責務

#### `gen_fleet_scale_config.py` 拡張版

このツールに持たせる責務:

- `api-mujoco-instance-N.json` を生成する
- `drone-pdudef-mujoco-instance-N.json` を生成する
- `api-mujoco-instance-N-service.json` を生成する
- 必要なら `mujoco` override も各 instance に書き込む

このツールは JSON 系生成を担当する。

#### `gen_mujoco_multidrone_xml.py`

このツールに持たせる責務:

- `mujoco-drone.xml.template` を読む
- `drone_count` を受け取る
- 命名規則に従って 1 機分 body block を N 回展開する
- multi-drone `drone.xml` を出力する

このツールは XML 系生成を担当する。

### 12.5 重要な原則

生成物の責務を混ぜないことが重要である。

- fleet config は instance 一覧を持つ
- type config は共通仕様を持つ
- service config は RPC 定義を持つ
- pdudef は PDU 接続定義を持つ
- MuJoCo XML は物理モデル実体を持つ

この分離を維持することで、

- loader の責務
- generator の責務
- MuJoCo runtime の責務

を切り分けやすくなる。
