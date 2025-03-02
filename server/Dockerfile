FROM ubuntu:22.04
WORKDIR /app

# Install basic dependencies
RUN set -xe \
 && apt update -q \
 && apt install -fyq python3 python3-pip \
 && apt clean

# Install deps
COPY requirements.txt .
RUN set -xe \
 && pip install --no-cache -r requirements.txt

# Copy sources
COPY . .
RUN chmod +x /app/entrypoint.sh


# Для реального определения нагрузки на GPU нужно раскоментировать соответствующий блок, иначе будет просто случайное число от 0 до 100
# Установка intel_gpu_top для видеокарт Intel
# RUN set -xe \
#  && apt install -fyq intel-gpu-tools

# Установка rocm-smi для видеокарт AMD
# RUN set -xe \
#  && apt install -fyq wget \
#  && wget https://repo.radeon.com/amdgpu-install/6.0.2/ubuntu/jammy/amdgpu-install_6.0.60002-1_all.deb \
#  && apt install -fyq ./amdgpu-install_6.0.60002-1_all.deb \
#  && amdgpu-install --usecase=rocm


ENTRYPOINT ["/app/entrypoint.sh"]
