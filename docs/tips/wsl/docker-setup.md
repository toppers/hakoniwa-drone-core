[English](docker-setup.en.md) | 日本語

# TIPS

## WSL/docker 環境のセットアップ方法

Docker Desktop for Windows を利用せずに、WSL2/Ubuntu環境に直接 docker をインストールして使用できるようになります。

本環境のメリット：

- Docker Desktop for Windows のライセンスの問題を回避できる
- Docker Desktop for Windows の起動待ち時間が不要
- WSL2/Ubuntu環境で直接 docker を使用できるため、Linux環境での開発が容易になる

### docker のインストール

以下を実行してください。

```bash
bash docker/wsl-docker-install.bash
```

途中で、パスワードの入力を求められますので、Ubuntuのユーザーパスワードを入力してください。

### docker の起動

以下を実行してください。

```bash
bash docker/wsl-docker-activate.bash
```

### docker イメージの取得

以下を実行してください。

```bash
bash docker/pull-image.bash
```

成功すると、こうなります。

```bash
$ docker images
REPOSITORY                      TAG       IMAGE ID       CREATED        SIZE
toppersjp/hakoniwa-drone-core   v1.0.0    cb5d12d6b7ba   17 hours ago   1.28GB
```


### docker コンテナの起動
以下を実行してください。

```bash
bash docker/run.bash
```

成功すると、コンテナにログインし、以下のようになります。

```bash
$ bash docker/run.bash 
x86_64
wsl2
root@WinHako:~/workspace# ls
README.md  config  docker  docs  drone_api  drone_log0  include  mavlink  sample  src  thirdparty  tools
```

### 起動されたコンテナへのログイン

以下を実行してください。

```bash
bash docker/attach.bash
```

### docker コンテナの停止

`exit` コマンドでコンテナを停止します。

```bash
root@WinHako:~/workspace# exit
exit
```