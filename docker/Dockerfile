FROM ubuntu:24.04 AS hakoniwa-drone-core

ARG DEBIAN_FRONTEND=noninteractive
ARG HAKO_PDU_ENDPOINT_REPO="https://github.com/hakoniwalab/hakoniwa-pdu-endpoint.git"
ARG HAKO_PDU_ENDPOINT_REF="main"
ARG HAKO_PDU_BRIDGE_CORE_REPO="https://github.com/hakoniwalab/hakoniwa-pdu-bridge-core.git"
ARG HAKO_PDU_BRIDGE_CORE_REF="main"
ARG HAKO_THREEJS_DRONE_REPO="https://github.com/hakoniwalab/hakoniwa-threejs-drone.git"
ARG CMAKE_BUILD_JOBS=4

ENV PATH="/usr/local/bin/hakoniwa:${PATH}" \
    HAKO_BINARY_PATH="/usr/share/hakoniwa/offset" \
    HAKO_PRO_PACKAGE="/opt/pro/lnx.zip" \
    HAKO_PRO_DIR="/opt/pro/lnx"

# 基本パッケージ（--no-install-recommends で軽量化）
RUN apt-get update && apt-get install -y --no-install-recommends \
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

# hakoniwa-core（OSS）
WORKDIR /root
RUN echo "deb [trusted=yes] https://hakoniwalab.github.io/apt stable main" \
 | tee /etc/apt/sources.list.d/hakoniwa.list \
 && apt-get update && apt-get install -y --no-install-recommends hakoniwa-core-full \
 && rm -rf /var/lib/apt/lists/*

# hakoniwa-pdu-endpoint（bridge-core 依存）
RUN git clone --depth 1 --branch "${HAKO_PDU_ENDPOINT_REF}" "${HAKO_PDU_ENDPOINT_REPO}" /tmp/hakoniwa-pdu-endpoint \
 && cmake -S /tmp/hakoniwa-pdu-endpoint -B /tmp/hakoniwa-pdu-endpoint/build -DCMAKE_BUILD_TYPE=Release \
 && cmake --build /tmp/hakoniwa-pdu-endpoint/build -j"${CMAKE_BUILD_JOBS}" \
 && cmake --install /tmp/hakoniwa-pdu-endpoint/build --prefix /usr/local/hakoniwa \
 && rm -rf /tmp/hakoniwa-pdu-endpoint

# hakoniwa-pdu-bridge-core（web bridge バイナリ）
RUN git clone --depth 1 --branch "${HAKO_PDU_BRIDGE_CORE_REF}" "${HAKO_PDU_BRIDGE_CORE_REPO}" /tmp/hakoniwa-pdu-bridge-core \
 && cmake -S /tmp/hakoniwa-pdu-bridge-core -B /tmp/hakoniwa-pdu-bridge-core/build \
      -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_CXX_FLAGS="-I/usr/include/hakoniwa" \
      -DBUILD_TESTING=OFF \
      -DHAKO_PDU_ENDPOINT_PREFIX=/usr/local/hakoniwa \
      -DCMAKE_INSTALL_PREFIX=/usr/local/hakoniwa \
 && cmake --build /tmp/hakoniwa-pdu-bridge-core/build \
      --target hakoniwa-pdu-bridge hakoniwa-pdu-web-bridge hakoniwa-pdu-bridge-monitor \
      -j"${CMAKE_BUILD_JOBS}" \
 && cmake --install /tmp/hakoniwa-pdu-bridge-core/build --prefix /usr/local/hakoniwa \
 && install -d /usr/local/hakoniwa/share/hakoniwa-pdu-bridge/config \
 && cp -R /tmp/hakoniwa-pdu-bridge-core/config/web_bridge_fleets \
      /usr/local/hakoniwa/share/hakoniwa-pdu-bridge/config/ \
 && rm -rf /tmp/hakoniwa-pdu-bridge-core

# threejs viewer（fleets web 配信用）
RUN git clone --recursive "${HAKO_THREEJS_DRONE_REPO}" /opt/hakoniwa-threejs-drone

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

ENTRYPOINT ["/usr/local/bin/hako-entry"]
CMD ["bash"]
