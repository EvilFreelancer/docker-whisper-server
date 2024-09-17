FROM nvidia/cuda:12.5.1-devel-ubuntu22.04 AS builder
WORKDIR /app

ARG WHISPER_REPO="https://github.com/ggerganov/whisper.cpp.git"
# It may be name of branch, tag or commit hash
#ARG WHISPER_VERSION="v1.6.3"  # TODO: When it will be released
ARG WHISPER_VERSION="master"

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
 && WHISPER_CUBLAS=1 GGML_CUDA=1 make -j$(nproc) server quantize


FROM nvidia/cuda:12.5.1-runtime-ubuntu22.04
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
