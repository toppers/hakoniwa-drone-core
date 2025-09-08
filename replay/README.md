# Hakoniwa Drone – Log Replay 機能

## 概要
本機能は、箱庭ドローンシミュレータで記録された `drone_dynamics.csv` ログを元に、ドローンの飛行状態を再現（リプレイ）する機能です。
HakoniwaのConductor（手動タイミング制御モード）と連携し、指定された時間間隔でログデータをPDUとして共有メモリに書き込みます。

シミュレーション環境（Unity/Unreal）と同じPDUインターフェースを利用するため、**実機シミュレーションとリプレイ再生を透過的に切り替える**ことが可能です。
内部では `pandas` ライブラリを利用して、効率的な時系列データの処理を実現しています。

---

## 機能一覧
- **ログ再生**
  - `drone_dynamics.csv` を再生対象とします。
  - 時系列に沿ってPDU（Twist型）を生成し、共有メモリに書き込みます。
- **複数機体対応**
  - `drone_log0`, `drone_log1` のように、複数のログディレクトリを同時に再生できます。
  - 各ログとドローン名・PDU名をマッピングして管理します。
- **再生制御**
  - 再生範囲の指定（時刻 or 秒）
  - 再生速度の変更（例: 0.5倍速でのスロー再生）
- **データハンドリング**
  - ログ読み込み時に、不正なデータ（NaN/inf）やタイムスタンプの乱れを自動的にクレンジングします。
  - 座標系をシミュレータで標準的なNED座標系から、ROSなどで一般的なROS座標系へ変換して出力します。

---

## モジュール構成

```
replay/
├── __init__.py
├── clock.py                 # グローバルなリプレイ時刻を管理
├── hako_asset_replayer.py   # ログ再生の実行、PDUへの書き込み、Hakoniwaアセットとしての登録
├── logdata_model.py         # CSVログをパースし、データクレンジングと時系列アクセスを提供
└── replay_model.py          # replay.json ファイルを読み込み、再生設定を管理
```

### 各モジュールの役割
- **hako_asset_replayer.py**
  本機能のエントリーポイントです。Hakoniwaアセットとして登録され、Conductorからの指示で手動タイミング制御ループを実行します。
  内部で `DroneReplayer` を管理し、各ドローンのログデータをPDUとして共有メモリに書き込みます。

- **replay_model.py**
  設定ファイル `replay.json` を読み込み、パースする責務を持ちます。
  再生対象のログ、ドローン名、PDU設定、再生範囲、速度などを解釈し、`HakoAssetReplayer` が利用できる形式に変換します。

- **logdata_model.py**
  `drone_dynamics.csv` を `pandas` DataFrameとして読み込みます。
  必須フィールドの検証、不正値の除去、タイムスタンプの単調増加保証などのクレンジング処理を行った後、座標系をNEDからROSに変換します。

- **clock.py**
  リプレイ中の時刻（マイクロ秒単位）を管理するためのシンプルなクラスです。
  開始・終了時刻や、次のタイムステップへの進行を管理します。

---

## Replay 設定ファイル (`replay.json`)

リプレイの挙動は `replay.json` ファイルで定義します。

### 設定項目
- `log_map` (必須): 再生したいログディレクトリと、対応するドローン名・PDU名をマッピングします。
  - `(key)`: `drone_log0` のようなログディレクトリへのパス。
  - `drone_name`: Hakoniwaアセット名。
  - `pdu_name`: PDUのチャンネル名（例: "pos"）。
- `pdu_def_file` (必須): PDUの構造を定義したJSONファイルのパス。
- `start_time`: リプレイの基準となる開始時刻（`HH:MM:SS.ffffff`形式）。`range_sec` と組み合わせて使用します。
- `range_sec`: `start_time` からの相対秒数で再生範囲を指定します。こちらが `range_timestamp` より優先されます。
  - `begin`: 開始秒。
  - `end`: 終了秒。
- `range_timestamp`: 絶対時刻で再生範囲を指定します。
  - `begin`: 開始時刻 (`HH:MM:SS.ffffff`形式)。
  - `end`: 終了時刻 (`HH:MM:SS.ffffff`形式)。
- `speed`: 再生速度。`1.0` が等速、`0.5` は0.5倍速（スロー再生）になります。

### `replay.json` の記述例

```json
{
  "log_map": {
    "../drone_log1": {
      "drone_name": "Drone",
      "pdu_name": "pos"
    }
  },
  "pdu_def_file": "config/pdudef/webavatar-2.json",
  "start_time": "00:00:00.000",
  "range_sec": {
    "description": "start_timeからの相対秒数。range_timestampより優先される。",
    "begin": 65,
    "end": 100
  },
  "range_timestamp": {
    "begin": "00:01:05.000",
    "end": "00:01:40.000"
  },
  "speed": 1.0
}
```

---

## 実行方法

以下のコマンドでリプレイ機能を開始します。
`hakopy` の `conductor_start()` が呼び出され、手動タイミングモードでリプレイが実行されます。

```bash
# プロジェクトルートディレクトリから実行
python3 -m replay.hako_asset_replayer --replay config/replay/replay.json
```

### コマンドライン引数
- `--replay` (必須): `replay.json` ファイルへのパス。
- `--delta-time-msec`: PDUを書き込む時間間隔（ミリ秒）。デフォルトは `3`。
- `--asset-name`: Hakoniwaに登録するアセット名。デフォルトは `AssetReplayer`。
- `--quiet`: 詳細なログ出力を抑制します。