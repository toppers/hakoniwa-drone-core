FROM ubuntu:24.04 AS hakoniwa-drone-core

ARG DEBIAN_FRONTEND=noninteractive
ARG HAKO_CORE_PRO_REPO="https://github.com/hakoniwalab/hakoniwa-core-pro.git"
ARG HAKO_CORE_PRO_REF="c0b700a744aaa81d3f8ce1c354439d981bc1046d"
ARG HAKO_PDU_ENDPOINT_REPO="https://github.com/hakoniwalab/hakoniwa-pdu-endpoint.git"
ARG HAKO_PDU_ENDPOINT_REF="fddc10e6929ac4e75cdc015b53e0b405147cd6bb"
ARG HAKO_PDU_BRIDGE_CORE_REPO="https://github.com/hakoniwalab/hakoniwa-pdu-bridge-core.git"
ARG HAKO_PDU_BRIDGE_CORE_REF="957e7fc14119994f2fa2e22f13a1acdf5463ad87"
ARG HAKO_THREEJS_DRONE_REPO="https://github.com/hakoniwalab/hakoniwa-threejs-drone.git"
ARG HAKO_THREEJS_DRONE_REF="c31960fb28eaf15e936d4a7b19aa8c5cdcd3c096"
ARG CMAKE_BUILD_JOBS=4

ENV PATH="/usr/local/hakoniwa/bin:/usr/local/bin/hakoniwa:${PATH}" \
    PYTHONPATH="/usr/local/lib/python3.12/dist-packages" \
    LD_LIBRARY_PATH="/usr/local/hakoniwa/lib" \
    HAKO_BINARY_PATH="/usr/share/hakoniwa/offset" \
    HAKO_PRO_PACKAGE="/opt/pro/lnx.zip" \
    HAKO_PRO_DIR="/opt/pro/lnx"

