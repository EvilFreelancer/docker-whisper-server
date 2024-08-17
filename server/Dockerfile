FROM ubuntu:22.04
WORKDIR /app

# Install basic dependencies
RUN set -xe \
 && apt update -q \
 && apt install -fyq python3 python3-pip

# Install deps
COPY requirements.txt .
RUN set -xe \
 && pip install -r requirements.txt

# Copy sources
COPY . .

ENTRYPOINT ["/app/entrypoint.sh"]
