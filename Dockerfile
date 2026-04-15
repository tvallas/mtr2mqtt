FROM python:3.10-slim

ARG VERSION

RUN python -m pip install --no-cache-dir --upgrade \
    pip \
    setuptools>=78.1.1 \
    wheel>=0.46.2 && \
    python -m pip install --no-cache-dir "mtr2mqtt==$VERSION"

RUN apt-get update && apt-get upgrade -y perl-base && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["mtr2mqtt"]