FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN python -m pip install --no-cache-dir --upgrade \
    pip \
    "setuptools>=78.1.1" \
    "wheel>=0.46.2" && \
    python -m pip install --no-cache-dir .

ENTRYPOINT ["mtr2mqtt"]