# TIPS

## WSL/docker 環境で箱庭&PX4連携方法

### 事前準備

- WSL2/Ubuntu環境にdockerをインストールしておく必要があります。
- dockerのインストール方法は、[こちら](docker-setup.md)を参照してください。
- QGC をインストールしておく必要があります。
- Unityをインストールしておく必要があります。
- [hakoniwa-unity-drone](https://github.com/hakoniwalab/hakoniwa-unity-drone) のsimulationpプロジェクトを開き、`Scenes/WebAvatar` シーンを開いておく必要があります。
- PX4 をビルドしておく必要があります。
- PX4 のビルド方法は、[こちら](px4-setup.md)を参照してください。


### 実行手順

1. QGC を起動します。
2. Unityを起動します。
3. [PX4 を起動します。](#PX4の起動)
4. [箱庭ドローンシミュレータを起動します。](#箱庭ドローンシミュレータの起動)
5. Unityのシーンを再生します。

#### PX4の起動

以下を実行してください。

```bash
bash hakoniwa-drone-core/tools/px4/run.bash
```

例：
```bash
tmori@WinHako:~/qiita$ bash hakoniwa-drone-core/tools/px4/run.bash
[0/1] launching px4 none_iris (SYS_AUTOSTART=10016)

______  __   __    ___
| ___ \ \ \ / /   /   |
| |_/ /  \ V /   / /| |
|  __/   /   \  / /_| |
| |     / /^\ \ \___  |
\_|     \/   \/     |_/

px4 starting.

INFO  [px4] startup script: /bin/sh etc/init.d-posix/rcS 0
env SYS_AUTOSTART: 10016
INFO  [param] selected parameter default file parameters.bson
INFO  [param] importing from 'parameters.bson'
INFO  [parameters] BSON document size 350 bytes, decoded 350 bytes (INT32:15, FLOAT:3)
INFO  [param] selected parameter backup file parameters_backup.bson
INFO  [dataman] data manager file './dataman' size is 1208528 bytes
INFO  [init] PX4_SIM_HOSTNAME: 127.0.0.1
INFO  [simulator_mavlink] using TCP on remote host 127.0.0.1 port 4560
WARN  [simulator_mavlink] Please ensure port 4560 is not blocked by a firewall.
INFO  [simulator_mavlink] Resolved host '127.0.0.1' to address: 127.0.0.1
INFO  [simulator_mavlink] Waiting for simulator to accept connection on TCP port 4560
```

#### 箱庭ドローンシミュレータの起動

以下を実行してください。

```bash
bash hakoniwa-drone-core/docker/run.bash
```

```bash
bash hakoniwa-drone-core/docker/tools/run-hako.bash px4
```

成功すると、QGC が反応します。

