# x500 と PX4 SITL（WSL2 / Ubuntu）

このディレクトリは、Hakoniwa Drone Simulator 4.2.0 の x500 クラス機体モデルと PX4 SITL 用の設定です。物理刻みは 1 ms、PX4 とのセンサー／制御更新周期は 4 ms です。PX4 SITL は WSL2 ホスト、箱庭と Python の飛行命令は Docker コンテナで動かします。

> x500 は公開情報から推定したモデルであり、メーカー公認のモデルではありません。

## 構成と前提

WSL2 の Ubuntu と Docker を用意し、Windows の `/mnt/c` ではなく WSL2 の Linux ファイルシステムで作業します。`~/project` の下に `hakoniwa-drone-core` と `PX4-Autopilot` を並べます。

```text
~/project/
├── hakoniwa-drone-core/       # Docker を起動する場所
└── PX4-Autopilot/             # WSL2 ホストで SITL を起動する場所
```

この手順は `toppersjp/hakoniwa-drone-core:v4.2.0` を使用します。イメージに含まれる Linux 実行バイナリは Release の `lnx.zip`（SHA-256: `344aac4b6bc1f2d82205c7740b574d0439eb9359363bcd6d69ef427587a865b0`）と同一のため、ここでは `-p lnx.zip` を付けません。`-p` は手元の Release 配布物でイメージ内バイナリを明示的に上書きしたい場合にだけ使います。

公開後は x500 の設定、x500 用 launcher、以下の手順書が drone-core に含まれます。公開前の検証では、その三つを同じパスへ置いてください。

```bash
mkdir -p ~/project
cd ~/project
git clone --recursive https://github.com/toppers/hakoniwa-drone-core.git
# 公開前だけ: config/drone/x500-px4-sitl/、config/launcher/x500-px4-sitl-wsl2.launch.json、
# tools/launch-x500-px4-sitl-wsl2.bash を取得元と同じ相対パスに配置する。
```

`--recursive` は必須です。省略すると PDU 定義に必要なサブモジュールが取得されません。

## PX4-Autopilot を取得してビルドする

検証済み PX4 は `a1726d316a941af9524f6279eb293a713d8fdcac`（`v1.17.0-alpha1-1702-ga1726d316a`）です。次は `~/project`、すなわち drone-core と PX4 の親ディレクトリから実行します。

```bash
cd ~/project
git clone --recursive https://github.com/PX4/PX4-Autopilot.git
cd PX4-Autopilot
git checkout a1726d316a941af9524f6279eb293a713d8fdcac
git submodule update --init --recursive
cd ..
bash hakoniwa-drone-core/tools/px4/build.bash PX4-Autopilot
```

`Tools/setup/ubuntu.sh` が再ログインを求めた場合は、WSL を再起動または再ログインしてから、最後の build コマンドを再実行します。

## airframe 900003 を追加する

`px4-params.txt` は airframe 本文です。標準ヘッダと `rc.mc_defaults` の読み込みを加え、ビルド済みの airframe ディレクトリに配置します。設定ファイルだけの追加なので、この後に PX4 を再ビルドする必要はありません。

```bash
cd ~/project/PX4-Autopilot
{
  cat <<'EOF'
#!/bin/sh
#
# @name Hakoniwa x500
# @type Quadrotor x
# @maintainer Hakoniwa

. ${R}etc/init.d/rc.mc_defaults
EOF
  cat ../hakoniwa-drone-core/config/drone/x500-px4-sitl/px4-params.txt
} > build/px4_sitl_default/etc/init.d-posix/airframes/900003_hakoniwa_x500
chmod +x build/px4_sitl_default/etc/init.d-posix/airframes/900003_hakoniwa_x500

# 以前の機体の保存値を使わない。
rm -f build/px4_sitl_default/rootfs/parameters.bson \
      build/px4_sitl_default/rootfs/parameters_backup.bson
```

## 起動する

3 個の WSL2 端末を開きます。ビューアは不要です。Docker は WSL2 では `--net host` で起動するため、コンテナとホストの `127.0.0.1` は同じネットワーク名前空間として使えます。

