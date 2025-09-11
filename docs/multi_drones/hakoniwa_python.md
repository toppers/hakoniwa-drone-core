# これは何？

箱庭ドローン操作用 Python API を用いて、複数機体を同時に制御するための手順です。
基本的には、既存のサンプルスクリプトに対して **ドローン名を変更** するだけで、2 機体以上の制御が可能です。

# 事前準備

1 台での Python API 制御が動作していることを前提とします。

単体での制御方法については、以下の記事を参照してください：
[Unity＋Pythonでドローン制御：実習や授業にそのまま使える箱庭ドローンシミュレータ](https://qiita.com/kanetugu2018/items/d9763ceb4e527b50c7e2)

## Python API（複数機体）セットアップ

### サンプルスクリプト

`drone_api/rc` ディレクトリに複数の制御サンプルがあります。

```tree
drone_api/rc
├── api_control_sample.py   # Drone 用
├── api_control_sample2.py  # Drone1 用
```

* `api_control_sample.py` は **Drone**（1 台目）を制御するサンプルです。
* `api_control_sample2.py` は **Drone1**（2 台目）を制御するサンプルです。

それぞれを **別プロセスで同時実行** することで、複数機体を同時に制御できます。

---

## 実行手順

### 1) 箱庭（Docker）

```bash
bash hakoniwa-drone-core/docker/tools/run-hako.bash api \
  hakoniwa-drone-core/config/pdudef/webavatar-2.json 2
```

### 2) Python スクリプト（Docker 内）

```bash
cd hakoniwa-drone-core/drone_api

# 機体0 (Drone)
python3 rc/api_control_sample.py config/pdudef/webavatar-2.json

# 機体1 (Drone1)
python3 rc/api_control_sample2.py config/pdudef/webavatar-2.json
```

※ それぞれ別ターミナル（プロセス）で実行してください。

---

### 動作確認

Unity 上で、2 機のドローンが同時に離陸し、各サンプルコードに記述されたシナリオ（移動・荷物操作・センサ取得など）を実行することを確認します。

（シーン名は、`WebAvatar2`です）

---

## インスタンス対応表（例）

| 機体 | Drone名 (Python) | サンプルスクリプト                | 設定ファイル                |
| -- | --------------- | ------------------------ | --------------------- |
| 0  | `Drone`         | `api_control_sample.py`  | `drone_config_0.json` |
| 1  | `Drone1`        | `api_control_sample2.py` | `drone_config_1.json` |

