FROM python:3.14-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install --only-upgrade -y \
        libssl3t64 \
        openssl \
        openssl-provider-legacy && \
    rm -rf /var/lib/apt/lists/*

COPY . /app

RUN python -m pip install --no-cache-dir --upgrade \
    pip \
    "setuptools>=78.1.1" \
    "wheel>=0.46.2" && \
    python -m pip install --no-cache-dir .

ENTRYPOINT ["mtr2mqtt"]