| 接続 | 待受・送信元 | 接続先 | ポート |
| --- | --- | --- | --- |
| simulator MAVLink | 箱庭（コンテナ）の aircraft service | PX4（ホスト） | TCP 4560 |
| 制御 MAVLink | PX4（ホスト）が送信 | `hakosim_mavlink`（コンテナ） | UDP 14540 |

2 機目は TCP 4561、UDP 14541 のように 1 ずつ増やします。Windows の QGroundControl だけは WSL2 の IP と UDP 14550 を使用します。

### 端末 1: 箱庭（Docker）

Docker イメージは事前にローカルに用意してください。ここで `docker pull` はしません。

```bash
cd ~/project/hakoniwa-drone-core
bash docker/run.bash --launcher tools/launch-x500-px4-sitl-wsl2.bash
```

この端末は起動したままにします。`x500-px4-sitl-wsl2.launch.json` は x500 の `drone_config_0.json` を使うため、既存の `mujoco-px4-1` に決め打ちされた launcher は使いません。

### 端末 2: PX4 SITL（WSL2 ホスト）

`tools/px4/run.bash` は airframe 10016 に決め打ちのため使用せず、x500 の 900003 を直接指定します。

```bash
cd ~/project/PX4-Autopilot
export PX4_HOME_LAT=47.641468
export PX4_HOME_LON=-122.140165
export PX4_HOME_ALT=121.321
export PX4_SIM_HOSTNAME=127.0.0.1
export PX4_SIM_PORT=4560
export PX4_MAVLINK_UDP_PORT=14540
PX4_SYS_AUTOSTART=900003 PX4_SIM_MODEL=none_iris \
  ./build/px4_sitl_default/bin/px4 -i 0
```

`[simulator_mavlink] ... port 4560`、`[mavlink] mode: Onboard ... remote port 14540`、`Ready for takeoff!` が出るまで待ちます。PX4 のプロンプトで次を実行し、値が 100 であることを確認します。

```text
param show SENS_GPS0_DELAY
```

`px4-rc.mavlinksim` が既定値を 10 に設定しても、airframe の `param set SENS_GPS0_DELAY 100` が実行値を 100 にします。

## mission JSON で離陸・移動・着陸を確認する

端末 3 で実行します。`docker/attach.bash` で、端末 1 のコンテナに入り、コンテナ内の `/root/workspace` から公開の pymavlink 例を実行します。

```bash
cd ~/project/hakoniwa-drone-core
bash docker/attach.bash
cd /root/workspace/drone_api/pymavlink
python3 env_test.py --name Drone --connect udp:127.0.0.1:14540 \
  --type px4 --mission-file mission.json
```

`mission.json` は、高度 20 m、複数の `moveToPosition`、最後の `land` を順に指定する公開の JSON です。`Takeoff successful.`、各 `Move successful.`、`Landed successfully.`、`Mission completed successfully` を確認します。実行ログの各 `[DONE] Reached target: pos_err=...` が、各目標地点の位置誤差です。2 回以上繰り返してください。

終了時は端末 2 の PX4 を `Ctrl-C`、端末 1 の Docker 起動を `Ctrl-C` で停止します。

## つながらないとき

- ホストで `ss -ltnp | grep 4560` を実行し、箱庭の aircraft service が TCP 4560 を待ち受けていることを確認します。
- PX4 ログで `simulator_mavlink` の TCP 4560 接続行と、`[mavlink] ... remote port 14540` を確認します。後者が無ければ PX4 が Python 側へ UDP を送っていません。
- heartbeat が sysid 0 のままなら、ホストで `ss -lunp | grep 1454` を実行し、UDP 14540 を別のプロセスが受けていないか確認します。コンテナ内でも同じコマンドを実行し、`udp:127.0.0.1:14540` が見えることを確認します。
- GPS または磁気で EKF が進まない場合は、機体設定の初期位置（47.641468, -122.140165, 121.321 m）と磁場偏角（15.0°）を確認します。

## ファイル

- `drone_config_0.json`: 箱庭の機体・物理・センサー設定
- `drone.xml`: MuJoCo モデル
- `px4-params.txt`: airframe 900003 に入れる PX4 パラメータ
- `../../launcher/x500-px4-sitl-wsl2.launch.json`: Docker 内で x500 aircraft service を起動する launcher 定義

PX4 がフライトコントローラを担当するため、箱庭内蔵コントローラおよび Control Link バックエンドは使用しません。
