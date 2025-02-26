FROM ubuntu:22.04 as hakoniwa-ardupilot-sitl

ARG DEBIAN_FRONTEND=noninteractive

# 必要なパッケージをインストール
RUN apt-get update && apt-get install -y \
    sudo \
    git \
    python3 \
    python3-pip \
    python3-matplotlib \
    python3-numpy \
    python3-opencv \
    python3-pyqt5 \
    python3-dev \
    python3-setuptools \
    python3-wheel \
    python3-pip \
    build-essential \
    g++ \
    gcc \
    cmake \
    make \
    pkg-config \
    wget \
    screen \
    nano \
    xz-utils \
    && rm -rf /var/lib/apt/lists/*

# ArduPilotの環境をセットアップ
RUN git clone --recurse-submodules https://github.com/ArduPilot/ardupilot.git /ardupilot
RUN git config --global --add safe.directory /ardupilot 

# 通常ユーザーを作成し、sudo 権限を付与
RUN useradd -m -s /bin/bash ardupilot && \
    mkdir -p /etc/sudoers.d && \
    echo "ardupilot ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/ardupilot && \
    chmod 0440 /etc/sudoers.d/ardupilot && \
    chown -R ardupilot:ardupilot /ardupilot  # 所有者変更を追加

# ArduPilotの依存パッケージをインストール
RUN apt-get update && apt-get install -y curl

# `usermod` のエラーを回避するために `USER` 環境変数を設定
ENV USER=ardupilot

# `ardupilot` ユーザーに切り替え
USER ardupilot
WORKDIR /ardupilot

# `sudo` のパスを明示的に設定
ENV PATH="/usr/bin:/usr/sbin:/bin:/sbin"

# ArduPilotの依存パッケージをインストール
RUN ./Tools/environment_install/install-prereqs-ubuntu.sh -y

# rootユーザーに戻す
USER root

# `empy`、`future`、`MAVProxy` をインストール
RUN pip3 install empy==3.3.4 future MAVProxy

# `MAVProxy` のパスを `PATH` に追加
ENV PATH=$PATH:/usr/local/bin


# **ArduPilot SITL を事前にビルドしてキャッシュ**
RUN ./waf configure --board sitl
RUN ./waf copter

RUN apt-get install -y netcat-openbsd

# SITLを実行できるようにする
CMD ["/bin/bash"]
