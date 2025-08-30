[English](docker-ardupilot.en.md) | 日本語

# TIPS

## WSL/docker 環境で箱庭&Ardupilot連携方法

### 事前準備

- WSL2/Ubuntu環境にdockerをインストールしておく必要があります。
- dockerのインストール方法は、[こちら](docker-setup.md)を参照してください。
- Mission Plannerをインストールしておく必要があります。
- Unityをインストールしておく必要があります。
- [hakoniwa-unity-drone](https://github.com/hakoniwalab/hakoniwa-unity-drone) のsimulationpプロジェクトを開き、`Scenes/WebAvatar` シーンを開いておく必要があります。
- Ardupilot をビルドしておく必要があります。
- Ardupilotのビルド方法は、[こちら](ardupilot-setup.md)を参照してください。
- ホストPCのIPアドレスを確認しておく必要があります。 power shellを起動し、以下のコマンドを実行してください。

```powershell
ipconfig
```

### 実行手順

1. Mission Plannerを起動します。
2. Unityを起動します。
3. [Ardupilot を起動します。](#ardupilotの起動)
4. [箱庭ドローンシミュレータを起動します。](#箱庭ドローンシミュレータの起動)
5. Unityのシーンを再生します。

#### Ardupilotの起動

以下を実行してください。

```bash
bash tools/ardupilot/run.bash <ardupilot-path> <HOST_IP>
```

`<ardupilot-path>` には、Ardupilotのパスを指定してください。  
`<HOST_IP>` には、ホストPCのIPアドレスを指定してください。

例：
```bash
tmori@WinHako:~/project/hakoniwa-drone-core$ bash tools/ardupilot/run.bash ../ardupilot  192.168.2.156
SIM_VEHICLE: Start
SIM_VEHICLE: Killing tasks
SIM_VEHICLE: Starting up at SITL location
SIM_VEHICLE: WAF build
SIM_VEHICLE: Configure waf
SIM_VEHICLE: "/home/tmori/project/ardupilot/modules/waf/waf-light" "configure" "--board" "sitl"
```

#### 箱庭ドローンシミュレータの起動

以下を実行してください。

```bash
bash hakoniwa-drone-core/docker/run.bash
```

```bash
bash hakoniwa-drone-core/docker/tools/run-hako.bash ardupilot
```

成功すると、Mission Planner が反応します。