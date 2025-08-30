[English](docker-python-api.en.md) | 日本語

# TIPS

## WSL/docker 環境で箱庭&Python API連携方法

### 事前準備

- WSL2/Ubuntu環境にdockerをインストールしておく必要があります。
- dockerのインストール方法は、[こちら](docker-setup.md)を参照してください。
- Unityをインストールしておく必要があります。
- [hakoniwa-unity-drone](https://github.com/hakoniwalab/hakoniwa-unity-drone) のsimulationpプロジェクトを開き、`Scenes/WebAvatar` シーンを開いておく必要があります。


### 実行手順

1. Unityを起動します。
2. [箱庭ドローンシミュレータを起動します。](#箱庭ドローンシミュレータの起動)
3. Unityのシーンの WebAvatar を再生します。
4. [Python API サンプルを実行します。](#python-api)




#### 箱庭ドローンシミュレータの起動

以下を実行してください。

```bash
bash hakoniwa-drone-core/docker/run.bash
```

```bash
bash hakoniwa-drone-core/docker/tools/run-hako.bash api
```


#### Python API
以下を実行してください。

```bash
bash hakoniwa-drone-core/docker/attach.bash
```

```bash
cd hakoniwa-drone-core/drone_api
```

```bash
python3 rc/api_control_sample.py ../config/pdudef/webavatar.json
```

## 補足：

Python API 仕様は、以下を参照ください。

- https://github.com/toppers/hakoniwa-drone-core/tree/main/drone_api/libs

本サンプルコードは、以下を参照ください。

- https://github.com/toppers/hakoniwa-drone-core/blob/main/drone_api/rc/api_control_sample.py