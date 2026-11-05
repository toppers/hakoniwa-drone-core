# センサの設定を v1 の書き方から v2 の書き方へ（v1 相当の設定）

v5.0.0 から、センサは常にセンサモデル v2 で動きます。この文書は、v4.2.0 までの書き方（v1 の書き方）で書いた
センサの設定を、**同じ意味のまま v2 の書き方に書き直す**手順です。書き直した設定を「v1 相当の設定」と呼びます。

## v1 相当の設定にする理由

- v1 の書き方の設定も読めますが、一部の項目は v2 では使われません（GPS の `eph`・`epv`・`sacc`・`noise`）。
  読み込み時に `WARNING: unknown sensor setting` が出て、その設定は効きません。
- v2 の新しい項目（取り付けの位置と向き、ノイズの密度、ゆっくり変わるずれ、測れる範囲、分解能、振動など）は、
  先行公開の実験的な機能です。**PID の自動調整を行う機体には入れないでください。** GPS の位置のノイズや
  ドリフトを入れると、真値と比べる合格条件が成り立たず、調整がそもそも進まないことがあります。
  調整のときにどの誤差を入れるべきかは、今後の版で整理します。
- そのため、まずは v1 で使っていた誤差だけを、v2 の書き方で書きます。

## 書き直し方

**直すのは、自分の機体設定（`drone_config_0.json`）です。** PID の自動調整の手順を使う場合は、変換する前の
入力（`work/my-drone-config/drone_config_0.json`）を直します。変換のツールは、この入力を変えずに、
SITL 用のコピーを作ります。元のファイルは、別の場所に控えを取ってから直してください。

`components.sensors` の中だけを直します。それ以外の設定は変えません。

| v1 の書き方 | v2 の書き方 | 値 |
| --- | --- | --- |
| `gps.eph` | `gps.accuracy.horizontalM` | そのまま（m） |
| `gps.epv` | `gps.accuracy.verticalM` | そのまま（m） |
| `gps.sacc` | `gps.accuracy.speedMps` | そのまま（m/s） |
| `gps.noise` | `gps.positionNoise.horizontalM` と `gps.positionNoise.verticalM` | 同じ値を両方に（m） |
| （v1 にはない） | `gps.updatePeriodMsec` | `simulation.timeStep` を ms にした値（v1 は物理の刻みごとに測っていました。1 ms なら 1） |
| `gps.sampleCount`、`gps.delayMsec` | 同じ | そのまま |
| `acc`・`gyro`・`mag` の `sampleCount`、`noise`、`softDelayMsec` | 同じ | そのまま |
| `baro` の `sampleCount`、`noise`、`delayMsec` | 同じ | そのまま。下の注意を見てください |

`gps.accuracy` がすでに v2 の書き方で書かれている場合は、そのまま残します。

v1 の書き方で `gps.eph`・`gps.epv`・`gps.sacc` を書いていない場合は、`gps.accuracy` を足す必要はありません。
`gps.noise` だけを `gps.positionNoise` に直し、`gps.updatePeriodMsec` を足します。PX4・ArduPilot の SITL 用に
変換するツールは、精度の申告（`gps.accuracy`）がなければ、決まった値を補います（変換の報告に表示されます）。

**気圧のノイズ（`baro.noise`）の意味の違い：** v1 は同じ σ を気圧（Pa）と気圧高度（m）の両方に足していました。
v2 は `noise` を高度の σ（m）と決めていて、その高度の誤差から、つじつまの合う気圧を作ります。値はそのまま使い、
v2 では高度の σ（m）として読まれることに注意してください。

## 例：x500

`config/drone/x500-px4-sitl/drone_config_0.json` の GPS は、次のように書き直してあります。

v1 の書き方：

```json
"gps": {
  "sampleCount": 1,
  "noise": 0.0,
  "sacc": 0.1,
  "eph": 0.2,
  "epv": 0.3,
  "delayMsec": 100
}
```

v2 の書き方（v1 相当の設定）：

```json
"gps": {
  "sampleCount": 1,
  "updatePeriodMsec": 1,
  "positionNoise": {
    "horizontalM": 0.0,
    "verticalM": 0.0
  },
  "accuracy": {
    "horizontalM": 0.2,
    "verticalM": 0.3,
    "speedMps": 0.1
  },
  "delayMsec": 100
}
```

## 結果を同じにしたいとき：乱数の種

センサのノイズの乱数は、`simulation.randomSeed` で種を決められます（[センサの共通仕様](README.md) 4.1）。
書かなければ、実行のたびに違う並びになり、PID の自動調整の結果も回ごとにばらつきます。同じ設定から同じ結果を
出したいときは、整数の種を書きます。

```json
"simulation": {
  "randomSeed": 1
}
```

## 確かめ方

機体を起動して、読み込みのメッセージを確かめます。

- `WARNING: unknown sensor setting` が出ないこと。出たら、その項目を上の表のとおりに直します。
- `INFO: sensor model v2 [<機体名>] setting: gps.accuracy`、`gps.positionNoise` のように、書いた項目が表示されること。

起動直後に一度だけ `WARNING: invalid sea-level atmosphere; keeping previous values` が出ることがあります。
最初の刻みで外乱の値がまだ届いていないためで、標準大気（1013.25 hPa、15 ℃）を使い続けます。結果には影響しません。
