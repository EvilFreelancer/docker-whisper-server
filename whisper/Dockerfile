ARG UBUNTU_VERSION=22.04
ARG CUDA_VERSION=12.6.1
ARG BASE_CUDA_DEV_CONTAINER=nvidia/cuda:${CUDA_VERSION}-devel-ubuntu${UBUNTU_VERSION}
ARG BASE_CUDA_RUNTIME_CONTAINER=nvidia/cuda:${CUDA_VERSION}-runtime-ubuntu${UBUNTU_VERSION}

FROM ${BASE_CUDA_DEV_CONTAINER} as builder
WORKDIR /app

# Repo with sources
ARG WHISPER_REPO="https://github.com/ggerganov/whisper.cpp.git"

# It may be name of branch, tag or commit hash
#ARG WHISPER_VERSION="v1.6.3"  # TODO: When it will be released
ARG WHISPER_VERSION="master"

# Unless otherwise specified, we make a fat build.
ARG CUDA_DOCKER_ARCH=all
# Set nvcc architecture
ENV CUDA_DOCKER_ARCH=${CUDA_DOCKER_ARCH}

# Enable cuBLAS
ARG GGML_CUDA=1
# Set cuBLAS
ENV GGML_CUDA=${GGML_CUDA}

# To get latest tag use this:
# git -c 'versionsort.suffix=-' ls-remote --tags --sort='v:refname' \
#    "https://github.com/ggerganov/whisper.cpp.git" '*.*.*' | \
#    tail --lines=1 | cut --delimiter='/' --fields=3
# For details see here: https://stackoverflow.com/questions/8932389/git-shallow-clone-to-specific-tag)

# Install dependencies
RUN set -xe \
 && apt update -q \
 && apt install -fyq bash wget ffmpeg git make vim g++

# Clone whisper.cpp repo
RUN set -xe \
 && git clone --branch "$WHISPER_VERSION" --depth 1 "$WHISPER_REPO"

# Build some whisper.cpp tools
WORKDIR /app/whisper.cpp
RUN make clean \
 && make -j$(nproc) server quantize


FROM ${BASE_CUDA_RUNTIME_CONTAINER}
WORKDIR /app

# Install basic dependencies
RUN set -xe \
 && apt update -q \
 && apt install -fyq bash wget ffmpeg

# Create folders
RUN set -xe \
 && mkdir -pv /app/models /app/audios

# Copy compiled tools
COPY --from=builder /app/whisper.cpp/models/download-ggml-model.sh .
COPY --from=builder /app/whisper.cpp/server .
COPY --from=builder /app/whisper.cpp/quantize .

# Init entrypoint
ADD entrypoint.sh .
ENTRYPOINT ["/app/entrypoint.sh"]
