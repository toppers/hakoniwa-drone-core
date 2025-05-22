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
    python3-dev \
    unzip \
    libffi-dev libbz2-dev libncurses5-dev libsqlite3-dev \
    liblzma-dev tk-dev xz-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && wget https://www.python.org/ftp/python/3.12.3/Python-3.12.3.tgz \
    && tar -xzf Python-3.12.3.tgz && cd Python-3.12.3 \
    && ./configure --enable-optimizations --enable-shared  \
    && make -j$(nproc) && make altinstall \
    && echo "/usr/local/lib" > /etc/ld.so.conf.d/python3.12.conf \
    && ldconfig \
	&& ln -sf /usr/local/bin/python3.12 /usr/bin/python3 \
	&& ln -sf /usr/local/bin/pip3.12 /usr/bin/pip3 \
    && cd .. && rm -rf Python-3.12.3*



# hakoniwa-core-cpp-client のインストール
WORKDIR /root
RUN git clone --recursive https://github.com/toppers/hakoniwa-core-cpp-client.git && \
    cd hakoniwa-core-cpp-client && \
    bash build.bash &&  \
    bash install.bash


# lnx.zip を取得し、バイナリと.soファイルを適切な場所に配置
RUN wget -O lnx.zip https://github.com/toppers/hakoniwa-drone-core/releases/latest/download/lnx.zip \
    && unzip lnx.zip -d lnx \
    && mkdir -p /usr/local/bin/hakoniwa \
    && mkdir -p /usr/local/lib/hakoniwa \
    && cp lnx/lnx/linux-* /usr/local/bin/hakoniwa/ \
    && chmod +x /usr/local/bin/hakoniwa/linux-* \
    && cp lnx/lnx/libhako_service_c.so /usr/local/lib/hakoniwa/ \
    && rm -rf lnx lnx.zip

# Python モジュールのインストール（必要に応じて追加）
RUN pip3 install --upgrade pip setuptools wheel \
    numpy


WORKDIR /root


