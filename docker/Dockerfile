FROM ubuntu:24.04 as hakoniwa-drone-core

ARG DEBIAN_FRONTEND=noninteractive

ENV PATH="/usr/local/bin/hakoniwa:${PATH}" \
    LD_LIBRARY_PATH="/usr/local/lib/hakoniwa:${LD_LIBRARY_PATH}" \
    PYTHONPATH="/usr/local/lib/hakoniwa/py:${PYTHONPATH}" \
    HAKO_BINARY_PATH="/usr/local/lib/hakoniwa/hako_binary/offset"

    RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    vim \
    libssl-dev libreadline-dev zlib1g-dev \
    autoconf \
    automake \
    pkg-config \
    curl \
    net-tools \
    netcat-openbsd \
    gcc g++ make cmake \
    git jq libgtest-dev \
    python3 python3-pip python3-dev \
    unzip \
    libffi-dev libbz2-dev libncurses5-dev libsqlite3-dev \
    liblzma-dev tk-dev xz-utils \
    iproute2 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*




# hakoniwa-core-cpp-client のインストール
WORKDIR /root
RUN git clone --recursive https://github.com/toppers/hakoniwa-core-cpp-client.git && \
    cd hakoniwa-core-cpp-client && \
    bash build.bash &&  \
    bash install.bash


# Python モジュールのインストール（必要に応じて追加）
RUN pip3 install --break-system-packages numpy scipy \
 && pip3 install --break-system-packages aiohttp>=3.10.0 aiohttp_cors>=0.7.0 websockets==13.1


RUN apt-get update && apt-get install iproute2 -y

# lnx.zip を取得し、バイナリと.soファイルを適切な場所に配置
RUN wget -O lnx.zip https://github.com/toppers/hakoniwa-drone-core/releases/latest/download/lnx.zip \
    && unzip lnx.zip -d lnx \
    && mkdir -p /usr/local/bin/hakoniwa \
    && mkdir -p /usr/local/lib/hakoniwa \
    && cp lnx/lnx/linux-* /usr/local/bin/hakoniwa/ \
    && chmod +x /usr/local/bin/hakoniwa/linux-* \
    && cp lnx/lnx/libhako_service_c.so /usr/local/lib/hakoniwa/ \
    && rm -rf lnx lnx.zip


WORKDIR /root