# 基本パッケージ（--no-install-recommends で軽量化）
RUN apt-get update && apt-get install -y --no-install-recommends \
    sudo \
    build-essential \
    mesa-common-dev libgl1-mesa-dev libglu1-mesa-dev xorg-dev \
    libglfw3-dev libgtest-dev libspdlog-dev \
    libboost-dev \
    libssl-dev libreadline-dev zlib1g-dev \
    autoconf automake pkg-config \
    curl wget jq git \
    net-tools netcat-openbsd iproute2 \
    gcc g++ make cmake \
    python3 python3-pip python3-dev \
    unzip \
    libffi-dev libbz2-dev libncurses5-dev libsqlite3-dev \
    liblzma-dev tk-dev xz-utils vim \
     && rm -rf /var/lib/apt/lists/*

COPY MUJOCO_VERSION.txt .
# MuJoCo
RUN MUJOCO_VERSION=$(cat MUJOCO_VERSION.txt) && \
    ARCH=$(dpkg --print-architecture) && \
    if [ "$ARCH" = "amd64" ]; then MUJOCO_ARCH="x86_64"; fi && \
    if [ "$ARCH" = "arm64" ]; then MUJOCO_ARCH="aarch64"; fi && \
    wget -O mujoco.tar.gz "https://github.com/google-deepmind/mujoco/releases/download/${MUJOCO_VERSION}/mujoco-${MUJOCO_VERSION}-linux-${MUJOCO_ARCH}.tar.gz" && \
    mkdir -p /usr/local/mujoco && \
    tar -xzf mujoco.tar.gz -C /usr/local/mujoco --strip-components=1 && \
    rm mujoco.tar.gz && \
    echo "/usr/local/mujoco/lib" > /etc/ld.so.conf.d/mujoco.conf && \
    ldconfig


# hakoniwa-core（source build）
WORKDIR /root
RUN git clone "${HAKO_CORE_PRO_REPO}" hakoniwa-core-pro \
    && git -C hakoniwa-core-pro checkout --detach "${HAKO_CORE_PRO_REF}" \
    && git -C hakoniwa-core-pro submodule update --init --recursive
WORKDIR /root/hakoniwa-core-pro
RUN bash build.bash
RUN bash install.bash
WORKDIR /root

# hakoniwa-pdu-endpoint（bridge-core 依存）
RUN pip3 install --no-cache-dir --break-system-packages cffi
ENV PYTHONPATH="/usr/local/hakoniwa/share/hakoniwa-pdu-endpoint/python:${PYTHONPATH}"
RUN git clone "${HAKO_PDU_ENDPOINT_REPO}" hakoniwa-pdu-endpoint \
    && git -C hakoniwa-pdu-endpoint checkout --detach "${HAKO_PDU_ENDPOINT_REF}" \
    && git -C hakoniwa-pdu-endpoint submodule update --init --recursive
WORKDIR /root/hakoniwa-pdu-endpoint
RUN bash build.bash
RUN bash install.bash
WORKDIR /root

# hakoniwa-pdu-bridge-core（web bridge バイナリ）
RUN git clone "${HAKO_PDU_BRIDGE_CORE_REPO}" hakoniwa-pdu-bridge-core \
    && git -C hakoniwa-pdu-bridge-core checkout --detach "${HAKO_PDU_BRIDGE_CORE_REF}" \
    && git -C hakoniwa-pdu-bridge-core submodule update --init --recursive
COPY docker/config/hakoniwa-pdu-bridge-core.yaml /opt/hakoniwa-build/hakoniwa-pdu-bridge-core.yaml
WORKDIR /root/hakoniwa-pdu-bridge-core
RUN python3 tools/hako.py build \
      --config /opt/hakoniwa-build/hakoniwa-pdu-bridge-core.yaml
RUN python3 tools/hako.py install \
      --config /opt/hakoniwa-build/hakoniwa-pdu-bridge-core.yaml \
      --install-dir /usr/local/hakoniwa
WORKDIR /root

# threejs viewer（fleets web 配信用）
RUN git clone "${HAKO_THREEJS_DRONE_REPO}" /opt/hakoniwa-threejs-drone \
    && git -C /opt/hakoniwa-threejs-drone checkout --detach "${HAKO_THREEJS_DRONE_REF}" \
    && git -C /opt/hakoniwa-threejs-drone submodule update --init --recursive

# Python（>= のクォートを忘れずに）
RUN pip3 install --no-cache-dir --break-system-packages numpy scipy \
 && pip3 install --no-cache-dir --break-system-packages "aiohttp>=3.10.0" "aiohttp_cors>=0.7.0" "websockets==13.1" \
 && pip3 install --no-cache-dir --break-system-packages hakoniwa-pdu pymavlink \
 && pip3 install --no-cache-dir --break-system-packages panda3d

# OSS版 lnx.zip を取得・配置（PROは起動時にentrypointで上書き）
RUN wget -O lnx.zip https://github.com/toppers/hakoniwa-drone-core/releases/latest/download/lnx.zip \
    && unzip lnx.zip -d lnx \
    && mkdir -p /usr/local/bin/hakoniwa /usr/local/lib/hakoniwa \
    && cp lnx/lnx/linux-* /usr/local/bin/hakoniwa/ \
    && chmod +x /usr/local/bin/hakoniwa/linux-* \
    && cp lnx/lnx/libhako_service_c.so /usr/local/lib/hakoniwa/ \
    && rm -rf lnx lnx.zip \
    # ライブラリ検索パスへ登録（これがないと .so が見つからないことがある） \
    && echo "/usr/local/lib/hakoniwa" > /etc/ld.so.conf.d/hakoniwa.conf \
    && ldconfig

# エントリポイント（起動時に PRO 資材があれば上書き、なければ何もしない）
COPY docker/entrypoint.sh /usr/local/bin/hako-entry
RUN chmod +x /usr/local/bin/hako-entry

RUN pip3 install --no-cache-dir --break-system-packages optuna matplotlib
ENV PYTHONPATH="/root/workspace:${PYTHONPATH}"
ENTRYPOINT ["/usr/local/bin/hako-entry"]
CMD ["bash"]
