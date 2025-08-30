[English](docker-gamepad.en.md) | 日本語

# TIPS

## WSL/docker 環境で箱庭&ゲームパッド操作方法

### 事前準備

- WSL2/Ubuntu環境にdockerをインストールしておく必要があります。
- dockerのインストール方法は、[こちら](docker-setup.md)を参照してください。
- Unityをインストールしておく必要があります。
- PS4/PS5コントローラーをUSB接続しておく必要があります。
- [hakoniwa-unity-drone](https://github.com/hakoniwalab/hakoniwa-unity-drone) のsimulationpプロジェクトを開き、`Scenes/WebAvatar` シーンを開いておく必要があります。


### 実行手順

1. Unityを起動します。
2. [箱庭ドローンシミュレータを起動します。](#箱庭ドローンシミュレータの起動)
3. Unityのシーンの WebAvatar を再生します。
4. [ゲームパッド操作します。](#ゲームパッド操作)



#### 箱庭ドローンシミュレータの起動

以下を実行してください。

```bash
bash hakoniwa-drone-core/docker/run.bash
```

```bash
bash hakoniwa-drone-core/docker/tools/run-hako.bash rc
```


#### ゲームパッド操作

PS4/PS5コントローラーをUSB接続している場合、以下の操作でドローンを操作できます。

- Xボタン： ARM/DISARM
- ○ボタン： 荷物着脱
- □ボタン：　カメラ撮影

- ↑ボタン： カメラアップ
- ↓ボタン： カメラダウン


- 左スティック（上下）： 上昇/下降
- 左スティック（左右）： 左右旋回
- 右スティック（上下）： 前後移動
- 右スティック（左右）： 左右移動

補足：

PS4/PS5コントローラは、Unity側でイベントハンドリングし、そのイベントを docker側にWebSocketで送信しています。