# legacy：v5.0.0で確かめていない古いサンプル（次の版で削除）

このディレクトリには、v4.2.0までのサンプルの機体設定を置いています。

- **v5.0.0では確かめていません。** v5.0.0からセンサモデル v2が標準になり、標準重力も9.80665 m/s²に
  揃えたため、ここの設定は読めますが、v4.2.0までと同じ結果にはなりません（非互換）。
- **次の版で削除します。** 使い続ける場合は、[v5.0.0への移行手順](../docs/upgrade_v5.0.0.md)を見て、
  `config/drone/x500-px4-sitl`を元に機体設定を作り直してください。
- 古い文書や起動の設定がここを参照している場合、その文書の冒頭に注意書きがあります。

## 移したもの

| 元の場所 | 移した先 |
| --- | --- |
| `config/drone/<名前>` | `legacy/config/drone/<名前>` |

対象：`api-1`、`ardupilot-1`、`ardupilot-2`、`mujoco`、`mujoco-2`、`mujoco-ardupilot-1`、
`mujoco-ardupilot-2`、`mujoco-px4`、`mujoco-px4-1`、`mujoco-px4-2`、`mujoco-shibuya-api-1`、
`mujoco-shibuya-api-2`、`mujoco-shibuya-api-10`、`px4-1`、`px4-2`、`rc-1`

v4.2.0までの状態が必要な場合は、`v4.2.0`タグとv4.2.0のバイナリを使ってください。
