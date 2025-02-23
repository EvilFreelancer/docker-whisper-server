ARG UBUNTU_VERSION=22.04
ARG CUDA_VERSION=12.6.1
ARG BASE_CUDA_DEVEL_CONTAINER=nvidia/cuda:${CUDA_VERSION}-devel-ubuntu${UBUNTU_VERSION}
ARG BASE_CUDA_RUNTIME_CONTAINER=nvidia/cuda:${CUDA_VERSION}-runtime-ubuntu${UBUNTU_VERSION}

FROM ${BASE_CUDA_DEVEL_CONTAINER} AS builder
WORKDIR /app

# Anti-"sanction" fix
RUN set -xe \
 && sed -r 's#developer.download.nvidia.com#mirror.yandex.ru/mirrors/developer.download.nvidia.com#g' -i /etc/apt/sources.list.d/cuda-*.list

# Install dependencies
RUN set -xe \
 && apt update -q \
 && apt install -fyq bash wget ffmpeg git make cmake vim g++ \
 && apt clean

# Repo with sources
ARG WHISPER_REPO="https://github.com/ggerganov/whisper.cpp.git"

# It may be name of branch, tag or commit hash
ARG WHISPER_VERSION="master"

# Clone whisper.cpp repo
RUN set -xe \
 && git clone "$WHISPER_REPO" whisper.cpp
WORKDIR /app/whisper.cpp
RUN set -xe \
 && git checkout "$WHISPER_VERSION" \
 && rm -rf .git

# Build some whisper.cpp tools
WORKDIR /app/whisper.cpp
RUN ln -s /usr/local/cuda/lib64/stubs/libcuda.so /usr/local/cuda/lib64/stubs/libcuda.so.1
RUN set -xe \
 && export LD_LIBRARY_PATH=/usr/local/cuda/lib64/stubs/:$LD_LIBRARY_PATH \
 && cmake -B build -DGGML_CUDA=ON \
 && cmake --build build --config Release -v -j$(nproc)


FROM ${BASE_CUDA_RUNTIME_CONTAINER} AS runtime
WORKDIR /app

# Anti-"sanction" fix
RUN set -xe \
 && sed -r 's#developer.download.nvidia.com#mirror.yandex.ru/mirrors/developer.download.nvidia.com#g' -i /etc/apt/sources.list.d/cuda-*.list

# Install basic dependencies
RUN set -xe \
 && apt update -q \
 && apt install -fyq bash wget ffmpeg \
 && apt clean

# Create folders
RUN set -xe \
 && mkdir -pv /app/models /app/audios

# Copy compiled tools
COPY --from=builder /app/whisper.cpp/models/download-ggml-model.sh .
COPY --from=builder /app/whisper.cpp/build/src/*.so /usr/lib/x86_64-linux-gnu
COPY --from=builder /app/whisper.cpp/build/src/*.so.* /usr/lib/x86_64-linux-gnu
COPY --from=builder /app/whisper.cpp/build/ggml/src/*.so /usr/lib/x86_64-linux-gnu
COPY --from=builder /app/whisper.cpp/build/ggml/src/ggml-cuda/*.so /usr/lib/x86_64-linux-gnu
COPY --from=builder /app/whisper.cpp/build/bin/whisper-bench .
COPY --from=builder /app/whisper.cpp/build/bin/whisper-server .
COPY --from=builder /app/whisper.cpp/build/bin/whisper-cli .
COPY --from=builder /app/whisper.cpp/build/bin/quantize .

# Init entrypoint
ADD entrypoint.sh .
ENTRYPOINT ["/app/entrypoint.sh"]
